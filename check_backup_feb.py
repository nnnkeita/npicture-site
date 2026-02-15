#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from collections import defaultdict

backup_file = "/Users/nishiharakeita/Downloads/backup_20260213_015735.json"

with open(backup_file, 'r') as f:
    data = json.load(f)

pages = data.get('tables', {}).get('pages', [])

# 日付ごとに集計
date_count = defaultdict(int)
page_by_date = defaultdict(list)

for page in pages:
    created_at = page.get('created_at', '')
    if created_at:
        date_part = created_at[:10]
        date_count[date_part] += 1
        page_by_date[date_part].append({
            'id': page.get('id'),
            'title': page.get('title', '')[:50],
        })

print("📊 バックアップファイル内のデータ（2/08-2/13）：")
print("=" * 60)

target_dates = ['2026-02-08', '2026-02-09', '2026-02-10', 
                '2026-02-11', '2026-02-12', '2026-02-13']

for date in target_dates:
    count = date_count[date]
    print(f"\n{date}: {count} ページ")
    if count > 0:
        for item in page_by_date[date][:5]:
            print(f"  - {item['title']}")
        if len(page_by_date[date]) > 5:
            print(f"  ... and {len(page_by_date[date]) - 5} more")

print(f"\n合計ページ数: {len(pages)}")
