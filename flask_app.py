# -*- coding: utf-8 -*-
"""
メインアプリケーション - Flask アプリケーション初期化

【モジュール分割構成】
- database.py: DB接続とテーブル管理
- utils.py: ユーティリティ関数（カロリー計算、エクスポート/インポート等）
- routes.py: APIエンドポイント定義（40+ルート）

このファイルは Flask アプリケーションの初期化とベースルートのみを管理します。
"""
from flask import Flask, render_template, send_from_directory, request, redirect, session, url_for, jsonify
import os
import secrets
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
import stripe
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import requests  # API通信用
import urllib.parse # URLエンコード用

from database import (
    init_db, get_or_create_inbox, get_or_create_finished, get_user_count, get_user_by_username, create_user,
    get_user_by_id, update_user_password, set_password_reset_token, get_password_reset_token,
    mark_password_reset_token_used, update_user_stripe_customer, update_user_subscription,
    get_user_by_stripe_customer
)

from routes import register_routes
from backup_scheduler import init_backup_scheduler

# === パス設定 ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'templates')
STATIC_FOLDER = os.path.join(BASE_DIR, 'static')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
BACKUP_FOLDER = os.path.join(BASE_DIR, 'backups')

# .envファイルを読み込み
load_dotenv(os.path.join(BASE_DIR, '.env'))

# === 設定値の定義 ===
TTS_ENABLED = os.getenv('TTS_ENABLED', '1') == '1'
CALORIE_ENABLED = os.getenv('CALORIE_ENABLED', '1') == '1'
AUTH_ENABLED = False  # ログイン認証を完全に無効化
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')
STRIPE_PRICE_ID = os.getenv('STRIPE_PRICE_ID', '')
APP_BASE_URL = os.getenv('APP_BASE_URL', 'http://127.0.0.1:5000')
STRIPE_SUCCESS_URL = os.getenv('STRIPE_SUCCESS_URL', f'{APP_BASE_URL}/billing?success=1')
STRIPE_CANCEL_URL = os.getenv('STRIPE_CANCEL_URL', f'{APP_BASE_URL}/billing?canceled=1')

SMTP_HOST = os.getenv('SMTP_HOST', '')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
SMTP_FROM = os.getenv('SMTP_FROM', SMTP_USER)

# --- Health Planet (Tanita) API 設定 ---
TANITA_CLIENT_ID = os.getenv('TANITA_CLIENT_ID', '')
TANITA_CLIENT_SECRET = os.getenv('TANITA_CLIENT_SECRET', '')
TANITA_REDIRECT_URI = os.getenv('TANITA_REDIRECT_URI', f'{APP_BASE_URL}/tanita/callback')
TANITA_AUTH_URL = 'https://www.healthplanet.jp/oauth/auth'
TANITA_TOKEN_URL = 'https://www.healthplanet.jp/oauth/token'
TANITA_DATA_URL = 'https://www.healthplanet.jp/status/innerscan.json'

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
secret = os.getenv('APP_SECRET')
if not secret:
    print('Warning: APP_SECRET is not set. Set APP_SECRET for production use.')
    secret = os.urandom(24)
app.secret_key = secret

if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

# === バックアップスケジューラー初期化 ===
init_backup_scheduler(app)

# === データベース復元関数（本番環境用） ===
def _restore_db_from_dump_if_needed():
    """DBが空の場合、SQLダンプから復元"""
    import sqlite3
    db_path = 'notion.db'
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pages'")
        pages_exists = cursor.fetchone() is not None
        conn.close()
        
        if not pages_exists:
            print("[INFO] Database tables not found. Restoring from SQL dump...")
            dump_path = os.path.join(BASE_DIR, 'notion_dump.sql')
            if os.path.exists(dump_path):
                conn = sqlite3.connect(db_path)
                with open(dump_path, 'r', encoding='utf-8') as f:
                    sql_script = f.read()
                    conn.executescript(sql_script)
                conn.commit()
                conn.close()
                print("[INFO] Database restored successfully from notion_dump.sql")
    except Exception as e:
        print(f"[WARNING] Failed to restore DB from dump: {e}")

