#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PythonAnywhere の環境確認スクリプト
データベースファイルとアプリケーションの状態を確認
"""
import os
import sys
import sqlite3
from datetime import datetime

def check_environment():
    print("=" * 60)
    print("PythonAnywhere 環境確認")
    print("=" * 60)
    
    # ファイルパスの確認
    db_path = 'notion.db'
    print(f"\n📁 ファイルパス確認:")
    print(f"   Current directory: {os.getcwd()}")
    print(f"   Database path: {db_path}")
    print(f"   Database exists: {os.path.exists(db_path)}")
    
    if os.path.exists(db_path):
        stat = os.stat(db_path)
        mod_time = datetime.fromtimestamp(stat.st_mtime)
        size = stat.st_size / 1024
        print(f"   Size: {size:.1f}KB")
        print(f"   Last modified: {mod_time}")
    
    # データベース内容の確認
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print(f"\n✅ データベース接続成功")
        
        # ページ数の確認
        cursor.execute("SELECT COUNT(*) FROM pages WHERE is_deleted = 0")
        page_count = cursor.fetchone()[0]
        print(f"   Total pages: {page_count}")
        
        # 食事ページ確認
        cursor.execute("SELECT COUNT(*) FROM pages WHERE title LIKE '%食事%' AND is_deleted = 0")
        meal_count = cursor.fetchone()[0]
        print(f"   Meal pages: {meal_count}")
        
        # 日記ページ確認
        cursor.execute("SELECT COUNT(*) FROM pages WHERE title LIKE '%日記%' AND is_deleted = 0")
        diary_count = cursor.fetchone()[0]
        print(f"   Diary pages: {diary_count}")
        
        # 感謝日記確認
        cursor.execute("SELECT COUNT(*) FROM pages WHERE title = '感謝日記' AND is_deleted = 0")
        gratitude_count = cursor.fetchone()[0]
        print(f"   Gratitude pages: {gratitude_count}")
        
        # 最新の月ページ確認
        cursor.execute("SELECT title, id FROM pages WHERE title LIKE '20%年%月' AND is_deleted = 0 ORDER BY title DESC LIMIT 1")
        latest_month = cursor.fetchone()
        if latest_month:
            print(f"\n   Latest month page: {latest_month['title']} (ID: {latest_month['id']})")
            
            # その月のテンプレート子ページを確認
            cursor.execute("""
                SELECT title, icon FROM pages 
                WHERE parent_id = ? AND is_deleted = 0 
                ORDER BY position
            """, (latest_month['id'],))
            children = cursor.fetchall()
            print(f"   Children pages of {latest_month['title']}:")
            for child in children:
                print(f"      - {child['icon']} {child['title']}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ データベースエラー: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("診断完了")
    print("=" * 60)

if __name__ == '__main__':
    check_environment()
