#!/usr/bin/env python3
import json
from pathlib import Path

# 複数のバックアップを確認
backups = [
    'backups/backup_20260213_210129.json',
    'backups/backup_20260214_063936.json',
    'backups/backup_20260208_175217.json',
]

for bak_path in backups:
    bak_file = Path(bak_path)
    if not bak_file.exists():
        print(f"❌ {bak_file.name}: not found")
        continue
    
    with open(bak_file) as f:
        data = json.load(f)
    
    blocks = data['tables'].get('blocks', [])
    
    # ブロックのコンテンツを確認
    content_blocks = [b for b in blocks if b.get('content', '').strip()]
    
    print(f"\n📊 {bak_file.name}")
    print(f"   Total blocks: {len(blocks)}")
    print(f"   Blocks with content: {len(content_blocks)}")
    
    # ブロックコンテンツのサンプル
    if content_blocks:
        for i, block in enumerate(content_blocks[:3]):
            content = block.get('content', '')[:80]
            print(f"     Sample {i+1}: {content}")
