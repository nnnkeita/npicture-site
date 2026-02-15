#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""食事ブロックの完全な構造を確認"""
import sqlite3
import json

conn = sqlite3.connect('notion.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 最初の食事ページを取得
cursor.execute("""
    SELECT id, title, parent_id, icon 
    FROM pages 
    WHERE title = '食事' AND is_deleted = 0 
    LIMIT 1
""")
meal_page = cursor.fetchone()

if meal_page:
    meal_id = meal_page['id']
    print(f"=== {meal_page['title']} (ID: {meal_id}) ===\n")
    
    # ブロック詳細を取得
    cursor.execute("""
        SELECT id, type, content, checked, position, collapsed, details, props
        FROM blocks 
        WHERE page_id = ?
        ORDER BY position
    """, (meal_id,))
    
    blocks = cursor.fetchall()
    print(f"ブロック数: {len(blocks)}\n")
    
    for i, block in enumerate(blocks, 1):
        print(f"ブロック {i}:")
        print(f"  ID: {block['id']}")
        print(f"  Type: {block['type']}")
        print(f"  Position: {block['position']}")
        print(f"  Checked: {block['checked']}")
        print(f"  Collapsed: {block['collapsed']}")
        print(f"  Content: {block['content'][:100] if block['content'] else '(empty)'}")
        print(f"  Details: {block['details'][:100] if block['details'] else '(empty)'}")
        print(f"  Props: {block['props']}")
        print()

conn.close()
