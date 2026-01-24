# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify, send_from_directory
import sqlite3
import json
import os
from werkzeug.utils import secure_filename
import uuid
import subprocess

# --- パス設定（PythonAnywhereで迷子にならないように絶対パスで指定） ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'notion.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'templates')

# --- アプリケーションの初期化（ここが重要！） ---
# template_folderを明示的に指定してエラーを防ぐ
app = Flask(__name__, template_folder=TEMPLATE_FOLDER)

# アップロード設定
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'webp', 'zip', 'docx'}

# ================== データベース設定 ==================
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # ページテーブル（カバー画像カラムなどを確実に作成）
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
    
    # 既存DBへのカラム追加対策（エラー無視）
    try:
        cursor.execute("ALTER TABLE pages ADD COLUMN cover_image TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass 

    # ブロックテーブル
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
    
    # 全文検索用テーブル
    cursor.execute('''
    CREATE VIRTUAL TABLE IF NOT EXISTS blocks_fts USING fts5(content, content=blocks, content_rowid=id)
    ''')

    # トリガー設定（検索インデックスの自動更新）
    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS blocks_ai AFTER INSERT ON blocks BEGIN
      INSERT INTO blocks_fts(rowid, content) VALUES (new.id, new.content);
    END;
    ''')
    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS blocks_ad AFTER DELETE ON blocks BEGIN
      INSERT INTO blocks_fts(blocks_fts, rowid, content) VALUES('delete', old.id, old.content);
    END;
    ''')
    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS blocks_au AFTER UPDATE ON blocks BEGIN
      INSERT INTO blocks_fts(blocks_fts, rowid, content) VALUES('delete', old.id, old.content);
      INSERT INTO blocks_fts(rowid, content) VALUES (new.id, new.content);
    END;
    ''')
    
    conn.commit()
    conn.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ================== ルーティング ==================

@app.route('/')
def index():
    # 明示的にtemplateフォルダ内のファイルを指定
    return render_template('index.html')

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/api/pages', methods=['GET'])
def get_pages():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM pages ORDER BY position ASC, created_at ASC')
    all_pages = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    # ツリー構造への変換
    page_map = {page['id']: {**page, 'children': []} for page in all_pages}
    roots = []
    for page in all_pages:
        if page['parent_id'] and page['parent_id'] in page_map:
            page_map[page['parent_id']]['children'].append(page_map[page['id']])
        else:
            roots.append(page_map[page['id']])
    return jsonify(roots)

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
    
    # 初期ブロック
    cursor.execute("INSERT INTO blocks (page_id, type, content, position) VALUES (?, 'text', '', 0)", (page_id,))
    
    conn.commit()
    cursor.execute('SELECT * FROM pages WHERE id = ?', (page_id,))
    page = dict(cursor.fetchone())
    conn.close()
    return jsonify(page)

@app.route('/api/pages/from-date', methods=['POST'])
def create_page_from_date():
    data = request.json
    date_str = data.get('date')  # フォーマット: YYYY-MM-DD
    
    conn = get_db()
    cursor = conn.cursor()
    
    # 日付でページを作成（タイトルは日付）
    cursor.execute('SELECT MAX(position) FROM pages WHERE parent_id IS NULL')
    max_pos = cursor.fetchone()[0]
    new_pos = (max_pos if max_pos is not None else -1) + 1
    
    # 日付のフォーマットを「2026年1月24日」に変換
    from datetime import datetime
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    formatted_date = date_obj.strftime('%Y年%m月%d日')
    
    cursor.execute('INSERT INTO pages (title, icon, parent_id, position) VALUES (?, ?, ?, ?)',
                   (formatted_date, '📅', None, new_pos))
    page_id = cursor.lastrowid
    
    # 初期ブロック
    cursor.execute("INSERT INTO blocks (page_id, type, content, position) VALUES (?, 'text', '', 0)", (page_id,))
    
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
    
    fields = ['title', 'icon', 'parent_id', 'cover_image']
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

@app.route('/api/pages/<int:page_id>', methods=['DELETE'])
def delete_page(page_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('PRAGMA foreign_keys = ON')
    cursor.execute('DELETE FROM pages WHERE id = ?', (page_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# --- 全文検索 ---
@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    if not query: return jsonify([])
    conn = get_db()
    cursor = conn.cursor()
    # 簡易FTS検索
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
    except Exception as e:
        print(e)
        results = []
    conn.close()
    return jsonify(results)

# --- ブロック操作 ---
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
    
    fields = ['type', 'content', 'checked', 'position']
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

# --- 自動デプロイ用Webhook ---
@app.route('/webhook_deploy', methods=['POST'])
def webhook_deploy():
    # GitHubから最新コードを強制的に取得
    subprocess.run(['git', 'fetch', '--all'], cwd='/home/nnnkeita/mysite')
    subprocess.run(['git', 'reset', '--hard', 'origin/main'], cwd='/home/nnnkeita/mysite')
    
    # サーバーをリロード（タッチ）
    subprocess.run(['touch', '/var/www/nnnkeita_pythonanywhere_com_wsgi.py'])
    
    return jsonify({'status': 'success', 'message': 'Deployed and Reloaded!'})

# 初期化実行（インポート時にも走るようにコンテキスト内で行う）
with app.app_context():
    init_db()

# PythonAnywhereはこの if __name__ == ... ブロックを実行しません
# ローカル開発用として残しておきますが、PythonAnywhereではコメントアウト
# if __name__ == '__main__':
#     app.run(debug=True, port=5001)