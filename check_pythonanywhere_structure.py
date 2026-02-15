#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PythonAnywhere上の食事ページのparent_idを確認"""
import sqlite3

conn = sqlite3.connect('notion.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 2月4日ページを確認
cursor.execute("SELECT id, title FROM pages WHERE title = '2026年2月4日'")
feb4_page = cursor.fetchone()
if feb4_page:
    print(f"=== 2月4日ページ ===")
    print(f"ID: {feb4_page['id']}, Title: {feb4_page['title']}")
    
    # そのページの子ページ
    cursor.execute("SELECT id, title, icon, parent_id FROM pages WHERE parent_id = ? AND is_deleted = 0", (feb4_page['id'],))
    children = cursor.fetchall()
    print(f"Children pages: {len(children)}")
    for child in children:
        print(f"  - {child['icon']} {child['title']} (ID: {child['id']}, parent_id: {child['parent_id']})")

# 食事ページを直接確認
print(f"\n=== 食事ページ ===")
cursor.execute("SELECT id, title, parent_id FROM pages WHERE title = '食事' LIMIT 5")
meal_pages = cursor.fetchall()
for meal_page in meal_pages:
    print(f"ID: {meal_page['id']}, Title: {meal_page['title']}, parent_id: {meal_page['parent_id']}")

conn.close()
