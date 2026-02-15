#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""食事ブロックの詳細構造を確認"""
import sqlite3

conn = sqlite3.connect('notion.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 食事ページを検索
cursor.execute("SELECT id, title, parent_id, icon, position FROM pages WHERE title = '食事' AND is_deleted = 0 LIMIT 1")
meal_page = cursor.fetchone()

if meal_page:
    meal_id = meal_page['id']
    print(f"=== 食事ページ ===")
    print(f"ID: {meal_id}")
    print(f"Title: {meal_page['title']}")
    print(f"Parent ID: {meal_page['parent_id']}")
    print(f"Icon: {meal_page['icon']}")
    print(f"Position: {meal_page['position']}")
    
    # その食事ページのブロックを取得
    cursor.execute("SELECT id, type, content, position FROM blocks WHERE page_id = ? ORDER BY position", (meal_id,))
    blocks = cursor.fetchall()
    
    print(f"\n=== ブロック ({len(blocks)}個) ===")
    for block in blocks:
        content = block['content'][:60] if block['content'] else '(empty)'
        print(f"  [{block['type']}] pos={block['position']}: {content}")
    
    # 親ページの情報も取得
    parent_id = meal_page['parent_id']
    if parent_id:
        cursor.execute("SELECT id, title FROM pages WHERE id = ?", (parent_id,))
        parent = cursor.fetchone()
        if parent:
            print(f"\n=== 親ページ ===")
            print(f"ID: {parent['id']}, Title: {parent['title']}")
else:
    print("食事ページが見つかりません")

conn.close()
