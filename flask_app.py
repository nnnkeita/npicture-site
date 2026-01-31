# -*- coding: utf-8 -*-
"""
メインアプリケーション - Flask アプリケーション初期化

【モジュール分割構成】
- database.py: DB接続とテーブル管理
- utils.py: ユーティリティ関数（カロリー計算、エクスポート/インポート等）
- routes.py: APIエンドポイント定義（40+ルート）

このファイルは Flask アプリケーションの初期化とベースルートのみを管理します。
"""
from flask import Flask, render_template, send_from_directory
import os

from database import init_db, get_or_create_inbox
from routes import register_routes

# === パス設定 ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'templates')
STATIC_FOLDER = os.path.join(BASE_DIR, 'static')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
BACKUP_FOLDER = os.path.join(BASE_DIR, 'backups')

TTS_ENABLED = os.getenv('TTS_ENABLED', '1') == '1'
CALORIE_ENABLED = os.getenv('CALORIE_ENABLED', '1') == '1'

# ディレクトリ作成
for folder in [UPLOAD_FOLDER, BACKUP_FOLDER]:
    try:
        os.makedirs(folder, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create {folder}: {e}")

# === Flask アプリケーション初期化 ===
app = Flask(__name__, template_folder=TEMPLATE_FOLDER, static_folder=STATIC_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# === ページルート ===
@app.route('/')
def index():
    return render_template('index.html', tts_enabled=TTS_ENABLED, calorie_enabled=CALORIE_ENABLED)

@app.route('/inbox')
def inbox_page():
    """あとで調べるページへのショートカットURL"""
    inbox = get_or_create_inbox()
    if inbox:
        return render_template('index.html', inbox_id=inbox['id'], tts_enabled=TTS_ENABLED, calorie_enabled=CALORIE_ENABLED)
    return render_template('index.html', tts_enabled=TTS_ENABLED, calorie_enabled=CALORIE_ENABLED)

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# === APIルート登録 ===
register_routes(app)

# === アプリケーション起動 ===
if __name__ == '__main__':
    import webbrowser
    from threading import Timer
    
    def open_browser():
        webbrowser.open_new('http://127.0.0.1:5000/')
    
    Timer(1, open_browser).start()
    
    with app.app_context():
        init_db()
    app.run(port=5000)
else:
    # PythonAnywhere用のWSGI
    try:
        with app.app_context():
            init_db()
    except Exception as e:
        print(f"Database initialization error: {e}")
        import traceback
        traceback.print_exc()
