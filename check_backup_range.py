#!/usr/bin/env python3
import json
from pathlib import Path

# 2月13日のバックアップから2月10-13日のデータを抽出
backup_13 = Path('backups/backup_20260213_210129.json')

with open(backup_13, 'r') as f:
    data13 = json.load(f)

pages13 = data13['tables']['pages']
blocks13 = data13['tables']['blocks']

# 2月10-13日のページを検索
feb10_13_pages = {}
for p in pages13:
    title = p.get('title', '')
    if '2月10日' in title or '2月11日' in title or '2月12日' in title or '2月13日' in title:
        if title not in feb10_13_pages:
            feb10_13_pages[title] = []
        feb10_13_pages[title].append(p.get('id'))

print("📊 2月13日バックアップから2月10-13日のデータ抽出:")
print(f"\n見つかった日記エントリ:")
for date_title in sorted(feb10_13_pages.keys()):
    page_ids = feb10_13_pages[date_title]
    block_count = len([b for b in blocks13 if b.get('page_id') in page_ids])
    print(f"  - {date_title}: {len(page_ids)} pages, {block_count} blocks")

if not feb10_13_pages:
    print("  ❌ 2月10-13日のデータが見つかりません")
else:
    print(f"\n✅ 合計 {len(feb10_13_pages)} 個の日付エントリが見つかりました")
