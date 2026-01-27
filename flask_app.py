# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
import sqlite3
import json
import re
import os
from werkzeug.utils import secure_filename
import uuid
import subprocess
from datetime import datetime, timedelta
import zipfile
import io
import shutil
from pathlib import Path

# --- パス設定 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'notion.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'templates')
STATIC_FOLDER = os.path.join(BASE_DIR, 'static')

app = Flask(__name__, template_folder=TEMPLATE_FOLDER, static_folder=STATIC_FOLDER)

# アップロード設定
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'webp', 'zip', 'docx'}

# --- データベース設定 ---
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT DEFAULT '',
        icon TEXT DEFAULT '📄',
        cover_image TEXT DEFAULT '', 
        parent_id INTEGER,
        position REAL DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (parent_id) REFERENCES pages(id) ON DELETE CASCADE
    )
    ''')
    try:
        cursor.execute("ALTER TABLE pages ADD COLUMN cover_image TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    
    # 新機能用カラム追加
    try:
        cursor.execute("ALTER TABLE pages ADD COLUMN is_pinned BOOLEAN DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    
    try:
        cursor.execute("ALTER TABLE pages ADD COLUMN is_deleted BOOLEAN DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    
    # ブロック用の折りたたみカラム
    try:
        cursor.execute("ALTER TABLE blocks ADD COLUMN collapsed BOOLEAN DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    
    # トグルブロック用の詳細内容カラム
    try:
        cursor.execute("ALTER TABLE blocks ADD COLUMN details TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    
    # position を REAL に変更（既存インデックスの衝突を防ぐ）
    try:
        cursor.execute("ALTER TABLE pages ADD COLUMN position_new REAL DEFAULT 0.0")
        cursor.execute("UPDATE pages SET position_new = CAST(position AS REAL) * 1000.0")
        cursor.execute("ALTER TABLE pages DROP COLUMN position")
        cursor.execute("ALTER TABLE pages RENAME COLUMN position_new TO position")
    except sqlite3.OperationalError:
        pass
    
    # props JSON カラムをブロックに追加
    try:
        cursor.execute("ALTER TABLE blocks ADD COLUMN props TEXT DEFAULT '{}'")
    except sqlite3.OperationalError:
        pass
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS blocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        page_id INTEGER NOT NULL,
        type TEXT DEFAULT 'text',
        content TEXT DEFAULT '',
        checked BOOLEAN DEFAULT 0,
        position REAL DEFAULT 0.0,
        collapsed BOOLEAN DEFAULT 0,
        details TEXT DEFAULT '',
        props TEXT DEFAULT '{}',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (page_id) REFERENCES pages(id) ON DELETE CASCADE
    )
    ''')
    cursor.execute('CREATE VIRTUAL TABLE IF NOT EXISTS blocks_fts USING fts5(title, content, content=blocks, content_rowid=id)')
    cursor.execute('CREATE TRIGGER IF NOT EXISTS blocks_ai AFTER INSERT ON blocks BEGIN INSERT INTO blocks_fts(rowid, title, content) VALUES (new.id, (SELECT title FROM pages WHERE id = new.page_id), new.content); END;')
    cursor.execute('CREATE TRIGGER IF NOT EXISTS blocks_ad AFTER DELETE ON blocks BEGIN INSERT INTO blocks_fts(blocks_fts, rowid, title, content) VALUES("delete", old.id, (SELECT title FROM pages WHERE id = old.page_id), old.content); END;')
    cursor.execute('CREATE TRIGGER IF NOT EXISTS blocks_au AFTER UPDATE ON blocks BEGIN INSERT INTO blocks_fts(blocks_fts, rowid, title, content) VALUES("delete", old.id, (SELECT title FROM pages WHERE id = old.page_id), old.content); INSERT INTO blocks_fts(rowid, title, content) VALUES (new.id, (SELECT title FROM pages WHERE id = new.page_id), new.content); END;')
    
    # テンプレート用テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        icon TEXT DEFAULT '📋',
        description TEXT DEFAULT '',
        content_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# --- カロリー計算の簡易データベース ---
# 値はおおよその目安。実際の食材・分量とは異なる可能性がある。
CALORIE_TABLE = [
    {'label': 'ご飯', 'keywords': ['ご飯', '白米', 'ライス'], 'kcal': 240, 'unit': '1杯(150g)'},
    {'label': '納豆', 'keywords': ['納豆'], 'kcal': 100, 'unit': '1パック'},
    {'label': 'パン', 'keywords': ['食パン', 'パン'], 'kcal': 180, 'unit': '1枚(6枚切)'},
    {'label': 'プロテイン', 'keywords': ['プロテイン'], 'kcal': 120, 'unit': '1杯(30g)'},
    {'label': '弁当', 'keywords': ['弁当'], 'kcal': 500, 'unit': '1個'},
    {'label': '卵', 'keywords': ['卵', 'たまご'], 'kcal': 80, 'unit': '1個'},
    {'label': '鶏むね肉', 'keywords': ['鶏むね', '鶏胸', 'ささみ'], 'kcal': 165, 'unit': '100g', 'per_grams': 100},
    {'label': '豚肉', 'keywords': ['豚肉'], 'kcal': 250, 'unit': '100g', 'per_grams': 100},
    {'label': '牛肉', 'keywords': ['牛肉'], 'kcal': 280, 'unit': '100g', 'per_grams': 100},
    {'label': '豆腐', 'keywords': ['豆腐'], 'kcal': 140, 'unit': '1丁(300g)', 'per_grams': 300},
    {'label': 'ヨーグルト', 'keywords': ['ヨーグルト'], 'kcal': 60, 'unit': '100g', 'per_grams': 100},
    {'label': 'バナナ', 'keywords': ['バナナ'], 'kcal': 90, 'unit': '1本'},
    {'label': 'そば', 'keywords': ['そば', '蕎麦'], 'kcal': 320, 'unit': '1人前'},
    {'label': 'うどん', 'keywords': ['うどん'], 'kcal': 280, 'unit': '1人前'},
    {'label': 'パスタ', 'keywords': ['パスタ', 'スパゲッティ'], 'kcal': 350, 'unit': '1人前'},
    {'label': '牛乳', 'keywords': ['牛乳', 'ミルク'], 'kcal': 130, 'unit': '200ml', 'per_ml': 200},
    {'label': 'サラダ', 'keywords': ['サラダ'], 'kcal': 80, 'unit': '1皿'},
    {'label': '汁物', 'keywords': ['汁', 'スープ', '味噌汁', 'みそ汁'], 'kcal': 80, 'unit': '1杯(180ml)', 'per_ml': 180},
]

