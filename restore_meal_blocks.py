#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PythonAnywhere用：食事ブロックを復元するスクリプト
meal_blocks_export.json から食事ページとブロックを復元
"""
import sqlite3
import json
import os

def restore_meal_blocks_from_json(db_path='notion.db', json_path='meal_blocks_export.json'):
    """JSONから食事ブロックを復元"""
    
    if not os.path.exists(json_path):
        print(f"❌ {json_path} が見つかりません")
        return False
    
    # JSONを読み込み
    with open(json_path, 'r', encoding='utf-8') as f:
        meal_data = json.load(f)
    
    print(f"📄 {json_path} から食事データを読み込み中...")
    print(f"   ページ: {len(meal_data['meal_pages'])}")
    print(f"   ブロック: {len(meal_data['meal_blocks'])}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # IDマッピング（オリジナルID -> 新しいID）
    id_map = {}
    
    try:
        # 食事ページを復元
        for page_info in meal_data['meal_pages']:
            original_id = page_info['original_id']
            title = page_info['title']
            parent_id = page_info['parent_id']
            icon = page_info['icon']
            position = page_info['position']
            
            # 既に存在するか確認
            cursor.execute(
                "SELECT id FROM pages WHERE title = ? AND parent_id = ? AND icon = ?",
                (title, parent_id, icon)
            )
            existing = cursor.fetchone()
            
            if existing:
                new_id = existing[0]
                print(f"  既存: {title} (ID: {new_id})")
            else:
                # 新規作成
                cursor.execute(
                    """INSERT INTO pages (title, parent_id, icon, position, is_deleted)
                       VALUES (?, ?, ?, ?, 0)""",
                    (title, parent_id, icon, position)
                )
                new_id = cursor.lastrowid
                print(f"  ✅ 復元: {title} (新ID: {new_id})")
            
            id_map[original_id] = new_id
        
        # ブロックを復元
        for block_info in meal_data['meal_blocks']:
            original_page_id = block_info['original_page_id']
            new_page_id = id_map.get(original_page_id)
            
            if not new_page_id:
                print(f"  ⚠️  ページID {original_page_id} のマッピングなし")
                continue
            
            # 既に存在するか確認
            cursor.execute(
                "SELECT id FROM blocks WHERE page_id = ? AND type = ? AND position = ?",
                (new_page_id, block_info['type'], block_info['position'])
            )
            existing = cursor.fetchone()
            
            if not existing:
                cursor.execute(
                    """INSERT INTO blocks 
                       (page_id, type, content, checked, position, collapsed, details, props)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        new_page_id,
                        block_info['type'],
                        block_info['content'],
                        block_info['checked'],
                        block_info['position'],
                        block_info['collapsed'],
                        block_info['details'],
                        block_info['props']
                    )
                )
        
        conn.commit()
        print("\n✅ 食事ブロックの復元が完了しました！")
        return True
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    restore_meal_blocks_from_json()