def _restore_meal_blocks_if_needed():
    """食事ブロックが存在しない場合、JSONから復元"""
    import sqlite3
    import json
    db_path = 'notion.db'
    json_path = os.path.join(BASE_DIR, 'meal_blocks_export.json')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 食事ページの数を確認
        cursor.execute("SELECT COUNT(*) FROM pages WHERE title = '食事' AND is_deleted = 0")
        meal_count = cursor.fetchone()[0]
        conn.close()
        
        if meal_count == 0 and os.path.exists(json_path):
            print("[INFO] No meal pages found. Restoring from meal_blocks_export.json...")
            
            with open(json_path, 'r', encoding='utf-8') as f:
                meal_data = json.load(f)
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            id_map = {}
            
            # 食事ページを復元
            for page_info in meal_data['meal_pages']:
                original_id = page_info['original_id']
                title = page_info['title']
                parent_id = page_info['parent_id']
                icon = page_info['icon']
                position = page_info['position']
                
                # 既に存在するか確認
                cursor.execute(
                    "SELECT id FROM pages WHERE title = ? AND parent_id = ? AND icon = ?",
                    (title, parent_id, icon)
                )
                existing = cursor.fetchone()
                
                if existing:
                    new_id = existing[0]
                else:
                    cursor.execute(
                        "INSERT INTO pages (title, parent_id, icon, position, is_deleted) VALUES (?, ?, ?, ?, 0)",
                        (title, parent_id, icon, position)
                    )
                    new_id = cursor.lastrowid
                
                id_map[original_id] = new_id
            
            # ブロックを復元
            for block_info in meal_data['meal_blocks']:
                original_page_id = block_info['original_page_id']
                new_page_id = id_map.get(original_page_id)
                
                if new_page_id:
                    cursor.execute(
                        "SELECT id FROM blocks WHERE page_id = ? AND type = ? AND position = ?",
                        (new_page_id, block_info['type'], block_info['position'])
                    )
                    if not cursor.fetchone():
                        cursor.execute(
                            "INSERT INTO blocks (page_id, type, content, checked, position, collapsed, details, props) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (
                                new_page_id,
                                block_info['type'],
                                block_info['content'],
                                block_info['checked'],
                                block_info['position'],
                                block_info['collapsed'],
                                block_info['details'],
                                block_info['props']
                            )
                        )
            
            conn.commit()
            conn.close()
            print(f"[INFO] Restored {len(meal_data['meal_pages'])} meal pages and {len(meal_data['meal_blocks'])} blocks")
    except Exception as e:
        print(f"[WARNING] Failed to restore meal blocks: {e}")

# === 課金判定 ===
def _is_subscription_active(user):
    if not user:
        return False
    status = user.get('subscription_status') or 'inactive'
    ends_at = user.get('subscription_ends_at')
    now = datetime.utcnow()
    if status == 'active':
        if ends_at:
            try:
                if datetime.fromisoformat(ends_at) < now:
                    return False
            except Exception:
                pass
        return True
    if status == 'trialing':
        if ends_at:
            try:
                return datetime.fromisoformat(ends_at) > now
            except Exception:
                return False
        return False
    return False

# === 認証ガード ===
@app.before_request
def require_login():
    if not AUTH_ENABLED:
        return
    if request.path.startswith('/static/'):
        return
    if request.endpoint is None:
        return
    public_endpoints = {
        'login',
        'setup',
        'webhook_deploy',
        'stripe_webhook',
        'reset_password',
        'forgot_password',
        'terms',
        'privacy',
        'tokusho',
        'tanita_callback' 
    }
    if request.endpoint in public_endpoints:
        return
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    subscription_exempt = public_endpoints | {
        'billing',
        'billing_checkout',
        'billing_portal',
        'logout'
    }
    if request.endpoint in subscription_exempt:
        return
    
    user = get_user_by_id(session.get('user_id'))
    user = dict(user) if user else None
    if not _is_subscription_active(user):
        return redirect(url_for('billing'))


# === ページルート ===
@app.route('/')
def index():
    return render_template('index.html', tts_enabled=TTS_ENABLED, calorie_enabled=CALORIE_ENABLED, current_user=session.get('username'))