DEFAULT_UNKNOWN_KCAL = 150  # 不明食材の暫定値


def _extract_number(text, pattern):
    match = re.search(pattern, text)
    return float(match.group(1)) if match else None


def _fallback_estimate(line):
    lowered = line.lower()
    if '汁' in line or 'スープ' in line:
        return {'label': '汁物(推定)', 'kcal': 80, 'is_estimated': True}
    if 'カレー' in line:
        return {'label': 'カレー(推定)', 'kcal': 500, 'is_estimated': True}
    if 'シチュー' in line:
        return {'label': 'シチュー(推定)', 'kcal': 350, 'is_estimated': True}
    if '煮込み' in line:
        return {'label': '煮込み(推定)', 'kcal': 300, 'is_estimated': True}
    if '炒め' in line or 'ソテー' in line:
        return {'label': '炒め物(推定)', 'kcal': 320, 'is_estimated': True}
    return {'label': '不明(推定)', 'kcal': DEFAULT_UNKNOWN_KCAL, 'is_estimated': True}


def estimate_calories(lines):
    """行ごとのメニュー文字列から概算カロリーを計算"""
    results = []
    total_kcal = 0.0

    for raw in lines:
        line = (raw or '').strip()
        if not line:
            continue

        matched_entry = None
        for entry in CALORIE_TABLE:
            if any(keyword in line for keyword in entry['keywords']):
                matched_entry = entry
                break

        amount = _extract_number(line, r'(\d+(?:\.\d+)?)') or 1.0
        gram_val = _extract_number(line, r'(\d+(?:\.\d+)?)\s*(?:g|グラム)')
        ml_val = _extract_number(line, r'(\d+(?:\.\d+)?)\s*(?:ml|mL|ML|㎖)')

        if matched_entry:
            kcal = matched_entry['kcal']
            unit = matched_entry.get('unit', '1食')

            if matched_entry.get('per_grams'):
                grams = gram_val if gram_val is not None else matched_entry['per_grams'] * amount
                kcal_total = (grams / matched_entry['per_grams']) * matched_entry['kcal']
                amount_label = f"{grams:.0f}g"
            elif matched_entry.get('per_ml'):
                ml = ml_val if ml_val is not None else matched_entry['per_ml'] * amount
                kcal_total = (ml / matched_entry['per_ml']) * matched_entry['kcal']
                amount_label = f"{ml:.0f}ml"
            else:
                kcal_total = amount * kcal
                amount_label = f"{amount:.1f}食" if amount != 1 else '1食'

            kcal_total = round(kcal_total, 1)
            total_kcal += kcal_total
            results.append({
                'input': line,
                'matched': matched_entry['label'],
                'unit': unit,
                'amount': amount_label,
                'kcal': kcal_total,
                'is_estimated': False
            })
        else:
            fallback = _fallback_estimate(line)
            kcal_total = round(fallback['kcal'], 1)
            total_kcal += kcal_total
            results.append({
                'input': line,
                'matched': fallback['label'],
                'unit': '推定',
                'amount': '-',
                'kcal': kcal_total,
                'is_estimated': True
            })

    return {
        'total_kcal': round(total_kcal, 1),
        'items': results,
        'note': '目安の計算です。食材や調理法で変動します。'
    }


