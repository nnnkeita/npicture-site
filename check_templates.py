#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""テンプレート機能の確認スクリプト"""
import sqlite3

conn = sqlite3.connect('notion.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 食事ページを検索
cursor.execute("SELECT id, title, icon FROM pages WHERE title LIKE '%食事%' LIMIT 5")
meal_pages = cursor.fetchall()
print("=== 食事ページ ===")
for page in meal_pages:
    print(f"ID: {page['id']}, Title: {page['title']}, Icon: {page['icon']}")

# 日記ページを検索
cursor.execute("SELECT id, title, icon FROM pages WHERE title LIKE '%日記%' LIMIT 10")
diary_pages = cursor.fetchall()
print("\n=== 日記ページ ===")
for page in diary_pages:
    print(f"ID: {page['id']}, Title: {page['title']}, Icon: {page['icon']}")

# 感謝日記テンプレートを検索
cursor.execute("SELECT id, title, icon FROM pages WHERE title = '感謝日記'")
gratitude_pages = cursor.fetchall()
print("\n=== 感謝日記ページ ===")
for page in gratitude_pages:
    print(f"ID: {page['id']}, Title: {page['title']}, Icon: {page['icon']}")
    cursor.execute("SELECT type, content FROM blocks WHERE page_id = ? ORDER BY position", (page['id'],))
    blocks = cursor.fetchall()
    for block in blocks[:5]:
        content = block['content'][:50] if block['content'] else '(empty)'
        print(f"  - {block['type']}: {content}")

# 最新の月ページを検索
cursor.execute("SELECT id, title, icon, parent_id FROM pages WHERE title LIKE '20%年%月' ORDER BY title DESC LIMIT 1")
latest_month = cursor.fetchone()
if latest_month:
    print(f"\n=== 最新の月ページ: {latest_month['title']} ===")
    month_id = latest_month['id']
    
    # その月の子ページ
    cursor.execute("SELECT id, title, icon FROM pages WHERE parent_id = ? AND is_deleted = 0 ORDER BY position", (month_id,))
    children = cursor.fetchall()
    for child in children:
        print(f"  - {child['icon']} {child['title']}")
        
        # その子ページのブロック
        cursor.execute("SELECT type, content FROM blocks WHERE page_id = ? ORDER BY position LIMIT 3", (child['id'],))
        blocks = cursor.fetchall()
        for block in blocks:
            content = block['content'][:40] if block['content'] else '(empty)'
            print(f"      {block['type']}: {content}")

conn.close()
