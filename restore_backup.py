#!/usr/bin/env python3
import sqlite3, json
from pathlib import Path

db = Path('notion.db')
bak = Path('backups/backup_20260213_210129.json')
old_db = db.with_suffix('.db.old')

# 古いDBをバックアップ
if db.exists():
    db.rename(old_db)
    print(f"✓ Old DB saved to {old_db.name}")

# JSON読み込み
with open(bak) as f:
    data = json.load(f)

# 新DBに復元
conn = sqlite3.connect(str(db))
c = conn.cursor()

# 各テーブル復元
for tbl, rows in data['tables'].items():
    if not rows:
        print(f"✓ {tbl}: 0 rows")
        continue
    
    # スキーマを自動生成
    first_row = rows[0]
    cols = list(first_row.keys())
    
    # テーブル作成
    col_defs = ', '.join([f'{col} TEXT' for col in cols])
    c.execute(f'CREATE TABLE IF NOT EXISTS {tbl} ({col_defs})')
    
    # IDカラムが存在すればPRIMARY KEYに変更
    if 'id' in cols:
        c.execute(f'DROP TABLE IF EXISTS {tbl}')
        col_defs = 'id INTEGER PRIMARY KEY, ' + ', '.join([f'{col} TEXT' for col in cols if col != 'id'])
        c.execute(f'CREATE TABLE {tbl} ({col_defs})')
    
    # データ挿入
    for row in rows:
        placeholders = ', '.join(['?' for _ in cols])
        c.execute(f"INSERT INTO {tbl} ({','.join(cols)}) VALUES ({placeholders})", [row.get(col) for col in cols])
    
    print(f"✓ {tbl}: {len(rows)} rows")

conn.commit()
conn.close()
print("✅ Restored!")
