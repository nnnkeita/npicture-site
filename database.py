# -*- coding: utf-8 -*-
"""
データベース関連の処理
- DB接続
- テーブル初期化
- 基本的なヘルパー関数
"""
import sqlite3
import os

# パス設定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'notion.db')

def get_db():
    """データベース接続を取得"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """データベーステーブルを初期化"""
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
    
    # パフォーマンス改善用インデックス
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pages_parent_position ON pages(parent_id, position, is_deleted)')
    except sqlite3.OperationalError:
        pass
    
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pages_is_deleted ON pages(is_deleted)')
    except sqlite3.OperationalError:
        pass
    
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_blocks_page_position ON blocks(page_id, position)')
    except sqlite3.OperationalError:
        pass
    
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

def get_next_position(cursor, parent_id):
    """次のposition値を計算（1000刻み方式）"""
    if parent_id:
        cursor.execute('SELECT MAX(position) FROM pages WHERE parent_id = ?', (parent_id,))
    else:
        cursor.execute('SELECT MAX(position) FROM pages WHERE parent_id IS NULL')
    max_pos = cursor.fetchone()[0]
    if max_pos is None:
        return 1000.0
    return max_pos + 1000.0

def get_block_next_position(cursor, page_id):
    """ブロックの次のposition値を計算"""
    cursor.execute('SELECT MAX(position) FROM blocks WHERE page_id = ?', (page_id,))
    max_pos = cursor.fetchone()[0]
    if max_pos is None:
        return 1000.0
    return max_pos + 1000.0

def mark_tree_deleted(cursor, page_id, is_deleted=True):
    """ページとその全子ページを再帰的に削除フラグ変更（soft delete）"""
    cursor.execute('UPDATE pages SET is_deleted = ? WHERE id = ?', (1 if is_deleted else 0, page_id))
    cursor.execute('SELECT id FROM pages WHERE parent_id = ?', (page_id,))
    for row in cursor.fetchall():
        mark_tree_deleted(cursor, row['id'], is_deleted)

def hard_delete_tree(cursor, page_id):
    """ページとその全子ページを再帰的に完全削除（hard delete）"""
    cursor.execute('SELECT id FROM pages WHERE parent_id = ?', (page_id,))
    for row in cursor.fetchall():
        hard_delete_tree(cursor, row['id'])
    cursor.execute('DELETE FROM pages WHERE id = ?', (page_id,))

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
