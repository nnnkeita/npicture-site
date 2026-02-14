#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""完全復元スクリプト - スキーマから完全初期化して復元"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

def restore_complete(backup_file_path):
    """バックアップから完全復元（スキーマを初期化してからデータを挿入）"""
    
    backup_file = Path(backup_file_path)
    db_path = Path('notion.db')
    
    if not backup_file.exists():
        print(f"❌ Backup file not found: {backup_file}")
        return False
    
    try:
        # バックアップを読み込み
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        print(f"📖 Loading backup from {backup_file.name}")
        print(f"   Timestamp: {backup_data.get('timestamp', 'N/A')}")
        
        # 既存DBをバックアップ
        if db_path.exists():
            backup_copy = db_path.with_suffix('.db.backup')
            db_path.rename(backup_copy)
            print(f"✓ Old DB backed up to {backup_copy.name}")
        
        # 新しいDBを作成して初期化
        conn = sqlite3.connect(str(db_path))
        c = conn.cursor()
        
        # テーブル作成（正規スキーマ）
        print("🔨 Creating database schema...")
        
        # pages テーブル
        c.execute('''
        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT DEFAULT '',
            icon TEXT DEFAULT '📄',
            cover_image TEXT DEFAULT '',
            parent_id INTEGER,
            position REAL DEFAULT 0.0,
            position_new REAL DEFAULT 0.0,
            is_pinned BOOLEAN DEFAULT 0,
            is_deleted BOOLEAN DEFAULT 0,
            mood INTEGER DEFAULT 0,
            gratitude_text TEXT DEFAULT '',
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY (parent_id) REFERENCES pages(id) ON DELETE CASCADE
        )
        ''')
        
        # blocks テーブル
        c.execute('''
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
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY (page_id) REFERENCES pages(id) ON DELETE CASCADE
        )
        ''')
        
        # templates テーブル
        c.execute('''
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            icon TEXT DEFAULT '📋',
            description TEXT DEFAULT '',
            content_json TEXT NOT NULL,
            created_at TEXT,
            updated_at TEXT
        )
        ''')
        
        # users テーブル
        c.execute('''
        CREATE TABLE IF NOT EXISTS users (
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
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT NOT NULL UNIQUE,
            expires_at TEXT,
            used BOOLEAN DEFAULT 0,
            created_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        ''')
        
        # healthplanet_tokens テーブル
        c.execute('''
        CREATE TABLE IF NOT EXISTS healthplanet_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            access_token TEXT NOT NULL,
            refresh_token TEXT,
            expires_at TEXT,
            scope TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        ''')
        
        # インデックス作成
        c.execute('CREATE INDEX IF NOT EXISTS idx_pages_parent_position ON pages(parent_id, position)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_blocks_page_position ON blocks(page_id, position)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_pages_is_deleted ON pages(is_deleted)')
        
        print("✓ Schema created")
        
        # バックアップからデータを復元
        print("📥 Restoring data...")
        for table_name, rows in backup_data['tables'].items():
            if not rows:
                print(f"  ✓ {table_name}: 0 rows")
                continue
            
            # テーブルが存在しなければスキップ
            if table_name not in ['pages', 'blocks', 'templates', 'users', 'password_reset_tokens', 'healthplanet_tokens']:
                print(f"  ⊘ {table_name}: skipped (unknown table)")
                continue
            
            # INSERT
            first_row = rows[0]
            keys = list(first_row.keys())
            placeholders = ', '.join(['?' for _ in keys])
            
            for row in rows:
                values = [row.get(k) for k in keys]
                try:
                    c.execute(f"INSERT INTO {table_name} ({','.join(keys)}) VALUES ({placeholders})", values)
                except Exception as e:
                    print(f"  ⚠️  Error inserting into {table_name}: {e}")
                    continue
            
            print(f"  ✓ {table_name}: {len(rows)} rows restored")
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Database completely restored from {backup_file.name}")
        return True
        
    except Exception as e:
        print(f"❌ Restore failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    import sys
    backup_path = sys.argv[1] if len(sys.argv) > 1 else 'backups/backup_20260213_210129.json'
    restore_complete(backup_path)
