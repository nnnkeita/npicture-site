#!/bin/bash

# 1月30日のバックアップから復元するスクリプト

echo "🔄 Restoring database from 2026-01-30 backup..."

# サーバーから最新バックアップをダウンロード
curl -s https://nnnkeita.pythonanywhere.com/download_db -o /tmp/server_db_jan30.db

if [ ! -f /tmp/server_db_jan30.db ]; then
    echo "❌ Failed to download backup from server"
    exit 1
fi

# ファイルがDBファイルか確認
file /tmp/server_db_jan30.db | grep -q "SQLite"
if [ $? -ne 0 ]; then
    echo "❌ Downloaded file is not a valid SQLite database"
    exit 1
fi

# ローカルのDBをバックアップ
cp /Users/nishiharakeita/npicture-site/notion.db /Users/nishiharakeita/npicture-site/notion.db.backup_restore_$(date +%Y%m%d_%H%M%S)

# サーバーのバックアップでローカルを復元
cp /tmp/server_db_jan30.db /Users/nishiharakeita/npicture-site/notion.db

echo "✅ Database restored from server backup"

# ローカルで新しいバックアップを作成
cd /Users/nishiharakeita/npicture-site
python3 scripts/backup_db.py

if [ $? -eq 0 ]; then
    echo "✅ New backup created successfully"
else
    echo "❌ Failed to create backup"
    exit 1
fi

echo "✅ All done!"
