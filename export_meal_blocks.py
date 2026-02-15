#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""食事ページと関連ブロックをJSONで抽出"""
import sqlite3
import json

conn = sqlite3.connect('notion.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 全食事ページを取得
cursor.execute("""
    SELECT id, title, parent_id, icon, position, created_at, updated_at
    FROM pages 
    WHERE title = '食事' AND is_deleted = 0
    ORDER BY created_at
""")
meal_pages = cursor.fetchall()

meal_data = {
    'meal_pages': [],
    'meal_blocks': []
}

print(f"食事ページ数: {len(meal_pages)}")

for meal_page in meal_pages:
    page_id = meal_page['id']
    
    # ページ情報をJSONに追加
    page_info = {
        'original_id': page_id,
        'title': meal_page['title'],
        'parent_id': meal_page['parent_id'],
        'icon': meal_page['icon'],
        'position': meal_page['position'],
        'created_at': meal_page['created_at'],
        'updated_at': meal_page['updated_at']
    }
    meal_data['meal_pages'].append(page_info)
    
    # このページのブロックを取得
    cursor.execute("""
        SELECT id, type, content, checked, position, collapsed, details, props
        FROM blocks 
        WHERE page_id = ?
        ORDER BY position
    """, (page_id,))
    blocks = cursor.fetchall()
    
    print(f"  {meal_page['title']} (ID: {page_id}): {len(blocks)}個のブロック")
    
    for block in blocks:
        block_info = {
            'original_page_id': page_id,
            'type': block['type'],
            'content': block['content'],
            'checked': block['checked'],
            'position': block['position'],
            'collapsed': block['collapsed'],
            'details': block['details'],
            'props': block['props']
        }
        meal_data['meal_blocks'].append(block_info)

# JSONをファイルに保存
with open('meal_blocks_export.json', 'w', encoding='utf-8') as f:
    json.dump(meal_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ 食事データをmeal_blocks_export.jsonにエクスポートしました")
print(f"   ページ数: {len(meal_data['meal_pages'])}")
print(f"   ブロック数: {len(meal_data['meal_blocks'])}")

conn.close()
