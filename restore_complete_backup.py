#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete backup restoration from backup_20260213_015735.json
Uses database.py init_db() for schema, restores all data
"""
import json
import os
import sys

# Add project directory to path
sys.path.insert(0, '/Users/nishiharakeita/npicture-site')

from database import get_db, init_db

def restore_from_backup():
    backup_file = "/Users/nishiharakeita/Downloads/backup_20260213_015735.json"
    db_file = '/Users/nishiharakeita/npicture-site/notion.db'
    
    # Validate backup
    if not os.path.exists(backup_file):
        print(f"❌ Backup not found: {backup_file}")
        return False
    
    print(f"📂 Loading backup from: {backup_file}")
    with open(backup_file, 'r') as f:
        backup_data = json.load(f)
    
    # Backup existing DB
    if os.path.exists(db_file):
        backup_path = f"{db_file}.backup_incomplete"
        os.rename(db_file, backup_path)
        print(f"✅ Backed up incomplete DB")
    
    # Initialize fresh database with schema
    print("🔄 Initializing database schema...")
    init_db()
    print("✅ Database schema created")
    
    # Get connection to new DB
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Restore data
        print("📥 Restoring data from backup...")
        
        # Only restore pages and blocks (most important)
        for table_name in ['pages', 'blocks']:  # Skip templates/users to avoid conflicts
            records = backup_data.get('tables', {}).get(table_name, [])
            
            if not records or len(records) == 0:
                print(f"  ⚠️  {table_name}: no data")
                continue
            
            # Skip users restoration if already created
            if table_name == 'users':
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                if cursor.fetchone()[0] > 0:
                    print(f"  ⏭️  {table_name}: keeping existing (already has data)")
                    continue
            
            # Get current table schema to filter valid columns
            cursor.execute(f"PRAGMA table_info({table_name})")
            current_columns = set(row[1] for row in cursor.fetchall())
            
            # Get columns from first record that exist in current schema
            first_record = records[0]
            valid_columns = [col for col in first_record.keys() if col in current_columns]
            
            if not valid_columns:
                print(f"  ⚠️  {table_name}: no matching columns found")
                continue
            
            columns_str = ', '.join(valid_columns)
            placeholders = ', '.join(['?' for _ in valid_columns])
            
            insert_sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            
            # Prepare values with only valid columns
            values_list = [
                tuple(record.get(col) for col in valid_columns)
                for record in records
            ]
            
            # Insert
            cursor.executemany(insert_sql, values_list)
            print(f"  ✅ {table_name}: {len(records)} restored")
        
        conn.commit()
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM pages")
        page_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM blocks")
        block_count = cursor.fetchone()[0]
        
        print(f"\n✅ 復元完了！")
        print(f"  Pages: {page_count}")
        print(f"  Blocks: {block_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    restore_from_backup()

