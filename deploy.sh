#!/bin/bash

# データベースバックアップを作成
echo "📦 Creating database backup..."
python3 scripts/backup_db.py
if [ $? -ne 0 ]; then
    echo "⚠️ Backup failed, but continuing with deployment..."
fi

# 1. 自動でコミットメッセージを作る（日付と時刻）
COMMIT_MSG="Auto update: $(date "+%Y-%m-%d %H:%M:%S")"

# 2. GitHubへ送信
echo "🚀 GitHubへ送信中..."
git add .
git commit -m "$COMMIT_MSG"
git push

# 3. PythonAnywhereの更新トリガーを引く
echo "🔄 サーバーを更新中..."
curl -X POST https://nnnkeita.pythonanywhere.com/webhook_deploy

echo ""
echo "✅ 更新完了！"
