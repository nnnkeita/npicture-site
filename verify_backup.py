#!/usr/bin/env python3
import json
from pathlib import Path

# バックアップを詳しく確認
bak_file = Path('backups/backup_20260213_210129.json')
with open(bak_file) as f:
    data = json.load(f)

blocks = data['tables'].get('blocks', [])

# コンテンツの長さを確認
content_stats = {}
for block in blocks:
    page_id = block.get('page_id')
    content = block.get('content', '')
    content_len = len(content.strip())
    
    if page_id not in content_stats:
        content_stats[page_id] = {'count': 0, 'with_content': 0}
    
    content_stats[page_id]['count'] += 1
    if content_len > 0:
        content_stats[page_id]['with_content'] += 1

print("📊 バックアップ内のコンテンツ統計:")
print(f"Total blocks: {len(blocks)}\n")

for page_id in sorted(content_stats.keys())[:15]:
    stats = content_stats[page_id]
    print(f"  Page {page_id}: {stats['count']} blocks, {stats['with_content']} with content")

# コンテンツありのサンプル
print("\n📝 コンテンツシンプル:")
found = 0
for block in blocks:
    if block.get('content', '').strip() and found < 5:
        content = block.get('content', '')[:150]
        print(f"  Block {block.get('id')} (page {block.get('page_id')}): {content}")
        found += 1