@app.route('/inbox')
def inbox_page():
    inbox = get_or_create_inbox()
    if inbox:
        return render_template('index.html', inbox_id=inbox['id'], tts_enabled=TTS_ENABLED, calorie_enabled=CALORIE_ENABLED, current_user=session.get('username'))
    return render_template('index.html', tts_enabled=TTS_ENABLED, calorie_enabled=CALORIE_ENABLED, current_user=session.get('username'))

@app.route('/finished')
def finished_page():
    finished = get_or_create_finished()
    if finished:
        return render_template('index.html', finished_id=finished['id'], tts_enabled=TTS_ENABLED, calorie_enabled=CALORIE_ENABLED, current_user=session.get('username'))
    return render_template('index.html', tts_enabled=TTS_ENABLED, calorie_enabled=CALORIE_ENABLED, current_user=session.get('username'))

@app.route('/chat')
def chat_page():
    return render_template('chat.html', current_user=session.get('username'))

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if get_user_count() == 0:
        return redirect(url_for('setup'))
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''
        user = get_user_by_username(username)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index'))
        return render_template('login.html', error='ユーザー名またはパスワードが違います。')
    return render_template('login.html')

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if get_user_count() > 0:
        return redirect(url_for('login'))
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''
        password_confirm = request.form.get('password_confirm') or ''
        if not username or not password:
            return render_template('setup.html', error='ユーザー名とパスワードを入力してください。')
        if password != password_confirm:
            return render_template('setup.html', error='パスワードが一致しません。')
        password_hash = generate_password_hash(password)
        user_id = create_user(username, password_hash)
        trial_ends = (datetime.utcnow() + timedelta(days=14)).isoformat()
        update_user_subscription(user_id, 'trialing', trial_ends)
        user = get_user_by_username(username)
        session['user_id'] = user['id']
        session['username'] = user['username']
        return redirect(url_for('index'))
    return render_template('setup.html')

