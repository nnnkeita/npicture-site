#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データベースを JSON テキスト形式でバックアップするスクリプト
"""

import sqlite3
import json
import os
import sys
from datetime import datetime
from pathlib import Path

def backup_database():
    """データベースをJSONテキストにエクスポート"""
    
    # パス設定
    base_dir = Path(__file__).parent.parent
    db_path = base_dir / 'notion.db'
    backup_dir = base_dir / 'backups'
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return False
    
    # バックアップディレクトリ作成
    backup_dir.mkdir(exist_ok=True)
    
    try:
        # データベース接続
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # テーブル一覧取得（FTSテーブルを除外）
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            AND name NOT LIKE 'sqlite_%'
            AND name NOT LIKE '%_fts%'
            AND name NOT LIKE '%_config'
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        # バックアップデータ
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'database': 'notion.db',
            'tables': {}
        }
        
        # 各テーブルをエクスポート
        for table in tables:
            cursor.execute(f'SELECT * FROM {table}')
            rows = cursor.fetchall()
            backup_data['tables'][table] = [dict(row) for row in rows]
            print(f"  ✓ {table}: {len(rows)} rows")
        
        conn.close()
        
        # JSONファイルに保存
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = backup_dir / f'backup_{timestamp}.json'
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Backup created: {backup_file}")
        print(f"   Size: {backup_file.stat().st_size / 1024:.1f} KB")
        
        # 最新のバックアップを latest.json にコピー
        latest_file = backup_dir / 'latest.json'
        with open(latest_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        print(f"✅ Latest backup updated: {latest_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🔄 Creating database backup...")
    success = backup_database()
    sys.exit(0 if success else 1)
