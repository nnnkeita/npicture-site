#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""完全復元スクリプト - データ型を正しく処理して復元"""

import sqlite3
import json
from pathlib import Path

def restore_safe(backup_file_path):
    """バックアップから完全復元（型を正しく処理）"""
    
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
        CREATE TABLE pages (
            id INTEGER PRIMARY KEY,
            title TEXT DEFAULT '',
            icon TEXT DEFAULT '📄',
            cover_image TEXT DEFAULT '',
            parent_id INTEGER,
            position REAL DEFAULT 0.0,
            position_new REAL DEFAULT 0.0,
            is_pinned INTEGER DEFAULT 0,
            is_deleted INTEGER DEFAULT 0,
            mood INTEGER DEFAULT 0,
            gratitude_text TEXT DEFAULT '',
            created_at TEXT,
            updated_at TEXT
        )
        ''')
        
        # blocks テーブル
        c.execute('''
        CREATE TABLE blocks (
            id INTEGER PRIMARY KEY,
            page_id INTEGER NOT NULL,
            type TEXT DEFAULT 'text',
            content TEXT DEFAULT '',
            checked INTEGER DEFAULT 0,
            position REAL DEFAULT 0.0,
            collapsed INTEGER DEFAULT 0,
            details TEXT DEFAULT '',
            props TEXT DEFAULT '{}',
            created_at TEXT,
            updated_at TEXT
        )
        ''')
        
        # templates テーブル
        c.execute('''
        CREATE TABLE templates (
            id INTEGER PRIMARY KEY,
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
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
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
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            token TEXT NOT NULL UNIQUE,
            expires_at TEXT,
            used INTEGER DEFAULT 0,
            created_at TEXT
        )
        ''')
        
        # healthplanet_tokens テーブル
        c.execute('''
        CREATE TABLE healthplanet_tokens (
            id INTEGER PRIMARY KEY,
            access_token TEXT NOT NULL,
            refresh_token TEXT,
            expires_at TEXT,
            scope TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        ''')
        
        print("✓ Schema created")
        
        # インデックス作成
        c.execute('CREATE INDEX idx_pages_parent_position ON pages(parent_id, position)')
        c.execute('CREATE INDEX idx_blocks_page_position ON blocks(page_id, position)')
        
        # バックアップからデータを復元
        print("📥 Restoring data...")
        
        # pages テーブルを復元（位置情報を修正）
        pages_data = backup_data['tables'].get('pages', [])
        if pages_data:
            for row in pages_data:
                # position と position_new を正規化
                for pos_key in ['position', 'position_new']:
                    if pos_key in row:
                        val = row[pos_key]
                        # 異常な大きさの値をリセット
                        if isinstance(val, (int, float)) and abs(val) > 1e10:
                            row[pos_key] = 0.0
                
                # INSERT
                keys = list(row.keys())
                placeholders = ', '.join(['?' for _ in keys])
                values = [row.get(k) for k in keys]
                c.execute(f"INSERT INTO pages ({','.join(keys)}) VALUES ({placeholders})", values)
            
            print(f"  ✓ pages: {len(pages_data)} rows restored")
        
        # blocks テーブルを復元
        blocks_data = backup_data['tables'].get('blocks', [])
        if blocks_data:
            for row in blocks_data:
                # position を正規化
                if 'position' in row:
                    val = row['position']
                    if isinstance(val, (int, float)) and abs(val) > 1e10:
                        row['position'] = 0.0
                
                keys = list(row.keys())
                placeholders = ', '.join(['?' for _ in keys])
                values = [row.get(k) for k in keys]
                c.execute(f"INSERT INTO blocks ({','.join(keys)}) VALUES ({placeholders})", values)
            
            print(f"  ✓ blocks: {len(blocks_data)} rows restored")
        
        # templates テーブルを復元
        templates_data = backup_data['tables'].get('templates', [])
        if templates_data:
            for row in templates_data:
                keys = list(row.keys())
                placeholders = ', '.join(['?' for _ in keys])
                values = [row.get(k) for k in keys]
                c.execute(f"INSERT INTO templates ({','.join(keys)}) VALUES ({placeholders})", values)
            print(f"  ✓ templates: {len(templates_data)} rows restored")
        
        # users テーブルを復元
        users_data = backup_data['tables'].get('users', [])
        if users_data:
            for row in users_data:
                keys = list(row.keys())
                placeholders = ', '.join(['?' for _ in keys])
                values = [row.get(k) for k in keys]
                c.execute(f"INSERT INTO users ({','.join(keys)}) VALUES ({placeholders})", values)
            print(f"  ✓ users: {len(users_data)} rows restored")
        
        # password_reset_tokens テーブルを復元
        tokens_data = backup_data['tables'].get('password_reset_tokens', [])
        if tokens_data:
            for row in tokens_data:
                keys = list(row.keys())
                placeholders = ', '.join(['?' for _ in keys])
                values = [row.get(k) for k in keys]
                c.execute(f"INSERT INTO password_reset_tokens ({','.join(keys)}) VALUES ({placeholders})", values)
            print(f"  ✓ password_reset_tokens: {len(tokens_data)} rows restored")
        
        # healthplanet_tokens テーブルを復元
        hp_data = backup_data['tables'].get('healthplanet_tokens', [])
        if hp_data:
            for row in hp_data:
                keys = list(row.keys())
                placeholders = ', '.join(['?' for _ in keys])
                values = [row.get(k) for k in keys]
                c.execute(f"INSERT INTO healthplanet_tokens ({','.join(keys)}) VALUES ({placeholders})", values)
            print(f"  ✓ healthplanet_tokens: {len(hp_data)} rows restored")
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Database completely restored from {backup_file.name}")
        print(f"   Pages: {len(pages_data)}")
        print(f"   Blocks: {len(blocks_data)}")
        return True
        
    except Exception as e:
        print(f"❌ Restore failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    import sys
    backup_path = sys.argv[1] if len(sys.argv) > 1 else 'backups/backup_20260213_210129.json'
    restore_safe(backup_path)
