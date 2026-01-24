#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os
import sqlite3
from datetime import datetime


def connect_db(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"DBファイルが見つかりません: {path}")
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def list_tables(conn):
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    return [r[0] for r in cur.fetchall()]


def table_counts(conn, tables):
    cur = conn.cursor()
    counts = {}
    for t in tables:
        try:
            cur.execute(f"SELECT COUNT(*) as c FROM {t}")
            counts[t] = cur.fetchone()[0]
        except Exception as e:
            counts[t] = f"error: {e}"
    return counts


def fetch_pages(conn, limit=50):
    cur = conn.cursor()
    cur.execute(
        "SELECT id, title, icon, parent_id, position, created_at, updated_at, cover_image "
        "FROM pages ORDER BY created_at DESC LIMIT ?",
        (limit,),
    )
    return [dict(r) for r in cur.fetchall()]


def fetch_blocks_for_page(conn, page_id, limit=50):
    cur = conn.cursor()
    cur.execute(
        "SELECT id, page_id, type, content, checked, position, created_at, updated_at "
        "FROM blocks WHERE page_id = ? ORDER BY position ASC LIMIT ?",
        (page_id, limit),
    )
    return [dict(r) for r in cur.fetchall()]


def export_snapshot(conn, out_path: str, page_limit=200, block_limit=200):
    snapshot = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "pages": [],
    }
    pages = fetch_pages(conn, page_limit)
    for p in pages:
        p_copy = dict(p)
        p_copy["blocks"] = fetch_blocks_for_page(conn, p["id"], block_limit)
        snapshot["pages"].append(p_copy)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Notion-like DBインスペクタ")
    parser.add_argument(
        "db",
        nargs="?",
        default=os.path.join(os.path.dirname(__file__), "..", "notion.db"),
        help="SQLite DBファイルへのパス（デフォルト: ワークスペース直下のnotion.db）",
    )
    parser.add_argument(
        "--export-json",
        default=os.path.join(os.path.dirname(__file__), "..", "backups", "pages_snapshot.json"),
        help="JSONスナップショット出力先",
    )
    args = parser.parse_args()

    db_path = os.path.abspath(args.db)
    conn = connect_db(db_path)

    tables = list_tables(conn)
    counts = table_counts(conn, tables)

    print("=== テーブル一覧 ===")
    for t in tables:
        print(f"- {t}: {counts.get(t)}件")

    print("\n=== 直近のページ（最大50件） ===")
    for p in fetch_pages(conn, 50):
        print(f"[#{p['id']}] {p['title'] or '無題'} {p['icon']} parent={p['parent_id']} created={p['created_at']}")

    # 先頭ページのブロックを例示
    pages = fetch_pages(conn, 1)
    if pages:
        pid = pages[0]["id"]
        print(f"\n=== ページ#{pid}のブロック（最大50件） ===")
        blocks = fetch_blocks_for_page(conn, pid, 50)
        for b in blocks:
            content_preview = (b["content"] or "").replace("\n", " ")
            if len(content_preview) > 80:
                content_preview = content_preview[:77] + "..."
            print(f"- ({b['type']}) {content_preview}")

    out_file = export_snapshot(conn, os.path.abspath(args.export_json))
    print(f"\nJSONスナップショットを出力しました: {out_file}")

    conn.close()


if __name__ == "__main__":
    main()