def get_or_create_inbox():
    """'あとで調べる'ページを取得、なければ作成"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM pages WHERE title = ? AND parent_id IS NULL LIMIT 1', ('🔖 あとで調べる',))
    inbox = cursor.fetchone()
    if not inbox:
        cursor.execute('SELECT MAX(position) FROM pages WHERE parent_id IS NULL')
        max_pos = cursor.fetchone()[0]
        new_pos = (max_pos if max_pos is not None else -1) + 1
        cursor.execute('INSERT INTO pages (title, icon, parent_id, position) VALUES (?, ?, ?, ?)',
                       ('🔖 あとで調べる', '🔖', None, new_pos))
        inbox_id = cursor.lastrowid
        cursor.execute("INSERT INTO blocks (page_id, type, content, position) VALUES (?, 'text', '', ?)",
                       (inbox_id, 1000.0))
        conn.commit()
        cursor.execute('SELECT * FROM pages WHERE id = ?', (inbox_id,))
        inbox = cursor.fetchone()
    conn.close()
    return dict(inbox) if inbox else None

def get_next_position(cursor, parent_id):
    """
    次のposition値を計算（1000刻み方式）
    """
    if parent_id:
        cursor.execute('SELECT MAX(position) FROM pages WHERE parent_id = ?', (parent_id,))
    else:
        cursor.execute('SELECT MAX(position) FROM pages WHERE parent_id IS NULL')
    max_pos = cursor.fetchone()[0]
    if max_pos is None:
        return 1000.0
    return max_pos + 1000.0


def get_block_next_position(cursor, page_id):
    """
    ブロックの次のposition値を計算
    """
    cursor.execute('SELECT MAX(position) FROM blocks WHERE page_id = ?', (page_id,))
    max_pos = cursor.fetchone()[0]
    if max_pos is None:
        return 1000.0
    return max_pos + 1000.0


# --- ユーティリティ ---
def mark_tree_deleted(cursor, page_id, is_deleted=True):
    """
    ページとその全子ページを再帰的に削除フラグ変更（soft delete）
    """
    cursor.execute('UPDATE pages SET is_deleted = ? WHERE id = ?', (1 if is_deleted else 0, page_id))
    cursor.execute('SELECT id FROM pages WHERE parent_id = ?', (page_id,))
    for row in cursor.fetchall():
        mark_tree_deleted(cursor, row['id'], is_deleted)


def hard_delete_tree(cursor, page_id):
    """
    ページとその全子ページを再帰的に完全削除（hard delete）
    """
    cursor.execute('SELECT id FROM pages WHERE parent_id = ?', (page_id,))
    for row in cursor.fetchall():
        hard_delete_tree(cursor, row['id'])
    cursor.execute('DELETE FROM pages WHERE id = ?', (page_id,))


def export_page_to_dict(cursor, page_id):
    """
    ページとその全ブロック・子ページを辞書に変換（エクスポート用）
    """
    cursor.execute('SELECT * FROM pages WHERE id = ?', (page_id,))
    page_row = cursor.fetchone()
    if not page_row:
        return None
    
    page = dict(page_row)
    cursor.execute('SELECT * FROM blocks WHERE page_id = ? ORDER BY position', (page_id,))
    page['blocks'] = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute('SELECT * FROM pages WHERE parent_id = ? ORDER BY position', (page_id,))
    page['children'] = [export_page_to_dict(cursor, row['id']) for row in cursor.fetchall()]
    
    return page


def page_to_markdown(page, level=1):
    """
    ページをMarkdownフォーマットに変換（再帰的）
    """
    lines = []
    
    # ページタイトルを見出しで表現
    heading = '#' * level
    lines.append(f"{heading} {page.get('icon', '📄')} {page.get('title', '無題')}")
    lines.append('')
    
    # ブロックをMarkdownに変換
    for block in page.get('blocks', []):
        block_type = block.get('type', 'text')
        content = block.get('content', '')
        
        if block_type == 'h1':
            lines.append(f"### {content}")
            lines.append('')
        elif block_type == 'todo':
            checked = '✓' if block.get('checked') else '☐'
            lines.append(f"- [{checked}] {content}")
        elif block_type == 'toggle':
            lines.append(f"**{content}**")
            details = block.get('details', '')
            if details:
                lines.append(details)
            lines.append('')
        elif block_type == 'image':
            lines.append(f"![Image]({content})")
            lines.append('')
        else:  # text
            if content:
                lines.append(content)
                lines.append('')
    
    # 子ページを再帰的に変換
    for child in page.get('children', []):
        lines.append(page_to_markdown(child, level + 1))
        lines.append('')
    
    return '\n'.join(lines)


def create_page_from_dict(cursor, page_dict, parent_id=None, position=None):
    """
    辞書からページを作成（インポート用）
    """
    parent_id = parent_id if parent_id is not None else page_dict.get('parent_id')
    
    if position is None:
        position = get_next_position(cursor, parent_id)
    
    cursor.execute(
        'INSERT INTO pages (title, icon, cover_image, parent_id, position, is_pinned, is_deleted) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (
            page_dict.get('title', ''),
            page_dict.get('icon', '📄'),
            page_dict.get('cover_image', ''),
            parent_id,
            position,
            page_dict.get('is_pinned', 0),
            0
        )
    )
    new_page_id = cursor.lastrowid
    
    # ブロック追加
    for block in page_dict.get('blocks', []):
        cursor.execute(
            'INSERT INTO blocks (page_id, type, content, checked, position, collapsed, details) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (
                new_page_id,
                block.get('type', 'text'),
                block.get('content', ''),
                block.get('checked', 0),
                block.get('position', 1000.0) if isinstance(block.get('position'), int) else block.get('position', 1000.0),
                block.get('collapsed', 0),
                block.get('details', ''),
                block.get('props', '{}')
            )
        )
    
    # 子ページ追加
    for i, child in enumerate(page_dict.get('children', [])):
        child_pos = (i + 1) * 1000.0
        create_page_from_dict(cursor, child, parent_id=new_page_id, position=child_pos)
    
    return new_page_id


def copy_page_tree(cursor, source_page_id, new_title=None, new_parent_id=None, position=None, override_icon=None):
    """
    source_page_id を起点にページとブロックを再帰コピーする。
    new_title/new_parent_id/position/override_icon はルートページの上書き用。
    """
    cursor.execute('SELECT * FROM pages WHERE id = ?', (source_page_id,))
    source_page = cursor.fetchone()
    if not source_page:
        return None

    src = dict(source_page)
    parent_id = new_parent_id if new_parent_id is not None else src['parent_id']
    # 位置は指定がなければ末尾に追加
    if position is None:
        position = get_next_position(cursor, parent_id)

    cursor.execute(
        'INSERT INTO pages (title, icon, cover_image, parent_id, position, is_pinned, is_deleted) VALUES (?, ?, ?, ?, ?, ?, 0)',
        (
            new_title if new_title is not None else src.get('title', ''),
            override_icon if override_icon is not None else src.get('icon', '📄'),
            src.get('cover_image', ''),
            parent_id,
            position,
            src.get('is_pinned', 0)
        )
    )
    new_page_id = cursor.lastrowid

    # ブロックコピー
    cursor.execute('SELECT * FROM blocks WHERE page_id = ? ORDER BY position', (source_page_id,))
    for block in cursor.fetchall():
        block_dict = dict(block)
        cursor.execute(
            'INSERT INTO blocks (page_id, type, content, checked, position, collapsed, details) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (
                new_page_id,
                block_dict.get('type', 'text'),
                block_dict.get('content', ''),
                block_dict.get('checked', 0),
                block_dict.get('position', 0),
                block_dict.get('collapsed', 0),
                block_dict.get('details', '')
            )
        )

    # 子ページを再帰コピー
    cursor.execute('SELECT * FROM pages WHERE parent_id = ? ORDER BY position', (source_page_id,))
    for child in cursor.fetchall():
        copy_page_tree(
            cursor,
            child['id'],
            new_parent_id=new_page_id,
            position=child['position']
        )

    return new_page_id

# --- ルーティング ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inbox')
def inbox_page():
    """あとで調べるページへのショートカットURL"""
    inbox = get_or_create_inbox()
    if inbox:
        return render_template('index.html', inbox_id=inbox['id'])
    return render_template('index.html')

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/api/inbox', methods=['GET'])
def get_inbox():
    """'あとで調べる'ページを取得"""
    inbox = get_or_create_inbox()
    return jsonify(inbox if inbox else {'error': 'Failed to create inbox'}), 200 if inbox else 500

@app.route('/api/pages', methods=['GET'])
def get_pages():
    conn = get_db()
    cursor = conn.cursor()
    # ゴミ箱除外、ピン留めを優先
    cursor.execute('SELECT * FROM pages WHERE is_deleted = 0 ORDER BY is_pinned DESC, position ASC, created_at ASC')
    all_pages = [dict(row) for row in cursor.fetchall()]
    conn.close()
    page_map = {page['id']: {**page, 'children': []} for page in all_pages}
    roots = []
    for page in all_pages:
        if page['parent_id'] and page['parent_id'] in page_map:
            page_map[page['parent_id']]['children'].append(page_map[page['id']])
        else:
            roots.append(page_map[page['id']])
    return jsonify(roots)

@app.route('/api/trash', methods=['GET'])
def get_trash():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM pages WHERE is_deleted = 1 ORDER BY updated_at DESC')
    trash_pages = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(trash_pages)

@app.route('/api/today-highlights/<int:page_id>', methods=['GET'])
def get_today_highlights(page_id):
    """指定ページ内で今日作成されたブロックを取得"""
    conn = get_db()
    cursor = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT * FROM blocks 
        WHERE page_id = ? AND DATE(created_at) = ?
        ORDER BY created_at DESC
        LIMIT 10
    ''', (page_id, today))
    highlights = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(highlights)

@app.route('/api/pages', methods=['POST'])
def create_page():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    parent_id = data.get('parent_id')
    new_pos = get_next_position(cursor, parent_id)
    cursor.execute('INSERT INTO pages (title, icon, parent_id, position) VALUES (?, ?, ?, ?)',
                   (data.get('title', ''), data.get('icon', '📄'), parent_id, new_pos))
    page_id = cursor.lastrowid
    cursor.execute("INSERT INTO blocks (page_id, type, content, position) VALUES (?, 'text', '', ?)", (page_id, get_block_next_position(cursor, page_id)))
    conn.commit()
    cursor.execute('SELECT * FROM pages WHERE id = ?', (page_id,))
    page = dict(cursor.fetchone())
    conn.close()
    return jsonify(page)

    # 必要な子ページ（定型）を不足していれば補完するヘルパー
    def ensure_daily_children(parent_page_id):
        required = [
            ('日記', '📝'),
            ('筋トレ', '🏋️'),
            ('英語学習', '🌍'),
            ('食事', '🍽️'),
        ]
        cursor.execute('SELECT title FROM pages WHERE parent_id = ? AND is_deleted = 0', (parent_page_id,))
        existing_titles = {row['title'] for row in cursor.fetchall()}
        next_pos = get_next_position(cursor, parent_page_id)
        for title_req, icon_req in required:
            if title_req in existing_titles:
                continue
            cursor.execute(
                'INSERT INTO pages (title, icon, parent_id, position) VALUES (?, ?, ?, ?)',
                (title_req, icon_req, parent_page_id, next_pos)
            )
            child_id = cursor.lastrowid
            next_pos += 1000.0
            if title_req == '日記':
                blocks = [
                    {'type': 'h1', 'content': '体調'},
                    {'type': 'text', 'content': ''},
                    {'type': 'h1', 'content': '天気'},
                    {'type': 'text', 'content': ''},
                    {'type': 'h1', 'content': 'やったこと'},
                    {'type': 'todo', 'content': ''},
                    {'type': 'h1', 'content': '振り返り'},
                    {'type': 'text', 'content': ''},
                ]
            elif title_req == '筋トレ':
                blocks = [
                    {'type': 'h1', 'content': '今日のメニュー'},
                    {'type': 'todo', 'content': ''},
                    {'type': 'h1', 'content': 'セット・回数'},
                    {'type': 'text', 'content': ''},
                    {'type': 'h1', 'content': 'メモ'},
                    {'type': 'text', 'content': ''},
                ]
            elif title_req == '英語学習':
                blocks = [
                    {'type': 'h1', 'content': '今日の学習内容'},
                    {'type': 'text', 'content': ''},
                    {'type': 'h1', 'content': '新しい単語'},
                    {'type': 'todo', 'content': ''},
                    {'type': 'h1', 'content': '発音練習'},
                    {'type': 'text', 'content': ''},
                    {'type': 'h1', 'content': 'リスニング時間'},
                    {'type': 'text', 'content': ''},
                    {'type': 'h1', 'content': '気づいたこと'},
                    {'type': 'text', 'content': ''},
                ]
            else:  # 食事
                blocks = [
                    {'type': 'h1', 'content': '今日の食事メモ'},
                    {'type': 'text', 'content': ''},
                    {'type': 'h1', 'content': 'カロリー記録'},
                    {'type': 'calorie', 'content': ''},
                ]
            for idx, block in enumerate(blocks):
                cursor.execute(
                    "INSERT INTO blocks (page_id, type, content, checked, position, props) VALUES (?, ?, ?, ?, ?, ?)",
                    (child_id, block['type'], block.get('content', ''), block.get('checked', 0), (idx + 1) * 1000.0, '{}')
                )

    # 同じタイトルのページがあれば再利用し、不足子ページを補完

    # 日付形式を日本語タイトルに変換 (例: 2026-01-24 -> 2026年1月24日)
    target_date = None
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d')
        title = f"{target_date.year}年{target_date.month}月{target_date.day}日"
    except Exception:
        title = date_str

    conn = get_db()
    cursor = conn.cursor()

    # 同じタイトルのページがあれば再利用
    cursor.execute('SELECT * FROM pages WHERE title = ? AND is_deleted = 0 LIMIT 1', (title,))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        return jsonify(dict(existing))

    # 前日ページがあればコピー
    previous_page_id = None
    if target_date:
        prev_date = target_date - timedelta(days=1)
        prev_title = f"{prev_date.year}年{prev_date.month}月{prev_date.day}日"
        cursor.execute('SELECT id FROM pages WHERE title = ? AND is_deleted = 0 ORDER BY created_at DESC LIMIT 1', (prev_title,))
        prev_row = cursor.fetchone()
        if prev_row:
            previous_page_id = prev_row['id']

    if previous_page_id:
        new_page_id = copy_page_tree(cursor, previous_page_id, new_title=title, new_parent_id=None, override_icon='📅')
        conn.commit()
        cursor.execute('SELECT * FROM pages WHERE id = ?', (new_page_id,))
        page = dict(cursor.fetchone())
        ensure_daily_children(page['id'])
        conn.commit()
        conn.close()
        return jsonify(page)
    
    # 親なし(ルート)で作成
    new_pos = get_next_position(cursor, None)
    
    cursor.execute('INSERT INTO pages (title, icon, parent_id, position) VALUES (?, ?, ?, ?)',
                   (title, '📅', None, new_pos))
    page_id = cursor.lastrowid

    # 親ページにデフォルトのテキストブロック
    cursor.execute("INSERT INTO blocks (page_id, type, content, position, props) VALUES (?, 'text', '', ?, ?)", (page_id, 1000.0, '{}'))

    # 子ページ（ツリー）を自動生成: 日記 / 筋トレ / 英語学習
    children_templates = [
        {
            'title': '日記',
            'icon': '📝',
            'blocks': [
                {'type': 'h1', 'content': '体調'},
                {'type': 'text', 'content': ''},
                {'type': 'h1', 'content': '天気'},
                {'type': 'text', 'content': ''},
                {'type': 'h1', 'content': 'やったこと'},
                {'type': 'todo', 'content': ''},
                {'type': 'h1', 'content': '振り返り'},
                {'type': 'text', 'content': ''},
            ]
        },
        {
            'title': '筋トレ',
            'icon': '🏋️',
            'blocks': [
                {'type': 'h1', 'content': '今日のメニュー'},
                {'type': 'todo', 'content': ''},
                {'type': 'h1', 'content': 'セット・回数'},
                {'type': 'text', 'content': ''},
                {'type': 'h1', 'content': 'メモ'},
                {'type': 'text', 'content': ''},
            ]
        },
        {
            'title': '英語学習',
            'icon': '🌍',
            'blocks': [
                {'type': 'h1', 'content': '今日の学習内容'},
                {'type': 'text', 'content': ''},
                {'type': 'h1', 'content': '新しい単語'},
                {'type': 'todo', 'content': ''},
                {'type': 'h1', 'content': '発音練習'},
                {'type': 'text', 'content': ''},
                {'type': 'h1', 'content': 'リスニング時間'},
                {'type': 'text', 'content': ''},
                {'type': 'h1', 'content': '気づいたこと'},
                {'type': 'text', 'content': ''},
            ]
        },
        {
            'title': '食事',
            'icon': '🍽️',
            'blocks': [
                {'type': 'h1', 'content': '今日の食事メモ'},
                {'type': 'text', 'content': ''},
                {'type': 'h1', 'content': 'カロリー記録'},
                {'type': 'calorie', 'content': ''},
            ]
        }
    ]

    for i, child in enumerate(children_templates):
        # 子ページの並び順は1000, 2000, 3000...
        cursor.execute('INSERT INTO pages (title, icon, parent_id, position) VALUES (?, ?, ?, ?)',
                       (child['title'], child['icon'], page_id, (i + 1) * 1000.0))
        child_id = cursor.lastrowid
        # 子ページのブロック追加
        for j, block in enumerate(child['blocks']):
            cursor.execute(
                "INSERT INTO blocks (page_id, type, content, checked, position, props) VALUES (?, ?, ?, ?, ?, ?)",
                (child_id, block['type'], block.get('content', ''), block.get('checked', 0), (j + 1) * 1000.0, '{}')
            )

    conn.commit()
    cursor.execute('SELECT * FROM pages WHERE id = ?', (page_id,))
    page = dict(cursor.fetchone())
    conn.close()
    return jsonify(page)

@app.route('/api/folders', methods=['POST'])
def create_folder():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    parent_id = data.get('parent_id')
    new_pos = get_next_position(cursor, parent_id)
    cursor.execute('INSERT INTO pages (title, icon, parent_id, position) VALUES (?, ?, ?, ?)',
                   (data.get('title', '新しいフォルダ'), '📁', parent_id, new_pos))
    folder_id = cursor.lastrowid
    conn.commit()
    cursor.execute('SELECT * FROM pages WHERE id = ?', (folder_id,))
    folder = dict(cursor.fetchone())
    conn.close()
    return jsonify(folder)

@app.route('/api/pages/from-template', methods=['POST'])
def create_page_from_template():
    data = request.json
    template_type = data.get('template')
    
    conn = get_db()
    cursor = conn.cursor()
    
    # テンプレート定義
    templates = {
        'daily': {
            'title': f'{datetime.now().strftime("%Y年%m月%d日")}の記録',
            'icon': '📝',
            'blocks': [
                {'type': 'h1', 'content': '体調'},
                {'type': 'text', 'content': ''},
                {'type': 'h1', 'content': '天気'},
                {'type': 'text', 'content': ''},
                {'type': 'h1', 'content': 'やったこと'},
                {'type': 'todo', 'content': ''},
                {'type': 'h1', 'content': '振り返り'},
                {'type': 'text', 'content': ''},
            ]
        },
        'reading': {
            'title': '読書メモ',
            'icon': '📚',
            'blocks': [
                {'type': 'h1', 'content': '本のタイトル'},
                {'type': 'text', 'content': ''},
                {'type': 'h1', 'content': '著者'},
                {'type': 'text', 'content': ''},
                {'type': 'h1', 'content': '読んだ日'},
                {'type': 'text', 'content': ''},
                {'type': 'h1', 'content': '感想・メモ'},
                {'type': 'text', 'content': ''},
            ]
        },
        'meeting': {
            'title': '会議メモ',
            'icon': '💼',
            'blocks': [
                {'type': 'h1', 'content': '日時'},
                {'type': 'text', 'content': ''},
                {'type': 'h1', 'content': '参加者'},
                {'type': 'text', 'content': ''},
                {'type': 'h1', 'content': '議題'},
                {'type': 'text', 'content': ''},
                {'type': 'h1', 'content': '決定事項'},
                {'type': 'todo', 'content': ''},
            ]
        },
        'english': {
            'title': f'{datetime.now().strftime("%Y年%m月%d日")}の英語進捗',
            'icon': '🌍',
            'blocks': [
                {'type': 'h1', 'content': '今日の学習内容'},
                {'type': 'text', 'content': ''},
                {'type': 'h1', 'content': '新しい単語'},
                {'type': 'todo', 'content': ''},
                {'type': 'h1', 'content': '発音練習'},
                {'type': 'text', 'content': ''},
                {'type': 'h1', 'content': 'リスニング時間'},
                {'type': 'text', 'content': ''},
                {'type': 'h1', 'content': '気づいたこと'},
                {'type': 'text', 'content': ''},
            ]
        }
    }
    
    template = templates.get(template_type, templates['daily'])
    
    new_pos = get_next_position(cursor, None)
    
    cursor.execute('INSERT INTO pages (title, icon, parent_id, position) VALUES (?, ?, ?, ?)',
                   (template['title'], template['icon'], None, new_pos))
    page_id = cursor.lastrowid
    
    # ブロックを追加
    for i, block in enumerate(template['blocks']):
        cursor.execute(
            "INSERT INTO blocks (page_id, type, content, checked, position, props) VALUES (?, ?, ?, ?, ?, ?)",
            (page_id, block['type'], block['content'], block.get('checked', 0), (i + 1) * 1000.0, '{}')
        )
    
    conn.commit()
    cursor.execute('SELECT * FROM pages WHERE id = ?', (page_id,))
    page = dict(cursor.fetchone())
    conn.close()
    return jsonify(page)

@app.route('/api/pages/<int:page_id>', methods=['GET'])
def get_page(page_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM pages WHERE id = ?', (page_id,))
    page_row = cursor.fetchone()
    if not page_row:
        conn.close()
        return jsonify({'error': 'Page not found'}), 404
    page = dict(page_row)
    cursor.execute('SELECT * FROM blocks WHERE page_id = ? ORDER BY position', (page_id,))
    page['blocks'] = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(page)

@app.route('/api/pages/<int:page_id>', methods=['PUT'])
def update_page(page_id):
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    updates = []
    values = []
    fields = ['title', 'icon', 'parent_id', 'cover_image', 'is_pinned', 'is_deleted', 'position']
    for field in fields:
        if field in data:
            updates.append(f'{field} = ?')
            values.append(data[field])
    if updates:
        updates.append('updated_at = CURRENT_TIMESTAMP')
        values.append(page_id)
        cursor.execute(f'UPDATE pages SET {", ".join(updates)} WHERE id = ?', values)
        conn.commit()
    cursor.execute('SELECT * FROM pages WHERE id = ?', (page_id,))
    page = dict(cursor.fetchone())
    conn.close()
    return jsonify(page)

@app.route('/api/pages/<int:page_id>/toggle-pin', methods=['POST'])
def toggle_pin(page_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT is_pinned FROM pages WHERE id = ?', (page_id,))
    row = cursor.fetchone()
    new_pinned = 0 if row[0] else 1
    cursor.execute('UPDATE pages SET is_pinned = ? WHERE id = ?', (new_pinned, page_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'is_pinned': new_pinned})

@app.route('/api/pages/<int:page_id>/move-to-trash', methods=['POST'])
def move_to_trash(page_id):
    conn = get_db()
    cursor = conn.cursor()
    mark_tree_deleted(cursor, page_id, is_deleted=True)
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/pages/<int:page_id>/restore', methods=['POST'])
def restore_page(page_id):
    conn = get_db()
    cursor = conn.cursor()
    mark_tree_deleted(cursor, page_id, is_deleted=False)
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/pages/<int:page_id>/copy', methods=['POST'])
def copy_page(page_id):
    """ページをコピー（ツリー構造ごと）"""
    data = request.json or {}
    parent_id = data.get('parent_id')
    
    conn = get_db()
    cursor = conn.cursor()
    
    # 元のページを取得してタイトルに「のコピー」を追加
    cursor.execute('SELECT title FROM pages WHERE id = ?', (page_id,))
    original = cursor.fetchone()
    new_title = (dict(original)['title'] if original else '無題') + 'のコピー'
    
    new_page_id = copy_page_tree(cursor, page_id, new_parent_id=parent_id, new_title=new_title)
    
    conn.commit()
    cursor.execute('SELECT * FROM pages WHERE id = ?', (new_page_id,))
    new_page = dict(cursor.fetchone())
    conn.close()
    
    return jsonify(new_page)

@app.route('/api/pages/<int:page_id>', methods=['DELETE'])
def delete_page(page_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('PRAGMA foreign_keys = ON')
    hard_delete_tree(cursor, page_id)
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    if not query: return jsonify([])
    conn = get_db()
    cursor = conn.cursor()
    search_query = f"{query}*"
    try:
        sql = '''
            SELECT blocks.id as block_id, blocks.page_id, pages.title as page_title, pages.icon, blocks.content, 
                   snippet(blocks_fts, 0, '<b>', '</b>', '...', 10) as snippet,
                   pages.parent_id
            FROM blocks_fts
            JOIN blocks ON blocks_fts.rowid = blocks.id
            JOIN pages ON blocks.page_id = pages.id
            WHERE blocks_fts MATCH ?
            ORDER BY rank
            LIMIT 20
        '''
        cursor.execute(sql, (search_query,))
        results = [dict(row) for row in cursor.fetchall()]
        
        # 各結果にパンくず（祖先パス）を追加
        for result in results:
            breadcrumb = []
            current_id = result.get('parent_id')
            while current_id:
                cursor.execute('SELECT id, title, icon, parent_id FROM pages WHERE id = ?', (current_id,))
                parent_row = cursor.fetchone()
                if parent_row:
                    parent_dict = dict(parent_row)
                    breadcrumb.insert(0, {
                        'id': parent_dict['id'],
                        'title': parent_dict['title'],
                        'icon': parent_dict['icon']
                    })
                    current_id = parent_dict['parent_id']
                else:
                    break
            result['breadcrumb'] = breadcrumb
    except Exception as e:
        results = []
    conn.close()
    return jsonify(results)

@app.route('/api/pages/<int:page_id>/blocks', methods=['POST'])
def create_block(page_id):
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    if data.get('position') is not None:
        new_pos = float(data.get('position'))
    else:
        new_pos = get_block_next_position(cursor, page_id)
    cursor.execute('INSERT INTO blocks (page_id, type, content, checked, position, props) VALUES (?, ?, ?, ?, ?, ?)',
                   (page_id, data.get('type', 'text'), data.get('content', ''), data.get('checked', False), new_pos, data.get('props', '{}')))
    block_id = cursor.lastrowid
    conn.commit()
    cursor.execute('SELECT * FROM blocks WHERE id = ?', (block_id,))
    block = dict(cursor.fetchone())
    conn.close()
    return jsonify(block)

@app.route('/api/blocks/<int:block_id>', methods=['PUT'])
def update_block(block_id):
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    updates = []
    values = []
    fields = ['type', 'content', 'checked', 'position', 'collapsed', 'details', 'props']
    for field in fields:
        if field in data:
            updates.append(f'{field} = ?')
            values.append(data[field])
    if updates:
        updates.append('updated_at = CURRENT_TIMESTAMP')
        values.append(block_id)
        cursor.execute(f'UPDATE blocks SET {", ".join(updates)} WHERE id = ?', values)
        conn.commit()
    cursor.execute('SELECT * FROM blocks WHERE id = ?', (block_id,))
    block = dict(cursor.fetchone())
    conn.close()
    return jsonify(block)

@app.route('/api/blocks/<int:block_id>', methods=['DELETE'])
def delete_block(block_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM blocks WHERE id = ?', (block_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


@app.route('/api/calc-calories', methods=['POST'])
def calc_calories():
    """メニュー文字列から概算カロリーを返す"""
    data = request.json or {}
    raw_lines = data.get('lines', '')
    if isinstance(raw_lines, list):
        lines = raw_lines
    else:
        lines = str(raw_lines).splitlines()
    result = estimate_calories(lines)
    return jsonify(result)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files: return jsonify({'error': 'No file'}), 400
    file = request.files['file']
    page_id = request.form.get('page_id')
    is_cover = request.form.get('is_cover') == 'true'
    if file.filename == '' or not allowed_file(file.filename): return jsonify({'error': 'Invalid file'}), 400
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4()}_{filename}"
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
    file_url = f'/uploads/{unique_filename}'
    conn = get_db()
    cursor = conn.cursor()
    if is_cover and page_id:
        cursor.execute('UPDATE pages SET cover_image = ? WHERE id = ?', (file_url, page_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'file_url': file_url, 'type': 'cover'})
    elif page_id:
        cursor.execute('SELECT MAX(position) FROM blocks WHERE page_id = ?', (page_id,))
        new_pos = (cursor.fetchone()[0] or -1) + 1
        block_type = 'image' if filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp'} else 'file'
        cursor.execute('INSERT INTO blocks (page_id, type, content, position) VALUES (?, ?, ?, ?)',
                       (page_id, block_type, file_url, new_pos))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'file_url': file_url, 'block_type': block_type})
    return jsonify({'error': 'Page ID missing'}), 400

# --- エクスポート/インポート機能 ---
@app.route('/api/export/all/json', methods=['GET'])
def export_all_json():
    """全ページをJSON形式でエクスポート"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM pages WHERE is_deleted = 0 AND parent_id IS NULL ORDER BY position')
    root_pages = [export_page_to_dict(cursor, row['id']) for row in cursor.fetchall()]
    conn.close()
    
    export_data = {
        'version': '1.0',
        'exported_at': datetime.now().isoformat(),
        'pages': root_pages
    }
    
    response = send_file(
        io.BytesIO(json.dumps(export_data, ensure_ascii=False, indent=2).encode('utf-8')),
        mimetype='application/json',
        as_attachment=True,
        download_name=f"diary_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    return response


@app.route('/api/export/pages/<int:page_id>/json', methods=['GET'])
def export_page_json(page_id):
    """指定ページをJSON形式でエクスポート"""
    conn = get_db()
    cursor = conn.cursor()
    page = export_page_to_dict(cursor, page_id)
    conn.close()
    
    if not page:
        return jsonify({'error': 'Page not found'}), 404
    
    export_data = {
        'version': '1.0',
        'exported_at': datetime.now().isoformat(),
        'page': page
    }
    
    response = send_file(
        io.BytesIO(json.dumps(export_data, ensure_ascii=False, indent=2).encode('utf-8')),
        mimetype='application/json',
        as_attachment=True,
        download_name=f"{page.get('title', 'page')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    return response


@app.route('/api/export/pages/<int:page_id>/markdown', methods=['GET'])
def export_page_markdown(page_id):
    """指定ページをMarkdown形式でエクスポート"""
    conn = get_db()
    cursor = conn.cursor()
    page = export_page_to_dict(cursor, page_id)
    conn.close()
    
    if not page:
        return jsonify({'error': 'Page not found'}), 404
    
    markdown_content = page_to_markdown(page, level=1)
    
    response = send_file(
        io.BytesIO(markdown_content.encode('utf-8')),
        mimetype='text/markdown',
        as_attachment=True,
        download_name=f"{page.get('title', 'page')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    )
    return response


@app.route('/api/export/pages/<int:page_id>/zip', methods=['GET'])
def export_page_zip(page_id):
    """指定ページを添付ファイル含めZIP化してエクスポート"""
    conn = get_db()
    cursor = conn.cursor()
    page = export_page_to_dict(cursor, page_id)
    conn.close()
    
    if not page:
        return jsonify({'error': 'Page not found'}), 404
    
    # ZIPファイルをメモリに作成
    zip_buffer = io.BytesIO()
    
    def add_page_to_zip(z, pg, prefix=''):
        """ページとその子ページを再帰的にZIPに追加"""
        page_dir = f"{prefix}{pg.get('title', '無題')}_[{pg['id']}]"
        
        # Markdownファイル追加
        md_content = page_to_markdown(pg, level=1)
        z.writestr(f"{page_dir}/page.md", md_content.encode('utf-8'))
        
        # メタデータJSON追加
        metadata = {
            'id': pg['id'],
            'title': pg.get('title', ''),
            'icon': pg.get('icon', ''),
            'created_at': pg.get('created_at', ''),
            'updated_at': pg.get('updated_at', '')
        }
        z.writestr(f"{page_dir}/metadata.json", json.dumps(metadata, ensure_ascii=False, indent=2).encode('utf-8'))
        
        # 添付ファイルをコピー
        for block in pg.get('blocks', []):
            if block.get('type') in ['image', 'file']:
                file_path = block.get('content', '')
                if file_path and file_path.startswith('/uploads/'):
                    filename = file_path.split('/')[-1]
                    full_path = os.path.join(UPLOAD_FOLDER, filename)
                    if os.path.exists(full_path):
                        z.write(full_path, f"{page_dir}/files/{filename}")
        
        # 子ページを再帰追加
        for child in pg.get('children', []):
            add_page_to_zip(z, child, f"{page_dir}/")
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        add_page_to_zip(zf, page)
    
    zip_buffer.seek(0)
    response = send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f"{page.get('title', 'page')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    )
    return response


@app.route('/api/import/json', methods=['POST'])
def import_json():
    """JSONファイルをインポート"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '' or not file.filename.endswith('.json'):
        return jsonify({'error': 'Invalid file format, expected JSON'}), 400
    
    try:
        import_data = json.loads(file.read().decode('utf-8'))
    except Exception as e:
        return jsonify({'error': f'Failed to parse JSON: {str(e)}'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        imported_ids = []
        
        # "pages"キーがあれば複数ページ、"page"キーがあれば単一ページ
        pages_to_import = import_data.get('pages', [])
        if import_data.get('page'):
            pages_to_import = [import_data.get('page')]
        
        for page_dict in pages_to_import:
            new_id = create_page_from_dict(cursor, page_dict)
            imported_ids.append(new_id)
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'{len(imported_ids)} page(s) imported',
            'imported_ids': imported_ids
        })
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'error': f'Import failed: {str(e)}'}), 500


@app.route('/api/import/zip', methods=['POST'])
def import_zip():
    """ZIPファイルをインポート"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '' or not file.filename.endswith('.zip'):
        return jsonify({'error': 'Invalid file format, expected ZIP'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # ZIPを開く
        with zipfile.ZipFile(io.BytesIO(file.read()), 'r') as zf:
            # 最初のmetadata.jsonを見つけて親ページを作成
            metadata_files = [f for f in zf.namelist() if f.endswith('metadata.json') and f.count('/') == 1]
            
            if not metadata_files:
                return jsonify({'error': 'No valid ZIP structure found'}), 400
            
            imported_ids = []
            
            for metadata_file in metadata_files:
                metadata = json.loads(zf.read(metadata_file).decode('utf-8'))
                
                # メタデータから新規ページを作成
                cursor.execute('SELECT MAX(position) FROM pages WHERE parent_id IS NULL')
                max_pos = cursor.fetchone()[0]
                position = (max_pos if max_pos is not None else -1) + 1
                
                cursor.execute(
                    'INSERT INTO pages (title, icon, parent_id, position) VALUES (?, ?, ?, ?)',
                    (metadata.get('title', ''), metadata.get('icon', '📄'), None, position)
                )
                new_page_id = cursor.lastrowid
                imported_ids.append(new_page_id)
                
                # ページディレクトリ内のpage.mdを読み込む
                page_dir = metadata_file.split('/')[0]
                page_md_path = f"{page_dir}/page.md"
                
                if page_md_path in zf.namelist():
                    md_content = zf.read(page_md_path).decode('utf-8')
                    # テキストブロックとして最初のブロックに内容を追加
                    cursor.execute(
                        "INSERT INTO blocks (page_id, type, content, position) VALUES (?, 'text', ?, 0)",
                        (new_page_id, md_content)
                    )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'{len(imported_ids)} page(s) imported from ZIP',
            'imported_ids': imported_ids
        })
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'error': f'ZIP import failed: {str(e)}'}), 500

# --- テンプレート管理機能 ---
@app.route('/api/templates', methods=['GET'])
def get_templates():
    """テンプレート一覧を取得"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM templates ORDER BY created_at DESC')
    templates = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(templates)

@app.route('/api/templates', methods=['POST'])
def create_template():
    """新しいテンプレートを作成"""
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT INTO templates (name, icon, description, content_json) VALUES (?, ?, ?, ?)',
        (
            data.get('name', '新しいテンプレート'),
            data.get('icon', '📋'),
            data.get('description', ''),
            json.dumps(data.get('content', {}), ensure_ascii=False)
        )
    )
    template_id = cursor.lastrowid
    conn.commit()
    
    cursor.execute('SELECT * FROM templates WHERE id = ?', (template_id,))
    template = dict(cursor.fetchone())
    conn.close()
    return jsonify(template)

@app.route('/api/templates/<int:template_id>', methods=['PUT'])
def update_template(template_id):
    """テンプレートを更新"""
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    updates = []
    values = []
    
    if 'name' in data:
        updates.append('name = ?')
        values.append(data['name'])
    if 'icon' in data:
        updates.append('icon = ?')
        values.append(data['icon'])
    if 'description' in data:
        updates.append('description = ?')
        values.append(data['description'])
    if 'content' in data:
        updates.append('content_json = ?')
        values.append(json.dumps(data['content'], ensure_ascii=False))
    
    if updates:
        updates.append('updated_at = CURRENT_TIMESTAMP')
        values.append(template_id)
        cursor.execute(f'UPDATE templates SET {', '.join(updates)} WHERE id = ?', values)
        conn.commit()
    
    cursor.execute('SELECT * FROM templates WHERE id = ?', (template_id,))
    template = dict(cursor.fetchone())
    conn.close()
    return jsonify(template)

@app.route('/api/templates/<int:template_id>', methods=['DELETE'])
def delete_template(template_id):
    """テンプレートを削除"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM templates WHERE id = ?', (template_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/pages/from-custom-template/<int:template_id>', methods=['POST'])
def create_page_from_custom_template(template_id):
    """カスタムテンプレートからページを作成"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM templates WHERE id = ?', (template_id,))
    template_row = cursor.fetchone()
    
    if not template_row:
        conn.close()
        return jsonify({'error': 'Template not found'}), 404
    
    template = dict(template_row)
    content = json.loads(template['content_json'])
    
    # 新しいページを作成
    new_pos = get_next_position(cursor, None)
    cursor.execute(
        'INSERT INTO pages (title, icon, parent_id, position) VALUES (?, ?, ?, ?)',
        (content.get('title', template['name']), template['icon'], None, new_pos)
    )
    page_id = cursor.lastrowid
    
    # ブロックを追加
    for i, block in enumerate(content.get('blocks', [])):
        cursor.execute(
            'INSERT INTO blocks (page_id, type, content, checked, position, collapsed, details, props) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (
                page_id,
                block.get('type', 'text'),
                block.get('content', ''),
                block.get('checked', 0),
                (i + 1) * 1000.0,
                block.get('collapsed', 0),
                block.get('details', ''),
                block.get('props', '{}')
            )
        )
    
    # 子ページを追加
    for i, child in enumerate(content.get('children', [])):
        child_pos = (i + 1) * 1000.0
        cursor.execute(
            'INSERT INTO pages (title, icon, parent_id, position) VALUES (?, ?, ?, ?)',
            (child.get('title', ''), child.get('icon', '📄'), page_id, child_pos)
        )
        child_id = cursor.lastrowid
        
        for j, block in enumerate(child.get('blocks', [])):
            cursor.execute(
                'INSERT INTO blocks (page_id, type, content, checked, position, props) VALUES (?, ?, ?, ?, ?, ?)',
                (child_id, block.get('type', 'text'), block.get('content', ''), block.get('checked', 0), (j + 1) * 1000.0, '{}')
            )
    
    conn.commit()
    cursor.execute('SELECT * FROM pages WHERE id = ?', (page_id,))
    page = dict(cursor.fetchone())
    conn.close()
    return jsonify(page)

@app.route('/api/pages/<int:page_id>/save-as-template', methods=['POST'])
def save_page_as_template(page_id):
    """現在のページをテンプレートとして保存"""
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    # ページとブロックを取得
    page_dict = export_page_to_dict(cursor, page_id)
    if not page_dict:
        conn.close()
        return jsonify({'error': 'Page not found'}), 404
    
    # テンプレート用のコンテンツを構築
    template_content = {
        'title': page_dict.get('title', ''),
        'blocks': page_dict.get('blocks', []),
        'children': page_dict.get('children', [])
    }
    
    # テンプレートを作成
    cursor.execute(
        'INSERT INTO templates (name, icon, description, content_json) VALUES (?, ?, ?, ?)',
        (
            data.get('name', page_dict.get('title', '新しいテンプレート')),
            page_dict.get('icon', '📋'),
            data.get('description', ''),
            json.dumps(template_content, ensure_ascii=False)
        )
    )
    template_id = cursor.lastrowid
    conn.commit()
    
    cursor.execute('SELECT * FROM templates WHERE id = ?', (template_id,))
    template = dict(cursor.fetchone())
    conn.close()
    return jsonify(template)

# --- Webhook (自動更新用) ---
@app.route('/webhook_deploy', methods=['POST'])
def webhook_deploy():
    # ユーザー名部分は適宜変更してください
    subprocess.run(['git', 'fetch', '--all'], cwd='/home/nnnkeita/mysite')
    subprocess.run(['git', 'reset', '--hard', 'origin/main'], cwd='/home/nnnkeita/mysite')
    subprocess.run(['touch', '/var/www/nnnkeita_pythonanywhere_com_wsgi.py'])
    return jsonify({'status': 'success', 'message': 'Deployed and Reloaded!'})

if __name__ == '__main__':
    import webbrowser
    from threading import Timer
    
    # 1秒後にブラウザを自動で開く予約をする
    def open_browser():
        webbrowser.open_new('http://127.0.0.1:5000/')
    
    Timer(1, open_browser).start()
    
    # アプリとして起動（ポート5000で待機）
    with app.app_context():
        init_db()
    app.run(port=5000)
else:
    # PythonAnywhere用のWSGI
    with app.app_context():
        init_db()