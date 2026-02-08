#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HealthPlanet daily sync script."""
import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta

from database import get_db, get_healthplanet_token
from utils import get_or_create_date_page


def _fetch_healthplanet_innerscan(access_token, from_str, to_str, tags):
    params = {
        'access_token': access_token,
        'date': '1',
        'from': from_str,
        'to': to_str,
        'tag': ','.join(tags)
    }
    url = 'https://www.healthplanet.jp/status/innerscan.json?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, method='GET')
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8'))


def _format_healthplanet_line(measurements):
    parts = []
    weight = measurements.get('6021')
    fat = measurements.get('6022')
    body_age = measurements.get('6028')
    if weight:
        parts.append(f"体重 {weight}kg")
    if fat:
        parts.append(f"体脂肪 {fat}%")
    if body_age:
        parts.append(f"体内年齢 {body_age}才")
    return ' / '.join(parts)


def _upsert_healthplanet_block(cursor, page_id, content):
    cursor.execute('SELECT id, position, props FROM blocks WHERE page_id = ? ORDER BY position ASC', (page_id,))
    rows = cursor.fetchall()
    target_id = None
    for row in rows:
        props = row['props'] or '{}'
        try:
            props_json = json.loads(props) if isinstance(props, str) else props
        except Exception:
            props_json = {}
        if props_json.get('source') == 'healthplanet':
            target_id = row['id']
            break

    if target_id:
        cursor.execute('UPDATE blocks SET content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (content, target_id))
        return

    if rows:
        min_pos = min(row['position'] for row in rows)
        new_pos = min_pos - 1000.0
    else:
        new_pos = 1000.0

    props = json.dumps({'source': 'healthplanet', 'type': 'body'})
    cursor.execute(
        "INSERT INTO blocks (page_id, type, content, position, props) VALUES (?, 'text', ?, ?, ?)",
        (page_id, content, new_pos, props)
    )


def main():
    token_row = get_healthplanet_token()
    if not token_row:
        print('HealthPlanet is not linked. Run /api/healthplanet/auth first.')
        return 1

    access_token = token_row['access_token']
    expires_at = token_row['expires_at']
    if expires_at:
        try:
            if datetime.fromisoformat(expires_at) < datetime.utcnow():
                print('HealthPlanet token expired. Re-authorize needed.')
                return 1
        except Exception:
            pass

    jst_now = datetime.utcnow() + timedelta(hours=9)
    start = jst_now.replace(hour=0, minute=0, second=0, microsecond=0)
    from_str = start.strftime('%Y%m%d%H%M%S')
    to_str = jst_now.strftime('%Y%m%d%H%M%S')
    date_str = jst_now.strftime('%Y-%m-%d')

    data = _fetch_healthplanet_innerscan(access_token, from_str, to_str, ['6021', '6022', '6028'])

    measurements = {}
    for entry in data.get('data', []) if isinstance(data, dict) else []:
        tag = str(entry.get('tag', ''))
        keydata = str(entry.get('keydata', '')).strip()
        date_value = str(entry.get('date', '')).strip()
        if not tag or not keydata:
            continue
        current = measurements.get(tag)
        if not current or date_value > current.get('date', ''):
            measurements[tag] = {'value': keydata, 'date': date_value}

    latest_values = {k: v.get('value') for k, v in measurements.items()}
    content = _format_healthplanet_line(latest_values)
    if not content:
        print('No data found for today.')
        return 1

    conn = get_db()
    cursor = conn.cursor()
    page = get_or_create_date_page(cursor, date_str)
    if not page:
        conn.close()
        print('Failed to create date page.')
        return 1

    _upsert_healthplanet_block(cursor, page['id'], content)
    conn.commit()
    conn.close()
    print('Synced HealthPlanet data to today page.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
