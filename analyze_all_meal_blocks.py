#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全食事ページのカロリーブロック構造を詳しく確認"""
import sqlite3
import json

conn = sqlite3.connect('notion.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# すべての食事ページを取得
cursor.execute("""
    SELECT id, title, parent_id
    FROM pages
    WHERE title = '食事' AND is_deleted = 0
    ORDER BY id
""")

meal_pages = cursor.fetchall()
print(f"食事ページ数: {len(meal_pages)}\n")

total_calorie_blocks = 0
for meal_page in meal_pages:
    meal_id = meal_page['id']
    
    # ブロックを取得
    cursor.execute("""
        SELECT id, type, content, props
        FROM blocks
        WHERE page_id = ?
        ORDER BY position
    """, (meal_id,))
    
    blocks = cursor.fetchall()
    
    print(f"ID {meal_id}: {len(blocks)}ブロック")
    for block in blocks:
        if block['type'] == 'calorie':
            total_calorie_blocks += 1
            if block['props']:
                try:
                    props = json.loads(block['props'])
                    total_kcal = props.get('total_kcal', '-')
                    items_count = len(props.get('items', []))
                    print(f"  calorie: {total_kcal} kcal ({items_count} items)")
                except:
                    print(f"  calorie: (parse error)")
        else:
            content_preview = (block['content'][:20] if block['content'] else '(empty)') .replace('\n', '\\n')
            print(f"  {block['type']}: {content_preview}")

print(f"\n合計カロリーブロック: {total_calorie_blocks}")

conn.close()
