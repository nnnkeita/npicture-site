#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""旧スキーマから2月9日バックアップを復元"""

import sqlite3
import json
from pathlib import Path

def restore_from_backup(backup_path):
    """旧スキーマで2月9日のバックアップを復元"""
    
    backup_file = Path(backup_path)
    db_path = Path('notion.db')
    
    if not backup_file.exists():
        print(f"❌ Backup not found: {backup_file}")
        return False
    
    # バックアップ読み込み
    with open(backup_file, 'r', encoding='utf-8') as f:
        backup_data = json.load(f)
    
    print(f"📖 Loading backup from {backup_file.name}")
    print(f"   Timestamp: {backup_data.get('timestamp', 'N/A')}")
    
    # 新しいDBを作成
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    
    # pages テーブル（旧スキーマ）
    print("🔨 Creating database schema (old version)...")
    c.execute('''
    CREATE TABLE pages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT DEFAULT '',
        icon TEXT DEFAULT '📄',
        cover_image TEXT DEFAULT '',
        parent_id INTEGER,
        position REAL DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_pinned BOOLEAN DEFAULT 0,
        is_deleted BOOLEAN DEFAULT 0,
        mood INTEGER DEFAULT 0,
        gratitude_text TEXT DEFAULT '',
        position_new REAL DEFAULT 0.0,
        FOREIGN KEY (parent_id) REFERENCES pages(id) ON DELETE CASCADE
    )
    ''')
    
    # blocks テーブル（旧スキーマ）
    c.execute('''
    CREATE TABLE blocks (
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
    
    # templates テーブル
    c.execute('''
    CREATE TABLE templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        icon TEXT DEFAULT '📋',
        description TEXT DEFAULT '',
        content_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # users テーブル
    c.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        stripe_customer_id TEXT,
        subscription_status TEXT DEFAULT 'inactive',
        subscription_ends_at TEXT,
        created_at TEXT
    )
    ''')
    
    # password_reset_tokens テーブル
    c.execute('''
    CREATE TABLE password_reset_tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token TEXT NOT NULL UNIQUE,
        expires_at TEXT,
        used BOOLEAN DEFAULT 0,
        created_at TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    ''')
    
    # healthplanet_tokens テーブル（存在する場合）
    c.execute('''
    CREATE TABLE healthplanet_tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        access_token TEXT NOT NULL,
        refresh_token TEXT,
        expires_at TEXT,
        scope TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    ''')
    
    # FTS テーブル
    c.execute('CREATE VIRTUAL TABLE blocks_fts USING fts5(title, content, content=blocks, content_rowid=id)')
    
    # Table mappings
    table_mappings = {
        'pages': ['id', 'title', 'icon', 'cover_image', 'parent_id', 'position', 
                  'created_at', 'updated_at', 'is_pinned', 'is_deleted', 'mood', 
                  'gratitude_text', 'position_new'],
        'blocks': ['id', 'page_id', 'type', 'content', 'checked', 'position',
                  'collapsed', 'details', 'props', 'created_at', 'updated_at'],
        'templates': ['id', 'name', 'icon', 'description', 'content_json', 
                     'created_at', 'updated_at'],
        'users': ['id', 'username', 'password_hash', 'stripe_customer_id',
                 'subscription_status', 'subscription_ends_at', 'created_at'],
        'password_reset_tokens': ['id', 'user_id', 'token', 'expires_at', 'used', 'created_at'],
        'healthplanet_tokens': ['id', 'access_token', 'refresh_token', 'expires_at', 'scope', 
                               'created_at', 'updated_at']
    }
    
    print("✓ Schema created")
    print("📥 Restoring data...")
    
    # データ復元
    for table_name, rows in backup_data['tables'].items():
        if not rows:
            print(f"  ✓ {table_name}: 0 rows")
            continue
        
        if table_name not in table_mappings:
            print(f"  ⊘ {table_name}: skipped (unknown table)")
            continue
        
        # 利用可能なカラムを判定
        available_cols = table_mappings[table_name]
        placeholders = ', '.join(['?' for _ in available_cols])
        
        for row in rows:
            values = [row.get(col) for col in available_cols]
            try:
                c.execute(f"INSERT INTO {table_name} ({','.join(available_cols)}) VALUES ({placeholders})", values)
            except Exception as e:
                print(f"  ⚠️  Error in {table_name}: {e}")
                continue
        
        print(f"  ✓ {table_name}: {len(rows)} rows restored")
    
    # Indexes
    try:
        c.execute('CREATE INDEX idx_pages_parent_position ON pages(parent_id, position, is_deleted)')
    except:
        pass
    
    try:
        c.execute('CREATE INDEX idx_blocks_page_position ON blocks(page_id, position)')
    except:
        pass
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Database restored successfully from {backup_file.name}")
    return True

if __name__ == '__main__':
    import sys
    backup_path = sys.argv[1] if len(sys.argv) > 1 else '/Users/nishiharakeita/Downloads/backup_20260209_041133.json'
    restore_from_backup(backup_path)
