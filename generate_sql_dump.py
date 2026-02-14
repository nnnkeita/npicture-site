#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""バックアップから SQL ダンプを生成 - サーバーで直接実行可能"""

import json
import sys
from pathlib import Path

def generate_sql_dump(backup_file_path, output_sql_path):
    """バックアップJSONから実行可能なSQLダンプを生成"""
    
    backup_file = Path(backup_file_path)
    output_file = Path(output_sql_path)
    
    if not backup_file.exists():
        print(f"❌ Backup file not found: {backup_file}")
        return False
    
    try:
        # バックアップを読み込み
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        # SQL ダンプ生成
        sql_lines = []
        sql_lines.append("-- Database Restore Dump")
        sql_lines.append(f"-- Generated from: {backup_file.name}")
        sql_lines.append(f"-- Timestamp: {backup_data.get('timestamp', 'N/A')}")
        sql_lines.append("")
        sql_lines.append("-- Drop existing tables")
        sql_lines.append("DROP TABLE IF EXISTS blocks;")
        sql_lines.append("DROP TABLE IF EXISTS pages;")
        sql_lines.append("DROP TABLE IF EXISTS templates;")
        sql_lines.append("DROP TABLE IF EXISTS users;")
        sql_lines.append("DROP TABLE IF EXISTS password_reset_tokens;")
        sql_lines.append("DROP TABLE IF EXISTS healthplanet_tokens;")
        sql_lines.append("")
        
        # テーブル作成
        sql_lines.append("-- Create tables")
        sql_lines.append("""
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
);
""")
        
        sql_lines.append("""
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
);
""")
        
        sql_lines.append("""
CREATE TABLE templates (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    icon TEXT DEFAULT '📋',
    description TEXT DEFAULT '',
    content_json TEXT NOT NULL,
    created_at TEXT,
    updated_at TEXT
);
""")
        
        sql_lines.append("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    stripe_customer_id TEXT,
    subscription_status TEXT DEFAULT 'inactive',
    subscription_ends_at TEXT,
    created_at TEXT
);
""")
        
        sql_lines.append("""
CREATE TABLE password_reset_tokens (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    token TEXT NOT NULL UNIQUE,
    expires_at TEXT,
    used INTEGER DEFAULT 0,
    created_at TEXT
);
""")
        
        sql_lines.append("""
CREATE TABLE healthplanet_tokens (
    id INTEGER PRIMARY KEY,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    expires_at TEXT,
    scope TEXT,
    created_at TEXT,
    updated_at TEXT
);
""")
        
        sql_lines.append("-- Create indexes")
        sql_lines.append("CREATE INDEX idx_pages_parent_position ON pages(parent_id, position);")
        sql_lines.append("CREATE INDEX idx_blocks_page_position ON blocks(page_id, position);")
        sql_lines.append("")
        sql_lines.append("-- Insert data")
        sql_lines.append("")
        
        # データ挿入
        table_order = ['users', 'templates', 'pages', 'blocks', 'password_reset_tokens', 'healthplanet_tokens']
        
        for table in table_order:
            rows = backup_data['tables'].get(table, [])
            if not rows:
                continue
            
            sql_lines.append(f"-- {table}: {len(rows)} rows")
            
            for row in rows:
                keys = list(row.keys())
                values = []
                
                for key in keys:
                    val = row[key]
                    if val is None:
                        values.append('NULL')
                    elif isinstance(val, str):
                        # SQL injection 対策: シングルクォートをエスケープ
                        escaped = val.replace("'", "''")
                        values.append(f"'{escaped}'")
                    elif isinstance(val, bool):
                        values.append('1' if val else '0')
                    elif isinstance(val, (int, float)):
                        # 異常に大きな数値をリセット
                        if abs(val) > 1e10:
                            values.append('0')
                        else:
                            values.append(str(val))
                    else:
                        values.append(f"'{val}'")
                
                insert_sql = f"INSERT INTO {table} ({','.join(keys)}) VALUES ({','.join(values)});"
                sql_lines.append(insert_sql)
            
            sql_lines.append("")
        
        # ファイル出力
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sql_lines))
        
        print(f"✅ SQL dump generated: {output_file.name}")
        print(f"   Size: {output_file.stat().st_size / 1024:.1f} KB")
        
        return True
        
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    backup_path = sys.argv[1] if len(sys.argv) > 1 else 'backups/backup_20260213_210129.json'
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'restore.sql'
    generate_sql_dump(backup_path, output_path)
