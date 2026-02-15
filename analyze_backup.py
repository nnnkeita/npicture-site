#!/usr/bin/env python3
import json
from pathlib import Path

# バックアップを詳細分析
bak_file = Path('backups/backup_20260213_210129.json')
with open(bak_file) as f:
    data = json.load(f)

pages = data['tables'].get('pages', [])
blocks = data['tables'].get('blocks', [])

# ページの日付分析
print("📅 バックアップ内のページ分析:")
print(f"Total pages: {len(pages)}\n")

pages_by_date = {}
for page in pages:
    title = page.get('title', '')
    # タイトルから日付を抽出
    if '年' in title:
        pages_by_date[title] = {
            'id': page.get('id'),
            'created_at': page.get('created_at', ''),
            'blocks': 0
        }

# ページの日付順でソート
print("ページ一覧:")
for title in sorted(pages_by_date.keys()):
    print(f"  {title} (id: {pages_by_date[title]['id']})")

# ブロック数をページIDでカウント
print("\n📊 ブロック数:")
page_block_count = {}
for block in blocks:
    pid = block.get('page_id')
    page_block_count[pid] = page_block_count.get(pid, 0) + 1

for title in sorted(pages_by_date.keys()):
    pid = pages_by_date[title]['id']
    count = page_block_count.get(pid, 0)
    pages_by_date[title]['blocks'] = count
    print(f"  {title}: {count} blocks")

# 2月5-11日を確認
print("\n❓ 2月5-11日のページが存在するか:")
for i in range(5, 12):
    search_title = f"2026年2月{i}日"
    found = search_title in pages_by_date
    print(f"  {search_title}: {'✓ YES' if found else '❌ NO'}")
