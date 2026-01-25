# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify, send_from_directory
import sqlite3
import json
import os
from werkzeug.utils import secure_filename
import uuid
import subprocess
from datetime import datetime, timedelta

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
        position INTEGER DEFAULT 0,
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
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS blocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        page_id INTEGER NOT NULL,
        type TEXT DEFAULT 'text',
        content TEXT DEFAULT '',
        checked BOOLEAN DEFAULT 0,
        position INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (page_id) REFERENCES pages(id) ON DELETE CASCADE
    )
    ''')
    cursor.execute('CREATE VIRTUAL TABLE IF NOT EXISTS blocks_fts USING fts5(content, content=blocks, content_rowid=id)')
    cursor.execute('CREATE TRIGGER IF NOT EXISTS blocks_ai AFTER INSERT ON blocks BEGIN INSERT INTO blocks_fts(rowid, content) VALUES (new.id, new.content); END;')
    cursor.execute('CREATE TRIGGER IF NOT EXISTS blocks_ad AFTER DELETE ON blocks BEGIN INSERT INTO blocks_fts(blocks_fts, rowid, content) VALUES("delete", old.id, old.content); END;')
    cursor.execute('CREATE TRIGGER IF NOT EXISTS blocks_au AFTER UPDATE ON blocks BEGIN INSERT INTO blocks_fts(blocks_fts, rowid, content) VALUES("delete", old.id, old.content); INSERT INTO blocks_fts(rowid, content) VALUES (new.id, new.content); END;')
    conn.commit()
    conn.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
        if parent_id:
            cursor.execute('SELECT MAX(position) FROM pages WHERE parent_id = ?', (parent_id,))
        else:
            cursor.execute('SELECT MAX(position) FROM pages WHERE parent_id IS NULL')
        max_pos = cursor.fetchone()[0]
        position = (max_pos if max_pos is not None else -1) + 1

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

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

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

@app.route('/api/pages', methods=['POST'])
def create_page():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    parent_id = data.get('parent_id')
    if parent_id:
        cursor.execute('SELECT MAX(position) FROM pages WHERE parent_id = ?', (parent_id,))
    else:
        cursor.execute('SELECT MAX(position) FROM pages WHERE parent_id IS NULL')
    max_pos = cursor.fetchone()[0]
    new_pos = (max_pos if max_pos is not None else -1) + 1
    cursor.execute('INSERT INTO pages (title, icon, parent_id, position) VALUES (?, ?, ?, ?)',
                   (data.get('title', ''), data.get('icon', '📄'), parent_id, new_pos))
    page_id = cursor.lastrowid
    cursor.execute("INSERT INTO blocks (page_id, type, content, position) VALUES (?, 'text', '', 0)", (page_id,))
    conn.commit()
    cursor.execute('SELECT * FROM pages WHERE id = ?', (page_id,))
    page = dict(cursor.fetchone())
    conn.close()
    return jsonify(page)

# --- カレンダーからページ作成用 ---
@app.route('/api/pages/from-date', methods=['POST'])
def create_page_from_date():
    data = request.json
    date_str = data.get('date') # YYYY-MM-DD
    if not date_str: return jsonify({'error': 'Date required'}), 400

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
        conn.close()
        return jsonify(page)
    
    # 親なし(ルート)で作成
    cursor.execute('SELECT MAX(position) FROM pages WHERE parent_id IS NULL')
    max_pos = cursor.fetchone()[0]
    new_pos = (max_pos if max_pos is not None else -1) + 1
    
    cursor.execute('INSERT INTO pages (title, icon, parent_id, position) VALUES (?, ?, ?, ?)',
                   (title, '📅', None, new_pos))
    page_id = cursor.lastrowid

    # 親ページにデフォルトのテキストブロック
    cursor.execute("INSERT INTO blocks (page_id, type, content, position) VALUES (?, 'text', '', 0)", (page_id,))

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
        }
    ]

    for i, child in enumerate(children_templates):
        # 子ページの並び順は0,1,2...
        cursor.execute('INSERT INTO pages (title, icon, parent_id, position) VALUES (?, ?, ?, ?)',
                       (child['title'], child['icon'], page_id, i))
        child_id = cursor.lastrowid
        # 子ページのブロック追加
        for j, block in enumerate(child['blocks']):
            cursor.execute(
                "INSERT INTO blocks (page_id, type, content, checked, position) VALUES (?, ?, ?, ?, ?)",
                (child_id, block['type'], block.get('content', ''), block.get('checked', 0), j)
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
    if parent_id:
        cursor.execute('SELECT MAX(position) FROM pages WHERE parent_id = ?', (parent_id,))
    else:
        cursor.execute('SELECT MAX(position) FROM pages WHERE parent_id IS NULL')
    max_pos = cursor.fetchone()[0]
    new_pos = (max_pos if max_pos is not None else -1) + 1
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
    
    cursor.execute('SELECT MAX(position) FROM pages WHERE parent_id IS NULL')
    max_pos = cursor.fetchone()[0]
    new_pos = (max_pos if max_pos is not None else -1) + 1
    
    cursor.execute('INSERT INTO pages (title, icon, parent_id, position) VALUES (?, ?, ?, ?)',
                   (template['title'], template['icon'], None, new_pos))
    page_id = cursor.lastrowid
    
    # ブロックを追加
    for i, block in enumerate(template['blocks']):
        cursor.execute(
            "INSERT INTO blocks (page_id, type, content, checked, position) VALUES (?, ?, ?, ?, ?)",
            (page_id, block['type'], block['content'], block.get('checked', 0), i)
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
    fields = ['title', 'icon', 'parent_id', 'cover_image', 'is_pinned', 'is_deleted']
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
            SELECT blocks.page_id, pages.title as page_title, blocks.content, snippet(blocks_fts, 0, '<b>', '</b>', '...', 10) as snippet
            FROM blocks_fts
            JOIN blocks ON blocks_fts.rowid = blocks.id
            JOIN pages ON blocks.page_id = pages.id
            WHERE blocks_fts MATCH ?
            ORDER BY rank
            LIMIT 20
        '''
        cursor.execute(sql, (search_query,))
        results = [dict(row) for row in cursor.fetchall()]
    except:
        results = []
    conn.close()
    return jsonify(results)

@app.route('/api/pages/<int:page_id>/blocks', methods=['POST'])
def create_block(page_id):
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    position = data.get('position', 0)
    cursor.execute('UPDATE blocks SET position = position + 1 WHERE page_id = ? AND position >= ?', (page_id, position))
    cursor.execute('INSERT INTO blocks (page_id, type, content, checked, position) VALUES (?, ?, ?, ?, ?)',
                   (page_id, data.get('type', 'text'), data.get('content', ''), data.get('checked', False), position))
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
    fields = ['type', 'content', 'checked', 'position', 'collapsed', 'details']
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

# --- Webhook (自動更新用) ---
@app.route('/webhook_deploy', methods=['POST'])
def webhook_deploy():
    # ユーザー名部分は適宜変更してください
    subprocess.run(['git', 'fetch', '--all'], cwd='/home/nnnkeita/mysite')
    subprocess.run(['git', 'reset', '--hard', 'origin/main'], cwd='/home/nnnkeita/mysite')
    subprocess.run(['touch', '/var/www/nnnkeita_pythonanywhere_com_wsgi.py'])
    return jsonify({'status': 'success', 'message': 'Deployed and Reloaded!'})

with app.app_context():
    init_db()