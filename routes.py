"""
Flask アプリケーション - APIルート定義
ページ、ブロック、テンプレート、インポート/エクスポート機能など
"""

from flask import request, jsonify, send_file
from datetime import datetime, timedelta
import os
import io
import json
import zipfile
import shutil
import sqlite3
import subprocess
from werkzeug.utils import secure_filename

from database import (
    get_db, get_next_position, get_block_next_position, 
    mark_tree_deleted, hard_delete_tree
)
from utils import (
    allowed_file, estimate_calories, export_page_to_dict, 
    page_to_markdown, create_page_from_dict, copy_page_tree, 
    backup_database_to_json
)

DATABASE = 'notion.db'
UPLOAD_FOLDER = 'uploads'
BACKUP_FOLDER = 'backups'


def register_routes(app):
    """全APIルートをアプリに登録"""

    @app.route('/api/inbox', methods=['GET'])
    def get_inbox():
        """'あとで調べる'ページを取得"""
        from database import get_or_create_inbox
        inbox = get_or_create_inbox()
        return jsonify(inbox if inbox else {'error': 'Failed to create inbox'}), 200 if inbox else 500

    @app.route('/api/pages', methods=['GET'])
    def get_pages():
        conn = get_db()
        cursor = conn.cursor()
        # インデックスを活用して高速化
        cursor.execute('''
            SELECT * FROM pages 
            WHERE is_deleted = 0 
            ORDER BY parent_id, position
        ''')
        all_pages = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # フロントエンドで階層構造を構築（DBクエリを削減）
        page_map = {page['id']: {**page, 'children': []} for page in all_pages}
        roots = []
        for page in all_pages:
            if page['parent_id'] and page['parent_id'] in page_map:
                page_map[page['parent_id']]['children'].append(page_map[page['id']])
            else:
                roots.append(page_map[page['id']])
        return jsonify(roots)

    @app.route('/api/trash', methods=['GET'])
    def get_trash():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM pages WHERE is_deleted = 1 ORDER BY updated_at DESC')
        trash_pages = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(trash_pages)

    def get_items_by_category(category_title):
        """指定されたカテゴリーのページとブロックを取得する汎用関数"""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM pages 
            WHERE title = ? AND is_deleted = 0
            ORDER BY updated_at DESC
        ''', (category_title,))
        pages = [dict(row) for row in cursor.fetchall()]
        
        result = []
        for page in pages:
            cursor.execute('''
                SELECT * FROM blocks 
                WHERE page_id = ? AND type IN ('todo', 'text', 'h1')
                ORDER BY position
            ''', (page['id'],))
            blocks = [dict(row) for row in cursor.fetchall()]
            
            parent_page = None
            if page['parent_id']:
                cursor.execute('SELECT * FROM pages WHERE id = ?', (page['parent_id'],))
                parent_row = cursor.fetchone()
                if parent_row:
                    parent_page = dict(parent_row)
            
            result.append({
                'page': page,
                'parent_page': parent_page,
                'blocks': blocks
            })
        
        conn.close()
        return result

    @app.route('/api/all-workouts', methods=['GET'])
    def get_all_workouts():
        """全ての日記から筋トレページとそのブロックを取得"""
        return jsonify(get_items_by_category('筋トレ'))

    @app.route('/api/all-english-learning', methods=['GET'])
    def get_all_english_learning():
        """全ての日記から英語学習ページとそのブロックを取得"""
        return jsonify(get_items_by_category('英語学習'))

    @app.route('/api/all-meals', methods=['GET'])
    def get_all_meals():
        """全ての日記から食事ページとそのブロックを取得"""
        return jsonify(get_items_by_category('食事'))

    @app.route('/api/today-highlights/<int:page_id>', methods=['GET'])
    def get_today_highlights(page_id):
        """指定ページ内で今日作成されたブロックを取得"""
        conn = get_db()
        cursor = conn.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT * FROM blocks 
            WHERE page_id = ? AND DATE(created_at) = ?
            ORDER BY created_at DESC
            LIMIT 10
        ''', (page_id, today))
        highlights = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(highlights)

    @app.route('/api/pages', methods=['POST'])
    def create_page():
        data = request.json
        conn = get_db()
        cursor = conn.cursor()
        parent_id = data.get('parent_id')
        new_pos = get_next_position(cursor, parent_id)
        cursor.execute('INSERT INTO pages (title, icon, parent_id, position) VALUES (?, ?, ?, ?)',
                       (data.get('title', ''), data.get('icon', '📄'), parent_id, new_pos))
        page_id = cursor.lastrowid
        cursor.execute("INSERT INTO blocks (page_id, type, content, position) VALUES (?, 'text', '', ?)", (page_id, get_block_next_position(cursor, page_id)))
        conn.commit()
        cursor.execute('SELECT * FROM pages WHERE id = ?', (page_id,))
        page = dict(cursor.fetchone())
        conn.close()
        return jsonify(page)

    @app.route('/api/folders', methods=['POST'])
    def create_folder():
        data = request.json
        conn = get_db()
        cursor = conn.cursor()
        parent_id = data.get('parent_id')
        new_pos = get_next_position(cursor, parent_id)
        cursor.execute('INSERT INTO pages (title, icon, parent_id, position) VALUES (?, ?, ?, ?)',
                       (data.get('title', '新しいフォルダ'), '📁', parent_id, new_pos))
        folder_id = cursor.lastrowid
        conn.commit()
        cursor.execute('SELECT * FROM pages WHERE id = ?', (folder_id,))
        folder = dict(cursor.fetchone())
        conn.close()
        return jsonify(folder)

    @app.route('/api/pages/from-template', methods=['POST'])
    def create_page_from_template():
        data = request.json
        template_type = data.get('template')
        
        conn = get_db()
        cursor = conn.cursor()
        
        templates = {
            'daily': {
                'title': f'{datetime.now().strftime("%Y年%m月%d日")}の記録',
                'icon': '📝',
                'blocks': [
                    {'type': 'h1', 'content': '体調'},
                    {'type': 'text', 'content': ''},
                    {'type': 'h1', 'content': '天気'},
                    {'type': 'text', 'content': ''},
                    {'type': 'h1', 'content': 'やったこと'},
                    {'type': 'todo', 'content': ''},
                    {'type': 'h1', 'content': '振り返り'},
                    {'type': 'text', 'content': ''},
                ]
            },
            'reading': {
                'title': '読書メモ',
                'icon': '📚',
                'blocks': [
                    {'type': 'h1', 'content': '本のタイトル'},
                    {'type': 'text', 'content': ''},
                    {'type': 'h1', 'content': '著者'},
                    {'type': 'text', 'content': ''},
                    {'type': 'h1', 'content': '読んだ日'},
                    {'type': 'text', 'content': ''},
                    {'type': 'h1', 'content': '感想・メモ'},
                    {'type': 'text', 'content': ''},
                ]
            },
            'meeting': {
                'title': '会議メモ',
                'icon': '💼',
                'blocks': [
                    {'type': 'h1', 'content': '日時'},
                    {'type': 'text', 'content': ''},
                    {'type': 'h1', 'content': '参加者'},
                    {'type': 'text', 'content': ''},
                    {'type': 'h1', 'content': '議題'},
                    {'type': 'text', 'content': ''},
                    {'type': 'h1', 'content': '決定事項'},
                    {'type': 'todo', 'content': ''},
                ]
            },
            'english': {
                'title': f'{datetime.now().strftime("%Y年%m月%d日")}の英語進捗',
                'icon': '🌍',
                'blocks': [
                    {'type': 'h1', 'content': '今日の学習内容'},
                    {'type': 'text', 'content': ''},
                    {'type': 'h1', 'content': '新しい単語'},
                    {'type': 'todo', 'content': ''},
                    {'type': 'h1', 'content': '発音練習'},
                    {'type': 'text', 'content': ''},
                    {'type': 'h1', 'content': 'リスニング時間'},
                    {'type': 'text', 'content': ''},
                    {'type': 'h1', 'content': '気づいたこと'},
                    {'type': 'text', 'content': ''},
                ]
            }
        }
        
        template = templates.get(template_type, templates['daily'])
        new_pos = get_next_position(cursor, None)
        
        cursor.execute('INSERT INTO pages (title, icon, parent_id, position) VALUES (?, ?, ?, ?)',
                       (template['title'], template['icon'], None, new_pos))
        page_id = cursor.lastrowid
        
        for i, block in enumerate(template['blocks']):
            cursor.execute(
                "INSERT INTO blocks (page_id, type, content, checked, position, props) VALUES (?, ?, ?, ?, ?, ?)",
                (page_id, block['type'], block['content'], block.get('checked', 0), (i + 1) * 1000.0, '{}')
            )
        
        conn.commit()
        cursor.execute('SELECT * FROM pages WHERE id = ?', (page_id,))
        page = dict(cursor.fetchone())
        conn.close()
        return jsonify(page)

    @app.route('/api/pages/from-date', methods=['POST'])
    def create_page_from_date():
        """指定日付のページを作成（存在しない場合は前日をコピー）"""
        data = request.json
        date_str = data.get('date')
        
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d')
            title = f"{target_date.year}年{target_date.month}月{target_date.day}日"
        except Exception:
            return jsonify({'error': 'Invalid date format'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM pages WHERE title = ? AND is_deleted = 0 LIMIT 1', (title,))
        existing = cursor.fetchone()
        if existing:
            conn.close()
            return jsonify(dict(existing))
        
        prev_date = target_date - timedelta(days=1)
        prev_title = f"{prev_date.year}年{prev_date.month}月{prev_date.day}日"
        cursor.execute('SELECT id FROM pages WHERE title = ? AND is_deleted = 0 ORDER BY created_at DESC LIMIT 1', (prev_title,))
        prev_row = cursor.fetchone()
        
        if prev_row:
            previous_page_id = prev_row['id']
            new_page_id = copy_page_tree(cursor, previous_page_id, new_title=title, new_parent_id=None, override_icon='📅')
            conn.commit()
            
            cursor.execute('SELECT title FROM pages WHERE parent_id = ? AND is_deleted = 0', (new_page_id,))
            existing_titles = {row['title'] for row in cursor.fetchall()}
            
            required_children = [
                ('日記', '📝'),
                ('筋トレ', '🏋️'),
                ('英語学習', '🌍'),
                ('食事', '🍽️'),
            ]
            
            next_pos = get_next_position(cursor, new_page_id)
            for title_req, icon_req in required_children:
                if title_req not in existing_titles:
                    cursor.execute(
                        'INSERT INTO pages (title, icon, parent_id, position) VALUES (?, ?, ?, ?)',
                        (title_req, icon_req, new_page_id, next_pos)
                    )
                    next_pos += 1000.0
            
            conn.commit()
            cursor.execute('SELECT * FROM pages WHERE id = ?', (new_page_id,))
            page = dict(cursor.fetchone())
            conn.close()
            return jsonify(page)
        
        new_pos = get_next_position(cursor, None)
        cursor.execute('INSERT INTO pages (title, icon, parent_id, position) VALUES (?, ?, ?, ?)',
                       (title, '📅', None, new_pos))
        page_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO blocks (page_id, type, content, position, props) VALUES (?, 'text', '', ?, ?)", 
                       (page_id, 1000.0, '{}'))
        
        children_templates = [
            {
                'title': '日記',
                'icon': '📝',
                'blocks': [
                    {'type': 'h1', 'content': '体調'},
                    {'type': 'text', 'content': ''},
                    {'type': 'h1', 'content': '天気'},
                    {'type': 'text', 'content': ''},
                    {'type': 'h1', 'content': 'やったこと'},
                    {'type': 'todo', 'content': ''},
                    {'type': 'h1', 'content': '振り返り'},
                    {'type': 'text', 'content': ''},
                ]
            },
            {
                'title': '筋トレ',
                'icon': '🏋️',
                'blocks': [
                    {'type': 'h1', 'content': '今日のメニュー'},
                    {'type': 'todo', 'content': ''},
                    {'type': 'h1', 'content': 'セット・回数'},
                    {'type': 'text', 'content': ''},
                    {'type': 'h1', 'content': 'メモ'},
                    {'type': 'text', 'content': ''},
                ]
            },
            {
                'title': '英語学習',
                'icon': '🌍',
                'blocks': [
                    {'type': 'h1', 'content': '今日の学習内容'},
                    {'type': 'text', 'content': ''},
                    {'type': 'h1', 'content': '新しい単語'},
                    {'type': 'todo', 'content': ''},
                    {'type': 'h1', 'content': '発音練習'},
                    {'type': 'text', 'content': ''},
                    {'type': 'h1', 'content': 'リスニング時間'},
                    {'type': 'text', 'content': ''},
                    {'type': 'h1', 'content': '気づいたこと'},
                    {'type': 'text', 'content': ''},
                ]
            },
            {
                'title': '食事',
                'icon': '🍽️',
                'blocks': [
                    {'type': 'h1', 'content': '🌅 朝食'},
                    {'type': 'todo', 'content': '', 'checked': 0},
                    {'type': 'text', 'content': ''},
                    {'type': 'h1', 'content': '🌞 昼食'},
                    {'type': 'todo', 'content': '', 'checked': 0},
                    {'type': 'text', 'content': ''},
                    {'type': 'h1', 'content': '🌙 夕食'},
                    {'type': 'todo', 'content': '', 'checked': 0},
                    {'type': 'text', 'content': ''},
                    {'type': 'h1', 'content': 'カロリー記録'},
                    {'type': 'calorie', 'content': ''},
                ]
            }
        ]
        
        for i, child in enumerate(children_templates):
            cursor.execute('INSERT INTO pages (title, icon, parent_id, position) VALUES (?, ?, ?, ?)',
                           (child['title'], child['icon'], page_id, (i + 1) * 1000.0))
            child_id = cursor.lastrowid
            for j, block in enumerate(child['blocks']):
                cursor.execute(
                    "INSERT INTO blocks (page_id, type, content, checked, position, props) VALUES (?, ?, ?, ?, ?, ?)",
                    (child_id, block['type'], block.get('content', ''), block.get('checked', 0), (j + 1) * 1000.0, '{}')
                )
        
        conn.commit()
        cursor.execute('SELECT * FROM pages WHERE id = ?', (page_id,))
        page = dict(cursor.fetchone())
        conn.close()
        return jsonify(page)

    @app.route('/api/pages/<int:page_id>', methods=['GET'])
    def get_page(page_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM pages WHERE id = ?', (page_id,))
        page_row = cursor.fetchone()
        if not page_row:
            conn.close()
            return jsonify({'error': 'Page not found'}), 404
        page = dict(page_row)
        # インデックスを活用してブロック取得を高速化
        cursor.execute('''
            SELECT * FROM blocks 
            WHERE page_id = ? 
            ORDER BY position
        ''', (page_id,))
        page['blocks'] = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(page)

    @app.route('/api/pages/<int:page_id>', methods=['PUT'])
    def update_page(page_id):
        data = request.json
        conn = get_db()
        cursor = conn.cursor()
        updates = []
        values = []
        fields = ['title', 'icon', 'parent_id', 'cover_image', 'is_pinned', 'is_deleted', 'position']
        for field in fields:
            if field in data:
                updates.append(f'{field} = ?')
                values.append(data[field])
        if updates:
            updates.append('updated_at = CURRENT_TIMESTAMP')
            values.append(page_id)
            cursor.execute(f'UPDATE pages SET {", ".join(updates)} WHERE id = ?', values)
            conn.commit()
        cursor.execute('SELECT * FROM pages WHERE id = ?', (page_id,))
        page = dict(cursor.fetchone())
        conn.close()
        return jsonify(page)

    @app.route('/api/pages/<int:page_id>/toggle-pin', methods=['POST'])
    def toggle_pin(page_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT is_pinned FROM pages WHERE id = ?', (page_id,))
        row = cursor.fetchone()
        new_pinned = 0 if row[0] else 1
        cursor.execute('UPDATE pages SET is_pinned = ? WHERE id = ?', (new_pinned, page_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'is_pinned': new_pinned})

    @app.route('/api/pages/<int:page_id>/move-to-trash', methods=['POST'])
    def move_to_trash(page_id):
        conn = get_db()
        cursor = conn.cursor()
        mark_tree_deleted(cursor, page_id, is_deleted=True)
        conn.commit()
        conn.close()
        return jsonify({'success': True})

    @app.route('/api/pages/<int:page_id>/restore', methods=['POST'])
    def restore_page(page_id):
        conn = get_db()
        cursor = conn.cursor()
        mark_tree_deleted(cursor, page_id, is_deleted=False)
        conn.commit()
        conn.close()
        return jsonify({'success': True})

    @app.route('/api/pages/<int:page_id>/copy', methods=['POST'])
    def copy_page(page_id):
        """ページをコピー（ツリー構造ごと）"""
        data = request.json or {}
        parent_id = data.get('parent_id')
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT title FROM pages WHERE id = ?', (page_id,))
        original = cursor.fetchone()
        new_title = (dict(original)['title'] if original else '無題') + 'のコピー'
        
        new_page_id = copy_page_tree(cursor, page_id, new_parent_id=parent_id, new_title=new_title)
        
        conn.commit()
        cursor.execute('SELECT * FROM pages WHERE id = ?', (new_page_id,))
        new_page = dict(cursor.fetchone())
        conn.close()
        
        return jsonify(new_page)

    @app.route('/api/pages/<int:page_id>', methods=['DELETE'])
    def delete_page(page_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('PRAGMA foreign_keys = ON')
        hard_delete_tree(cursor, page_id)
        conn.commit()
        conn.close()
        return jsonify({'success': True})

    @app.route('/api/search', methods=['GET'])
    def search():
        query = request.args.get('q', '')
        if not query: return jsonify([])
        conn = get_db()
        cursor = conn.cursor()
        search_query = f"{query}*"
        try:
            sql = '''
                SELECT blocks.id as block_id, blocks.page_id, pages.title as page_title, pages.icon, blocks.content, 
                       snippet(blocks_fts, 0, '<b>', '</b>', '...', 10) as snippet,
                       pages.parent_id
                FROM blocks_fts
                JOIN blocks ON blocks_fts.rowid = blocks.id
                JOIN pages ON blocks.page_id = pages.id
                WHERE blocks_fts MATCH ?
                ORDER BY rank
                LIMIT 20
            '''
            cursor.execute(sql, (search_query,))
            results = [dict(row) for row in cursor.fetchall()]
            
            for result in results:
                breadcrumb = []
                current_id = result.get('parent_id')
                while current_id:
                    cursor.execute('SELECT id, title, icon, parent_id FROM pages WHERE id = ?', (current_id,))
                    parent_row = cursor.fetchone()
                    if parent_row:
                        parent_dict = dict(parent_row)
                        breadcrumb.insert(0, {
                            'id': parent_dict['id'],
                            'title': parent_dict['title'],
                            'icon': parent_dict['icon']
                        })
                        current_id = parent_dict['parent_id']
                    else:
                        break
                result['breadcrumb'] = breadcrumb
        except Exception as e:
            results = []
        conn.close()
        return jsonify(results)

    @app.route('/api/pages/<int:page_id>/blocks', methods=['POST'])
    def create_block(page_id):
        data = request.json
        conn = get_db()
        cursor = conn.cursor()
        if data.get('position') is not None:
            new_pos = float(data.get('position'))
        else:
            new_pos = get_block_next_position(cursor, page_id)
        cursor.execute('INSERT INTO blocks (page_id, type, content, checked, position, props) VALUES (?, ?, ?, ?, ?, ?)',
                       (page_id, data.get('type', 'text'), data.get('content', ''), data.get('checked', False), new_pos, data.get('props', '{}')))
        block_id = cursor.lastrowid
        conn.commit()
        cursor.execute('SELECT * FROM blocks WHERE id = ?', (block_id,))
        block = dict(cursor.fetchone())
        conn.close()
        return jsonify(block)

    @app.route('/api/blocks/<int:block_id>', methods=['PUT'])
    def update_block(block_id):
        data = request.json
        conn = get_db()
        cursor = conn.cursor()
        updates = []
        values = []
        fields = ['type', 'content', 'checked', 'position', 'collapsed', 'details', 'props']
        for field in fields:
            if field in data:
                updates.append(f'{field} = ?')
                values.append(data[field])
        if updates:
            updates.append('updated_at = CURRENT_TIMESTAMP')
            values.append(block_id)
            cursor.execute(f'UPDATE blocks SET {", ".join(updates)} WHERE id = ?', values)
            conn.commit()
        cursor.execute('SELECT * FROM blocks WHERE id = ?', (block_id,))
        block = dict(cursor.fetchone())
        conn.close()
        
        import time
        current_time = time.time()
        last_backup_time = getattr(update_block, '_last_backup', 0)
        if current_time - last_backup_time > 300:
            backup_database_to_json()
            update_block._last_backup = current_time
        
        return jsonify(block)

    @app.route('/api/blocks/<int:block_id>', methods=['DELETE'])
    def delete_block(block_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM blocks WHERE id = ?', (block_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})

    @app.route('/api/calc-calories', methods=['POST'])
    def calc_calories():
        """メニュー文字列から概算カロリーを返す"""
        data = request.json or {}
        raw_lines = data.get('lines', '')
        if isinstance(raw_lines, list):
            lines = raw_lines
        else:
            lines = str(raw_lines).splitlines()
        result = estimate_calories(lines)
        return jsonify(result)

    @app.route('/api/upload', methods=['POST'])
    def upload_file():
        if 'file' not in request.files: return jsonify({'error': 'No file'}), 400
        file = request.files['file']
        page_id = request.form.get('page_id')
        is_cover = request.form.get('is_cover') == 'true'
        if file.filename == '' or not allowed_file(file.filename): return jsonify({'error': 'Invalid file'}), 400
        filename = secure_filename(file.filename)
        import uuid
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file.save(os.path.join(UPLOAD_FOLDER, unique_filename))
        file_url = f'/uploads/{unique_filename}'
        conn = get_db()
        cursor = conn.cursor()
        if is_cover and page_id:
            cursor.execute('UPDATE pages SET cover_image = ? WHERE id = ?', (file_url, page_id))
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'file_url': file_url, 'type': 'cover'})
        elif page_id:
            cursor.execute('SELECT MAX(position) FROM blocks WHERE page_id = ?', (page_id,))
            new_pos = (cursor.fetchone()[0] or -1) + 1
            block_type = 'image' if filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp'} else 'file'
            cursor.execute('INSERT INTO blocks (page_id, type, content, position) VALUES (?, ?, ?, ?)',
                           (page_id, block_type, file_url, new_pos))
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'file_url': file_url, 'block_type': block_type})
        return jsonify({'error': 'Page ID missing'}), 400

    @app.route('/api/export/all/json', methods=['GET'])
    def export_all_json():
        """全ページをJSON形式でエクスポート"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM pages WHERE is_deleted = 0 AND parent_id IS NULL ORDER BY position')
        root_pages = [export_page_to_dict(cursor, row['id']) for row in cursor.fetchall()]
        conn.close()
        
        export_data = {
            'version': '1.0',
            'exported_at': datetime.now().isoformat(),
            'pages': root_pages
        }
        
        response = send_file(
            io.BytesIO(json.dumps(export_data, ensure_ascii=False, indent=2).encode('utf-8')),
            mimetype='application/json',
            as_attachment=True,
            download_name=f"diary_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        return response

    @app.route('/api/export/pages/<int:page_id>/json', methods=['GET'])
    def export_page_json(page_id):
        """指定ページをJSON形式でエクスポート"""
        conn = get_db()
        cursor = conn.cursor()
        page = export_page_to_dict(cursor, page_id)
        conn.close()
        
        if not page:
            return jsonify({'error': 'Page not found'}), 404
        
        export_data = {
            'version': '1.0',
            'exported_at': datetime.now().isoformat(),
            'page': page
        }
        
        response = send_file(
            io.BytesIO(json.dumps(export_data, ensure_ascii=False, indent=2).encode('utf-8')),
            mimetype='application/json',
            as_attachment=True,
            download_name=f"{page.get('title', 'page')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        return response

    @app.route('/api/export/pages/<int:page_id>/markdown', methods=['GET'])
    def export_page_markdown(page_id):
        """指定ページをMarkdown形式でエクスポート"""
        conn = get_db()
        cursor = conn.cursor()
        page = export_page_to_dict(cursor, page_id)
        conn.close()
        
        if not page:
            return jsonify({'error': 'Page not found'}), 404
        
        markdown_content = page_to_markdown(page, level=1)
        
        response = send_file(
            io.BytesIO(markdown_content.encode('utf-8')),
            mimetype='text/markdown',
            as_attachment=True,
            download_name=f"{page.get('title', 'page')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )
        return response

    @app.route('/api/export/pages/<int:page_id>/zip', methods=['GET'])
    def export_page_zip(page_id):
        """指定ページを添付ファイル含めZIP化してエクスポート"""
        conn = get_db()
        cursor = conn.cursor()
        page = export_page_to_dict(cursor, page_id)
        conn.close()
        
        if not page:
            return jsonify({'error': 'Page not found'}), 404
        
        zip_buffer = io.BytesIO()
        
        def add_page_to_zip(z, pg, prefix=''):
            """ページとその子ページを再帰的にZIPに追加"""
            page_dir = f"{prefix}{pg.get('title', '無題')}_[{pg['id']}]"
            
            md_content = page_to_markdown(pg, level=1)
            z.writestr(f"{page_dir}/page.md", md_content.encode('utf-8'))
            
            metadata = {
                'id': pg['id'],
                'title': pg.get('title', ''),
                'icon': pg.get('icon', ''),
                'created_at': pg.get('created_at', ''),
                'updated_at': pg.get('updated_at', '')
            }
            z.writestr(f"{page_dir}/metadata.json", json.dumps(metadata, ensure_ascii=False, indent=2).encode('utf-8'))
            
            for block in pg.get('blocks', []):
                if block.get('type') in ['image', 'file']:
                    file_path = block.get('content', '')
                    if file_path and file_path.startswith('/uploads/'):
                        filename = file_path.split('/')[-1]
                        full_path = os.path.join(UPLOAD_FOLDER, filename)
                        if os.path.exists(full_path):
                            z.write(full_path, f"{page_dir}/files/{filename}")
            
            for child in pg.get('children', []):
                add_page_to_zip(z, child, f"{page_dir}/")
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            add_page_to_zip(zf, page)
        
        zip_buffer.seek(0)
        response = send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f"{page.get('title', 'page')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        )
        return response

    @app.route('/api/import/json', methods=['POST'])
    def import_json():
        """JSONファイルをインポート"""
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '' or not file.filename.endswith('.json'):
            return jsonify({'error': 'Invalid file format, expected JSON'}), 400
        
        try:
            import_data = json.loads(file.read().decode('utf-8'))
        except Exception as e:
            return jsonify({'error': f'Failed to parse JSON: {str(e)}'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            imported_ids = []
            
            pages_to_import = import_data.get('pages', [])
            if import_data.get('page'):
                pages_to_import = [import_data.get('page')]
            
            for page_dict in pages_to_import:
                new_id = create_page_from_dict(cursor, page_dict)
                imported_ids.append(new_id)
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': f'{len(imported_ids)} page(s) imported',
                'imported_ids': imported_ids
            })
        except Exception as e:
            conn.rollback()
            conn.close()
            return jsonify({'error': f'Import failed: {str(e)}'}), 500

    @app.route('/api/import/zip', methods=['POST'])
    def import_zip():
        """ZIPファイルをインポート"""
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '' or not file.filename.endswith('.zip'):
            return jsonify({'error': 'Invalid file format, expected ZIP'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            with zipfile.ZipFile(io.BytesIO(file.read()), 'r') as zf:
                metadata_files = [f for f in zf.namelist() if f.endswith('metadata.json') and f.count('/') == 1]
                
                if not metadata_files:
                    return jsonify({'error': 'No valid ZIP structure found'}), 400
                
                imported_ids = []
                
                for metadata_file in metadata_files:
                    metadata = json.loads(zf.read(metadata_file).decode('utf-8'))
                    
                    cursor.execute('SELECT MAX(position) FROM pages WHERE parent_id IS NULL')
                    max_pos = cursor.fetchone()[0]
                    position = (max_pos if max_pos is not None else -1) + 1
                    
                    cursor.execute(
                        'INSERT INTO pages (title, icon, parent_id, position) VALUES (?, ?, ?, ?)',
                        (metadata.get('title', ''), metadata.get('icon', '📄'), None, position)
                    )
                    new_page_id = cursor.lastrowid
                    imported_ids.append(new_page_id)
                    
                    page_dir = metadata_file.split('/')[0]
                    page_md_path = f"{page_dir}/page.md"
                    
                    if page_md_path in zf.namelist():
                        md_content = zf.read(page_md_path).decode('utf-8')
                        cursor.execute(
                            "INSERT INTO blocks (page_id, type, content, position) VALUES (?, 'text', ?, 0)",
                            (new_page_id, md_content)
                        )
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': f'{len(imported_ids)} page(s) imported from ZIP',
                'imported_ids': imported_ids
            })
        except Exception as e:
            conn.rollback()
            conn.close()
            return jsonify({'error': f'ZIP import failed: {str(e)}'}), 500

    @app.route('/api/templates', methods=['GET'])
    def get_templates():
        """テンプレート一覧を取得"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM templates ORDER BY created_at DESC')
        templates = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(templates)

    @app.route('/api/templates', methods=['POST'])
    def create_template():
        """新しいテンプレートを作成"""
        data = request.json
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO templates (name, icon, description, content_json) VALUES (?, ?, ?, ?)',
            (
                data.get('name', '新しいテンプレート'),
                data.get('icon', '📋'),
                data.get('description', ''),
                json.dumps(data.get('content', {}), ensure_ascii=False)
            )
        )
        template_id = cursor.lastrowid
        conn.commit()
        
        cursor.execute('SELECT * FROM templates WHERE id = ?', (template_id,))
        template = dict(cursor.fetchone())
        conn.close()
        return jsonify(template)

    @app.route('/api/templates/<int:template_id>', methods=['PUT'])
    def update_template(template_id):
        """テンプレートを更新"""
        data = request.json
        conn = get_db()
        cursor = conn.cursor()
        
        updates = []
        values = []
        
        if 'name' in data:
            updates.append('name = ?')
            values.append(data['name'])
        if 'icon' in data:
            updates.append('icon = ?')
            values.append(data['icon'])
        if 'description' in data:
            updates.append('description = ?')
            values.append(data['description'])
        if 'content' in data:
            updates.append('content_json = ?')
            values.append(json.dumps(data['content'], ensure_ascii=False))
        
        if updates:
            updates.append('updated_at = CURRENT_TIMESTAMP')
            values.append(template_id)
            cursor.execute(f"UPDATE templates SET {', '.join(updates)} WHERE id = ?", values)
            conn.commit()
        
        cursor.execute('SELECT * FROM templates WHERE id = ?', (template_id,))
        template = dict(cursor.fetchone())
        conn.close()
        return jsonify(template)

    @app.route('/api/templates/<int:template_id>', methods=['DELETE'])
    def delete_template(template_id):
        """テンプレートを削除"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM templates WHERE id = ?', (template_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})

    @app.route('/api/pages/from-custom-template/<int:template_id>', methods=['POST'])
    def create_page_from_custom_template(template_id):
        """カスタムテンプレートからページを作成"""
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM templates WHERE id = ?', (template_id,))
        template_row = cursor.fetchone()
        
        if not template_row:
            conn.close()
            return jsonify({'error': 'Template not found'}), 404
        
        template = dict(template_row)
        content = json.loads(template['content_json'])
        
        new_pos = get_next_position(cursor, None)
        cursor.execute(
            'INSERT INTO pages (title, icon, parent_id, position) VALUES (?, ?, ?, ?)',
            (content.get('title', template['name']), template['icon'], None, new_pos)
        )
        page_id = cursor.lastrowid
        
        for i, block in enumerate(content.get('blocks', [])):
            cursor.execute(
                'INSERT INTO blocks (page_id, type, content, checked, position, collapsed, details, props) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (
                    page_id,
                    block.get('type', 'text'),
                    block.get('content', ''),
                    block.get('checked', 0),
                    (i + 1) * 1000.0,
                    block.get('collapsed', 0),
                    block.get('details', ''),
                    block.get('props', '{}')
                )
            )
        
        for i, child in enumerate(content.get('children', [])):
            child_pos = (i + 1) * 1000.0
            cursor.execute(
                'INSERT INTO pages (title, icon, parent_id, position) VALUES (?, ?, ?, ?)',
                (child.get('title', ''), child.get('icon', '📄'), page_id, child_pos)
            )
            child_id = cursor.lastrowid
            
            for j, block in enumerate(child.get('blocks', [])):
                cursor.execute(
                    'INSERT INTO blocks (page_id, type, content, checked, position, props) VALUES (?, ?, ?, ?, ?, ?)',
                    (child_id, block.get('type', 'text'), block.get('content', ''), block.get('checked', 0), (j + 1) * 1000.0, '{}')
                )
        
        conn.commit()
        cursor.execute('SELECT * FROM pages WHERE id = ?', (page_id,))
        page = dict(cursor.fetchone())
        conn.close()
        return jsonify(page)

    @app.route('/api/pages/<int:page_id>/save-as-template', methods=['POST'])
    def save_page_as_template(page_id):
        """現在のページをテンプレートとして保存"""
        data = request.json
        conn = get_db()
        cursor = conn.cursor()
        
        page_dict = export_page_to_dict(cursor, page_id)
        if not page_dict:
            conn.close()
            return jsonify({'error': 'Page not found'}), 404
        
        template_content = {
            'title': page_dict.get('title', ''),
            'blocks': page_dict.get('blocks', []),
            'children': page_dict.get('children', [])
        }
        
        cursor.execute(
            'INSERT INTO templates (name, icon, description, content_json) VALUES (?, ?, ?, ?)',
            (
                data.get('name', page_dict.get('title', '新しいテンプレート')),
                page_dict.get('icon', '📋'),
                data.get('description', ''),
                json.dumps(template_content, ensure_ascii=False)
            )
        )
        template_id = cursor.lastrowid
        conn.commit()
        
        cursor.execute('SELECT * FROM templates WHERE id = ?', (template_id,))
        template = dict(cursor.fetchone())
        conn.close()
        return jsonify(template)

    @app.route('/webhook_deploy', methods=['POST'])
    def webhook_deploy():
        subprocess.run(['git', 'fetch', '--all'], cwd='/home/nnnkeita/mysite')
        subprocess.run(['git', 'reset', '--hard', 'origin/main'], cwd='/home/nnnkeita/mysite')
        subprocess.run(['touch', '/var/www/nnnkeita_pythonanywhere_com_wsgi.py'])
        return jsonify({'status': 'success', 'message': 'Deployed and Reloaded!'})

    @app.route('/download_db', methods=['GET'])
    def download_db():
        """データベースファイルをダウンロード"""
        try:
            return send_file(DATABASE, as_attachment=True, download_name='notion.db')
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/list_backups', methods=['GET'])
    def list_backups():
        """利用可能なバックアップファイルをリストアップ"""
        try:
            import glob
            json_backups = sorted(glob.glob(os.path.join(BACKUP_FOLDER, 'backup_*.json')))
            backups = []
            for backup_file in json_backups:
                stat = os.stat(backup_file)
                backups.append({
                    'name': os.path.basename(backup_file),
                    'path': backup_file,
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            return jsonify({'backups': backups})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/restore_backup/<backup_name>', methods=['POST'])
    def restore_backup(backup_name):
        """バックアップファイルからデータベースを復元"""
        try:
            backup_file = os.path.join(BACKUP_FOLDER, backup_name)
            
            if not os.path.exists(backup_file) or not backup_file.startswith(BACKUP_FOLDER):
                return jsonify({'error': 'Backup file not found'}), 404
            
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            backup_path = DATABASE + '.backup_' + datetime.now().strftime('%Y%m%d_%H%M%S')
            if os.path.exists(DATABASE):
                shutil.copy2(DATABASE, backup_path)
            
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            
            for table_name, rows in backup_data['tables'].items():
                if not rows:
                    continue
                
                cursor.execute(f'DELETE FROM {table_name}')
                
                if rows:
                    first_row = rows[0]
                    columns = list(first_row.keys())
                    placeholders = ', '.join(['?' for _ in columns])
                    insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                    
                    for row in rows:
                        values = [row.get(col) for col in columns]
                        cursor.execute(insert_sql, values)
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'status': 'success',
                'message': f'Database restored from {backup_name}',
                'backup_created': backup_path
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/upload_db', methods=['POST'])
    def upload_db():
        """データベースファイルをアップロード（復元用）"""
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            backup_path = DATABASE + '.backup_' + datetime.now().strftime('%Y%m%d_%H%M%S')
            if os.path.exists(DATABASE):
                shutil.copy2(DATABASE, backup_path)
            
            file.save(DATABASE)
            
            return jsonify({
                'status': 'success', 
                'message': 'Database restored successfully',
                'backup': backup_path
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