@app.route('/forgot', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        user = get_user_by_username(username)
        if user:
            token = secrets.token_urlsafe(32)
            expires_at = (datetime.utcnow() + timedelta(hours=1)).isoformat()
            set_password_reset_token(user['id'], token, expires_at)
            reset_link = f"{APP_BASE_URL}/reset/{token}"
            if SMTP_HOST and SMTP_FROM:
                msg = EmailMessage()
                msg['Subject'] = 'パスワード再設定'
                msg['From'] = SMTP_FROM
                msg['To'] = user['username'] if '@' in user['username'] else SMTP_FROM
                msg.set_content(f"以下のリンクからパスワードを再設定してください。\n{reset_link}\n\n有効期限: 1時間")
                try:
                    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                        server.starttls()
                        if SMTP_USER:
                            server.login(SMTP_USER, SMTP_PASSWORD)
                        server.send_message(msg)
                except Exception:
                    return render_template('forgot.html', error='メール送信に失敗しました。', debug_link=reset_link)
            return render_template('forgot.html', success='再設定リンクを送信しました。', debug_link=reset_link)
        return render_template('forgot.html', success='再設定リンクを送信しました。')
    return render_template('forgot.html')

@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    token_row = get_password_reset_token(token)
    if not token_row:
        return render_template('reset.html', error='無効なリンクです。')
    if token_row['used']:
        return render_template('reset.html', error='このリンクは使用済みです。')
    if datetime.fromisoformat(token_row['expires_at']) < datetime.utcnow():
        return render_template('reset.html', error='リンクの有効期限が切れています。')
    if request.method == 'POST':
        password = request.form.get('password') or ''
        password_confirm = request.form.get('password_confirm') or ''
        if not password:
            return render_template('reset.html', error='パスワードを入力してください。')
        if password != password_confirm:
            return render_template('reset.html', error='パスワードが一致しません。')
        update_user_password(token_row['user_id'], generate_password_hash(password))
        mark_password_reset_token_used(token)
        return redirect(url_for('login'))
    return render_template('reset.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/tokusho')
def tokusho():
    return render_template('tokusho.html')

@app.route('/billing')
def billing():
    user = get_user_by_id(session.get('user_id')) if session.get('user_id') else None
    user = dict(user) if user else None
    status = user['subscription_status'] if user else 'inactive'
    return render_template('billing.html', status=status)

@app.route('/billing/checkout')
def billing_checkout():
    if not STRIPE_SECRET_KEY or not STRIPE_PRICE_ID:
        return render_template('billing.html', status='inactive', error='Stripe設定が未完了です。')
    user = get_user_by_id(session.get('user_id'))
    user = dict(user) if user else None
    if not user:
        return redirect(url_for('login'))
    customer_id = user.get('stripe_customer_id')
    if not customer_id:
        customer = stripe.Customer.create()
        customer_id = customer['id']
        update_user_stripe_customer(user['id'], customer_id)
    session_obj = stripe.checkout.Session.create(
        mode='subscription',
        customer=customer_id,
        line_items=[{'price': STRIPE_PRICE_ID, 'quantity': 1}],
        success_url=STRIPE_SUCCESS_URL,
        cancel_url=STRIPE_CANCEL_URL
    )
    return redirect(session_obj.url)

@app.route('/billing/portal')
def billing_portal():
    if not STRIPE_SECRET_KEY:
        return redirect(url_for('billing'))
    user = get_user_by_id(session.get('user_id'))
    user = dict(user) if user else None
    if not user or not user.get('stripe_customer_id'):
        return redirect(url_for('billing'))
    portal = stripe.billing_portal.Session.create(
        customer=user['stripe_customer_id'],
        return_url=f'{APP_BASE_URL}/billing'
    )
    return redirect(portal.url)

@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        if STRIPE_WEBHOOK_SECRET:
            event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
        else:
            event = request.get_json() or {}
    except stripe.error.SignatureVerificationError as e:
        import sys
        print(f"[WEBHOOK] Signature verification failed (development): {e}", file=sys.stderr, flush=True)
        import json
        try:
            event = json.loads(payload)
        except:
            return jsonify({'error': 'Invalid JSON payload'}), 400
    except Exception as e:
        import sys
        print(f"[WEBHOOK] Unexpected error: {e}", file=sys.stderr, flush=True)
        return jsonify({'error': 'Webhook processing error'}), 400

    event_type = event.get('type')
    data = event.get('data', {}).get('object', {})
    
    import sys
    print(f"[WEBHOOK] Event type: {event_type}, customer: {data.get('customer', 'N/A')}", file=sys.stderr, flush=True)

    if event_type in ['checkout.session.completed']:
        customer_id = data.get('customer')
        if customer_id:
            user = get_user_by_stripe_customer(customer_id)
            if user:
                update_user_subscription(user['id'], 'active', None)

    if event_type in ['customer.subscription.updated', 'customer.subscription.created']:
        customer_id = data.get('customer')
        status = data.get('status')
        period_end = data.get('current_period_end')
        ends_at = datetime.utcfromtimestamp(period_end).isoformat() if period_end else None
        if customer_id:
            user = get_user_by_stripe_customer(customer_id)
            if user:
                update_user_subscription(user['id'], status, ends_at)

    if event_type in ['customer.subscription.deleted']:
        customer_id = data.get('customer')
        if customer_id:
            user = get_user_by_stripe_customer(customer_id)
            if user:
                update_user_subscription(user['id'], 'canceled', None)

    return jsonify({'received': True})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# === Health Planet (Tanita) Integration Routes ===

@app.route('/tanita/login')
def tanita_login():
    """タニタの認証ページへリダイレクト"""
    if not TANITA_CLIENT_ID:
        # 環境変数が読み込めていない場合のデバッグ表示
        print("Error: TANITA_CLIENT_ID is missing.")
        return "タニタAPIのClient IDが設定されていません。.envを確認して再起動してください。", 500
    
    # URLエンコードを確実に行うためのパラメータ作成
    params = {
        'client_id': TANITA_CLIENT_ID,
        'redirect_uri': TANITA_REDIRECT_URI,
        'scope': 'innerscan',
        'response_type': 'code'
    }
    
    # 辞書からクエリパラメータ文字列を生成 (例: client_id=...&redirect_uri=http%3A%2F%2F...)
    # これにより : や / が正しく %xx に変換されます
    auth_query = urllib.parse.urlencode(params)
    
    # デバッグ用にコンソールにURLを表示
    full_url = f"{TANITA_AUTH_URL}?{auth_query}"
    print(f"--- Redirecting to Tanita ---")
    print(full_url)
    print(f"-----------------------------")

    return redirect(full_url)

@app.route('/tanita/callback')
def tanita_callback():
    """タニタからのコールバックを受け取りトークンを取得"""
    code = request.args.get('code')
    if not code:
        return "認証エラー: コードがありません", 400

    # トークン交換リクエスト
    payload = {
        'client_id': TANITA_CLIENT_ID,
        'client_secret': TANITA_CLIENT_SECRET,
        'redirect_uri': TANITA_REDIRECT_URI,
        'code': code,
        'grant_type': 'authorization_code'
    }
    
    try:
        response = requests.post(TANITA_TOKEN_URL, data=payload)
        response.raise_for_status()
        token_data = response.json()
        
        session['tanita_access_token'] = token_data.get('access_token')
        
        return redirect(url_for('get_weight_data'))
        
    except requests.exceptions.RequestException as e:
        return f"トークン取得エラー: {e} - レスポンス: {response.text}", 400

@app.route('/tanita/data')
def get_weight_data():
    """保存されたトークンを使ってデータを取得"""
    access_token = session.get('tanita_access_token')
    if not access_token:
        return redirect(url_for('tanita_login'))

    params = {
        'access_token': access_token,
        'date': 1,
        'tag': '6021,6022'
    }
    
    try:
        response = requests.get(TANITA_DATA_URL, params=params)
        response.raise_for_status()
        data = response.json()
        return jsonify(data)
        
    except requests.exceptions.RequestException as e:
        return f"データ取得エラー: {e}", 400

# === 診断エンドポイント ===
@app.route('/api/diagnose')
def diagnose_database():
    """データベースの状態を診断"""
    import sqlite3
    from datetime import datetime
    
    result = {}
    
    # ファイル情報
    db_path = 'notion.db'
    if os.path.exists(db_path):
        stat = os.stat(db_path)
        result['db_size_kb'] = stat.st_size / 1024
        result['db_modified'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
    
    # データベース接続と確認
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM pages WHERE is_deleted = 0")
        result['total_pages'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM pages WHERE title LIKE '%食事%' AND is_deleted = 0")
        result['meal_pages'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM pages WHERE title LIKE '%日記%' AND is_deleted = 0")
        result['diary_pages'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM pages WHERE title = '感謝日記' AND is_deleted = 0")
        result['gratitude_pages'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT title, id FROM pages WHERE title LIKE '20%年%月' AND is_deleted = 0 ORDER BY title DESC LIMIT 1")
        latest_month = cursor.fetchone()
        if latest_month:
            result['latest_month_title'] = latest_month['title']
            result['latest_month_id'] = latest_month['id']
            
            cursor.execute("""
                SELECT title, icon FROM pages 
                WHERE parent_id = ? AND is_deleted = 0 
                ORDER BY position
            """, (latest_month['id'],))
            children = cursor.fetchall()
            result['month_children'] = [{'title': c['title'], 'icon': c['icon']} for c in children]
        
        cursor.execute("SELECT COUNT(*) FROM blocks")
        result['total_blocks'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users")
        result['total_users'] = cursor.fetchone()[0]
        
        conn.close()
        result['status'] = 'ok'
        
    except Exception as e:
        result['status'] = 'error'
        result['error'] = str(e)
        import traceback
        result['traceback'] = traceback.format_exc()
    
    return jsonify(result)

# === APIルート登録 ===
register_routes(app)

# === アプリケーション起動 ===
if __name__ == '__main__':
    # ローカル開発用
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
            _restore_db_from_dump_if_needed()
            _restore_meal_blocks_if_needed()
            init_db()
    except Exception as e:
        print(f"Database initialization error: {e}")
        import traceback
        traceback.print_exc()