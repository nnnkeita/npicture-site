-- Database Restore Dump
-- Generated from: backup_20260213_210129.json
-- Timestamp: 2026-02-13T21:01:29.436081

-- Drop existing tables
DROP TABLE IF EXISTS blocks;
DROP TABLE IF EXISTS pages;
DROP TABLE IF EXISTS templates;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS password_reset_tokens;
DROP TABLE IF EXISTS healthplanet_tokens;

-- Create tables

CREATE TABLE pages (
    id INTEGER PRIMARY KEY,
    title TEXT DEFAULT '',
    icon TEXT DEFAULT '📄',
    cover_image TEXT DEFAULT '',
    parent_id INTEGER,
    position REAL DEFAULT 0.0,
    position_new REAL DEFAULT 0.0,
    is_pinned INTEGER DEFAULT 0,
    is_deleted INTEGER DEFAULT 0,
    mood INTEGER DEFAULT 0,
    gratitude_text TEXT DEFAULT '',
    created_at TEXT,
    updated_at TEXT
);


CREATE TABLE blocks (
    id INTEGER PRIMARY KEY,
    page_id INTEGER NOT NULL,
    type TEXT DEFAULT 'text',
    content TEXT DEFAULT '',
    checked INTEGER DEFAULT 0,
    position REAL DEFAULT 0.0,
    collapsed INTEGER DEFAULT 0,
    details TEXT DEFAULT '',
    props TEXT DEFAULT '{}',
    created_at TEXT,
    updated_at TEXT
);


CREATE TABLE templates (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    icon TEXT DEFAULT '📋',
    description TEXT DEFAULT '',
    content_json TEXT NOT NULL,
    created_at TEXT,
    updated_at TEXT
);


CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    stripe_customer_id TEXT,
    subscription_status TEXT DEFAULT 'inactive',
    subscription_ends_at TEXT,
    created_at TEXT
);


CREATE TABLE password_reset_tokens (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    token TEXT NOT NULL UNIQUE,
    expires_at TEXT,
    used INTEGER DEFAULT 0,
    created_at TEXT
);


CREATE TABLE healthplanet_tokens (
    id INTEGER PRIMARY KEY,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    expires_at TEXT,
    scope TEXT,
    created_at TEXT,
    updated_at TEXT
);

-- Create indexes
CREATE INDEX idx_pages_parent_position ON pages(parent_id, position);
CREATE INDEX idx_blocks_page_position ON blocks(page_id, position);

-- Insert data

-- users: 1 rows
INSERT INTO users (id,username,password_hash,created_at,stripe_customer_id,subscription_status,subscription_ends_at) VALUES (1,'nnnkeita@gmail.com','scrypt:32768:8:1$FDxBG4pTF86KQIBs$c2383efc60d5b35ee48393a090056befac68b1cd8da3682fc3f4324b3b06e1ef319c7c4f0d703e2a7fef9a556aa90a66b18ff15205325a698aa0f26f15074cea','2026-02-01 07:53:44','cus_TtjexijvsiiUCB','active','2026-02-15T07:53:44.353371');

-- templates: 3 rows
INSERT INTO templates (id,name,icon,description,content_json,created_at,updated_at) VALUES (1,'感謝日記','🙏','毎日の感謝を記録するテンプレート','{"title": "感謝日記", "blocks": [{"type": "h1", "content": "感謝日記", "position": 1000}, {"type": "text", "content": "今日感謝したことを3つ書きましょう。", "position": 2000}, {"type": "text", "content": "1. ", "position": 3000}, {"type": "text", "content": "2. ", "position": 4000}, {"type": "text", "content": "3. ", "position": 5000}]}','2026-02-01 07:43:22','2026-02-01 07:43:22');
INSERT INTO templates (id,name,icon,description,content_json,created_at,updated_at) VALUES (2,'PDCA日報','📊','Plan-Do-Check-Actフレームワーク','{"title": "PDCA日報", "blocks": [{"type": "h1", "content": "PDCA日報", "position": 1000}, {"type": "h2", "content": "計画（Plan）", "position": 2000}, {"type": "text", "content": "", "position": 3000}, {"type": "h2", "content": "実行（Do）", "position": 4000}, {"type": "text", "content": "", "position": 5000}, {"type": "h2", "content": "確認（Check）", "position": 6000}, {"type": "text", "content": "", "position": 7000}, {"type": "h2", "content": "改善（Act）", "position": 8000}, {"type": "text", "content": "", "position": 9000}]}','2026-02-01 07:43:22','2026-02-01 07:43:22');
INSERT INTO templates (id,name,icon,description,content_json,created_at,updated_at) VALUES (3,'5行日記','📖','1日の出来事を5行で整理するテンプレート','{"title": "5行日記", "blocks": [{"type": "h1", "content": "5行日記", "position": 1000}, {"type": "text", "content": "1. 今日起きたこと：", "position": 2000}, {"type": "text", "content": "2. その時の気持ち：", "position": 3000}, {"type": "text", "content": "3. その出来事の意味：", "position": 4000}, {"type": "text", "content": "4. その経験から学んだこと：", "position": 5000}, {"type": "text", "content": "5. 明日への決意：", "position": 6000}]}','2026-02-01 07:43:22','2026-02-01 07:43:22');

-- pages: 90 rows
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (36,'2026年1月24日','📅','',NULL,'2026-01-24 07:46:18','2026-01-24 07:46:18',0,0,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (37,'日記','📝','',36,'2026-01-24 07:46:18','2026-01-24 07:46:18',0,0,0.0,0.0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (38,'筋トレ','🏋️','',36,'2026-01-24 07:46:18','2026-01-24 07:46:18',0,0,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (39,'英語学習','🌍','',36,'2026-01-24 07:46:18','2026-01-24 07:46:18',0,0,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (40,'読書メモ','📚','',NULL,'2026-01-25 00:34:42','2026-01-25 00:34:42',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (57,'2026年1月25日','📅','',NULL,'2026-01-25 01:22:44','2026-01-27 12:12:05',0,0,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (58,'日記','📝','',57,'2026-01-25 01:22:44','2026-01-25 01:22:44',0,0,0.0,0.0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (59,'筋トレ','🏋️','',57,'2026-01-25 01:22:44','2026-01-25 01:22:44',0,0,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (60,'英語学習','🌍','',57,'2026-01-25 01:22:44','2026-01-25 01:22:44',0,0,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (61,'2026年01月25日の記録','📝','',NULL,'2026-01-25 01:54:11','2026-01-25 01:54:11',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (62,'無題','📄','',NULL,'2026-01-25 02:02:49','2026-01-25 02:02:49',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (63,'あい','📄','',NULL,'2026-01-25 02:02:59','2026-01-25 02:04:15',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (64,'🔖 あとで調べる','🔖','',NULL,'2026-01-25 02:14:00','2026-01-25 02:14:00',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (65,'2026年1月27日','📅','',NULL,'2026-01-25 02:19:41','2026-01-25 02:19:41',0,0,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (66,'日記','📝','',65,'2026-01-25 02:19:41','2026-01-25 02:19:41',0,0,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (67,'筋トレ','🏋️','',65,'2026-01-25 02:19:41','2026-01-25 02:19:41',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (68,'英語学習','🌍','',65,'2026-01-25 02:19:41','2026-01-25 02:19:41',0,0,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (69,'2026年1月26日','📅','',NULL,'2026-01-25 21:30:16','2026-01-27 12:12:12',0,0,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (70,'日記','📝','',69,'2026-01-25 21:30:16','2026-01-25 21:30:16',0,0,0.0,0.0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (71,'筋トレ','🏋️','',69,'2026-01-25 21:30:16','2026-01-25 21:30:16',0,0,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (72,'英語学習','🌍','',69,'2026-01-25 21:30:16','2026-01-25 21:30:16',0,0,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (73,'無題','📄','',NULL,'2026-01-26 12:13:53','2026-01-26 12:13:53',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (74,'無題','📄','',NULL,'2026-01-26 12:23:04','2026-01-26 12:23:04',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (75,'2026年1月28日','📅','',NULL,'2026-01-27 11:49:58','2026-01-27 11:49:58',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (76,'日記','📝','',75,'2026-01-27 11:49:58','2026-01-27 11:49:58',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (77,'筋トレ','🏋️','',75,'2026-01-27 11:49:58','2026-01-27 11:49:58',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (78,'英語学習','🌍','',75,'2026-01-27 11:49:58','2026-01-27 11:49:58',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (79,'2026年1月28日','📅','',NULL,'2026-01-27 11:50:43','2026-01-27 11:50:43',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (80,'日記','📝','',79,'2026-01-27 11:50:43','2026-01-27 11:50:43',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (81,'筋トレ','🏋️','',79,'2026-01-27 11:50:43','2026-01-27 11:50:43',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (82,'英語学習','🌍','',79,'2026-01-27 11:50:43','2026-01-27 11:50:43',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (83,'2026年1月29日','📅','',NULL,'2026-01-27 11:51:07','2026-01-27 11:51:07',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (84,'日記','📝','',83,'2026-01-27 11:51:07','2026-01-27 11:51:07',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (85,'筋トレ','🏋️','',83,'2026-01-27 11:51:07','2026-01-27 11:51:07',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (86,'英語学習','🌍','',83,'2026-01-27 11:51:07','2026-01-27 11:51:07',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (87,'2026年1月28日','📅','',NULL,'2026-01-27 11:53:44','2026-01-27 11:53:44',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (88,'日記','📝','',87,'2026-01-27 11:53:44','2026-01-27 11:53:44',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (89,'筋トレ','🏋️','',87,'2026-01-27 11:53:44','2026-01-27 11:53:44',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (90,'英語学習','🌍','',87,'2026-01-27 11:53:44','2026-01-27 11:53:44',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (96,'筋トレのコピー','🏋️','',65,'2026-01-27 12:18:57','2026-01-27 12:18:57',0,0,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (97,'無題','📄','',NULL,'2026-01-27 21:26:48','2026-01-27 21:26:48',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (98,'2026年1月28日','📅','',NULL,'2026-01-28 03:13:43','2026-01-28 03:13:54',0,0,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (99,'日記','📝','',98,'2026-01-28 03:13:43','2026-01-28 03:13:43',0,0,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (100,'筋トレ','🏋️','',98,'2026-01-28 03:13:43','2026-01-28 03:13:43',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (101,'英語学習','🌍','',98,'2026-01-28 03:13:43','2026-01-28 03:13:43',0,0,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (102,'筋トレ','🏋️','',98,'2026-01-28 03:13:43','2026-01-28 11:37:59',0,0,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (103,'2026年1月29日','📅','',NULL,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (104,'日記','📝','',103,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (105,'筋トレ','🏋️','',103,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (106,'英語学習','🌍','',103,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (107,'筋トレのコピー','🏋️','',103,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (108,'2026年1月29日','📅','',NULL,'2026-01-28 11:41:11','2026-01-28 11:41:11',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (109,'日記','📝','',108,'2026-01-28 11:41:11','2026-01-28 11:41:11',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (110,'筋トレ','🏋️','',108,'2026-01-28 11:41:11','2026-01-28 11:41:11',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (111,'英語学習','🌍','',108,'2026-01-28 11:41:11','2026-01-28 11:41:11',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (112,'筋トレ','🏋️','',108,'2026-01-28 11:41:11','2026-01-28 11:41:11',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (113,'無題','📄','',NULL,'2026-01-28 11:46:33','2026-01-28 11:46:33',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (114,'2026年1月29日','📅','',NULL,'2026-01-28 11:49:45','2026-01-28 11:49:45',0,0,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (115,'日記','📝','',114,'2026-01-28 11:49:45','2026-01-28 11:49:45',0,0,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (116,'筋トレ','🏋️','',114,'2026-01-28 11:49:45','2026-01-28 11:49:45',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (117,'英語学習','🌍','',114,'2026-01-28 11:49:45','2026-01-28 11:49:45',0,0,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (118,'筋トレ','🏋️','',114,'2026-01-28 11:49:45','2026-01-28 11:49:45',0,0,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (119,'食事','🍽️','',114,'2026-01-28 11:49:45','2026-01-28 11:49:45',0,0,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (120,'無題','📄','',NULL,'2026-01-29 11:44:40','2026-01-29 11:44:40',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (121,'2026年1月30日','📅','',NULL,'2026-01-29 18:10:21','2026-01-29 18:10:21',0,0,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (122,'日記','📝','',121,'2026-01-29 18:10:21','2026-01-29 18:10:21',0,0,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (123,'筋トレ','🏋️','',121,'2026-01-29 18:10:21','2026-01-29 18:10:21',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (124,'英語学習','🌍','',121,'2026-01-29 18:10:21','2026-01-29 18:10:21',0,0,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (126,'食事','🍽️','',121,'2026-01-29 18:10:21','2026-01-29 18:10:21',0,1,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (127,'2026年1月31日','📅','',NULL,'2026-01-30 07:47:57','2026-01-30 07:47:57',0,0,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (128,'日記','📝','',127,'2026-01-30 07:47:57','2026-01-30 07:47:57',0,0,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (129,'筋トレ','🏋️','',127,'2026-01-30 07:47:57','2026-01-30 07:47:57',0,0,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (130,'英語学習','🌍','',127,'2026-01-30 07:47:57','2026-01-30 07:47:57',0,0,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (132,'食事','🍽️','',127,'2026-01-30 07:47:57','2026-01-30 07:47:57',0,0,0,0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (133,'2026年2月1日','📅','',NULL,'2026-02-01 00:32:14','2026-02-01 00:32:14',0,0,0,0.0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (134,'日記','📝','',133,'2026-02-01 00:32:14','2026-02-01 00:32:14',0,0,0,0.0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (135,'筋トレ','🏋️','',133,'2026-02-01 00:32:14','2026-02-01 00:32:14',0,0,0,0.0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (136,'英語学習','🌍','',133,'2026-02-01 00:32:14','2026-02-01 00:32:14',0,0,0,0.0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (137,'食事','🍽️','',133,'2026-02-01 00:32:14','2026-02-01 00:32:14',0,0,0,0.0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (138,'2026年2月4日','📅','',NULL,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,0,0,0.0,5,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (139,'日記','📝','',138,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,0,1000.0,0.0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (140,'筋トレ','🏋️','',138,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,0,2000.0,0.0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (141,'英語学習','🌍','',138,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,0,3000.0,0.0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (142,'食事','🍽️','',138,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,0,4000.0,0.0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (143,'2026年2月12日','📅','',NULL,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,0,0,0.0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (144,'日記','📝','',143,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,0,1000.0,0.0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (145,'筋トレ','🏋️','',143,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,0,2000.0,0.0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (146,'英語学習','🌍','',143,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,0,3000.0,0.0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (147,'食事','🍽️','',143,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,0,4000.0,0.0,0,'');
INSERT INTO pages (id,title,icon,cover_image,parent_id,created_at,updated_at,is_pinned,is_deleted,position,position_new,mood,gratitude_text) VALUES (148,'読書','📚','',143,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,0,5000.0,0.0,0,'');

-- blocks: 511 rows
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (111,36,'text','',0,0,'2026-01-24 07:46:18','2026-01-24 07:46:18',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (112,37,'h1','体調',0,0,'2026-01-24 07:46:18','2026-01-24 07:46:18',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (113,37,'text','


',0,1,'2026-01-24 07:46:18','2026-01-25 00:32:11',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (114,37,'h1','天気',0,2,'2026-01-24 07:46:18','2026-01-24 07:46:18',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (115,37,'text','



',0,3,'2026-01-24 07:46:18','2026-01-25 00:32:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (116,37,'h1','やったこと',0,4,'2026-01-24 07:46:18','2026-01-24 07:46:18',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (117,37,'todo','


',0,5,'2026-01-24 07:46:18','2026-01-25 00:39:32',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (118,37,'h1','振り返り',0,7,'2026-01-24 07:46:18','2026-01-25 00:32:03',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (119,37,'text','

',0,7,'2026-01-24 07:46:18','2026-01-25 00:39:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (120,38,'h1','今日のメニュー',0,0,'2026-01-24 07:46:18','2026-01-24 07:46:18',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (121,38,'todo','@3',0,1,'2026-01-24 07:46:18','2026-01-25 01:04:16',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (122,38,'h1','',0,2,'2026-01-24 07:46:18','2026-01-24 07:47:25',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (124,38,'h1','メモ',0,4,'2026-01-24 07:46:18','2026-01-24 07:46:18',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (125,38,'text','アブドミナル 45kg

①45②52③52

フライリアデルト25.0kg→31.5kg

①31.5②31.5③31.5

バックエクステンション52kg 

①52②58.5③58.5

ラットプル31.5→38.5kg

①38.5②38.5③38.5

チェストプレス25kg→31.5kg

①31.5②31.5③31.5

鉄アレイ8kg

①8②9③9

ぶら下がり',0,5,'2026-01-24 07:46:18','2026-01-24 07:47:07',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (126,39,'h1','今日の学習内容',0,0,'2026-01-24 07:46:18','2026-01-24 07:46:18',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (127,39,'text','英検１級　15分',0,1,'2026-01-24 07:46:18','2026-01-25 00:34:26',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (128,39,'h1','新しい単語',0,2,'2026-01-24 07:46:18','2026-01-24 07:46:18',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (129,39,'todo','',0,3,'2026-01-24 07:46:18','2026-01-24 07:46:18',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (130,39,'h1','発音練習',0,4,'2026-01-24 07:46:18','2026-01-24 07:46:18',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (131,39,'text','',0,5,'2026-01-24 07:46:18','2026-01-24 07:46:18',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (132,39,'h1','リスニング時間',0,6,'2026-01-24 07:46:18','2026-01-24 07:46:18',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (133,39,'text','',0,7,'2026-01-24 07:46:18','2026-01-24 07:46:18',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (134,39,'h1','気づいたこと',0,8,'2026-01-24 07:46:18','2026-01-24 07:46:18',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (135,39,'text','',0,9,'2026-01-24 07:46:18','2026-01-24 07:46:18',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (136,40,'h1','本のタイトル',0,0,'2026-01-25 00:34:42','2026-01-25 00:34:42',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (137,40,'text','',0,1,'2026-01-25 00:34:42','2026-01-25 00:34:42',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (138,40,'h1','著者',0,2,'2026-01-25 00:34:42','2026-01-25 00:34:42',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (139,40,'text','',0,3,'2026-01-25 00:34:42','2026-01-25 00:34:42',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (140,40,'h1','読んだ日',0,4,'2026-01-25 00:34:42','2026-01-25 00:34:42',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (141,40,'text','',0,5,'2026-01-25 00:34:42','2026-01-25 00:34:42',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (142,40,'h1','感想・メモ',0,6,'2026-01-25 00:34:42','2026-01-25 00:34:42',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (143,40,'text','',0,7,'2026-01-25 00:34:42','2026-01-25 00:34:42',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (242,57,'text','

',0,0,'2026-01-25 01:22:44','2026-01-27 11:19:35',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (243,58,'h1','体調',0,0,'2026-01-25 01:22:44','2026-01-25 01:22:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (244,58,'text','


',0,1,'2026-01-25 01:22:44','2026-01-25 01:22:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (245,58,'h1','天気',0,2,'2026-01-25 01:22:44','2026-01-25 01:22:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (246,58,'text','



',0,3,'2026-01-25 01:22:44','2026-01-25 01:22:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (247,58,'h1','やったこと',0,4,'2026-01-25 01:22:44','2026-01-25 01:22:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (248,58,'todo','


',0,5,'2026-01-25 01:22:44','2026-01-25 01:22:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (249,58,'h1','振り返り',0,7,'2026-01-25 01:22:44','2026-01-25 01:22:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (250,58,'text','

',0,7,'2026-01-25 01:22:44','2026-01-25 01:22:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (251,59,'h1','今日のメニュー',0,0,'2026-01-25 01:22:44','2026-01-25 01:22:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (252,59,'todo','❌今日はできなかった　ウィング休み',0,1,'2026-01-25 01:22:44','2026-01-25 09:55:23',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (253,59,'h1','',0,2,'2026-01-25 01:22:44','2026-01-25 01:22:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (254,59,'h1','メモ',0,4,'2026-01-25 01:22:44','2026-01-25 01:22:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (255,59,'text','アブドミナル 45kg

①45②52③52

フライリアデルト25.0kg→31.5kg

①31.5②31.5③31.5

バックエクステンション52kg 

①52②58.5③58.5

ラットプル31.5→38.5kg

①38.5②38.5③38.5

チェストプレス25kg→31.5kg

①31.5②31.5③31.5

鉄アレイ8kg

①8②9③9

ぶら下がり',0,5,'2026-01-25 01:22:44','2026-01-25 01:22:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (256,60,'h1','今日の学習内容',0,0,'2026-01-25 01:22:44','2026-01-25 01:22:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (257,60,'text','英検１級　15分　４ページ',0,1,'2026-01-25 01:22:44','2026-01-25 10:26:51',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (258,60,'h1','新しい単語',0,2,'2026-01-25 01:22:44','2026-01-25 01:22:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (259,60,'todo','🔹 ① 動作・行為を表す動詞／句動詞

alteration
→ （服などの）お直し、修正

fall prey to
→ ～の餌食になる

scoff at
→ ～を嘲笑する

lag behind
→ 遅れを取る

abstain from
→ ～を控える、棄権する

intervene (in)
→ （争いなどに）介入する

mediate (in)
→ 仲裁する

bask in
→ （賞賛・評価などを）享受する

renege on
→ （約束を）破る

respond well to
→ ～にうまく対応する

disseminate
→ （情報を）広める

divulge
→ （秘密などを）暴露する

infuse A with B
→ AにBを吹き込む

bank on
→ ～を当てにする

beef up
→ 強化する

boil down to
→ 結局～に帰着する

botch up
→ 台無しにする

bail out
→ （経済的に）救済する

balk at
→ ～に尻込みする

🔹 ② 状態・性質・評価を表す語

amiable
→ （人柄が）感じのよい

amicable
→ （関係が）友好的な

amity
→ 友好関係

inclined to
→ ～する気がある

engulfed in
→ ～に飲み込まれた

long-standing
→ 長年の

financially troubled
→ 財政難の

🔹 ③ 感情・内面・抽象語

premonition
→ 予感

zest (for life)
→ 活力、情熱

zeal
→ 熱意、熱狂

conscience
→ 良心

fate
→ 運命

emancipate
→ 解放する

🔹 ④ 社会・政治・制度関連

moderator
→ 司会者、進行役

dissent
→ 異議、反対意見

outburst
→ 感情の爆発

general amnesty
→ 一般恩赦

political prisoner
→ 政治犯

coalition government
→ 連立政権

proxy
→ 代理

protocol
→ 手順、取り決め

proxy server
→ 代理サーバー

🔹 ⑤ 名詞句・表現（そのまま使える）

sheer luck
→ 純粋な運

bottled-up feelings
→ 抑え込まれた感情

acting up
→ 調子が悪い

lecture series
→ 講演シリーズ

🎯 英検1級的・今日の重要語TOP5（優先復習）

boil down to

fall prey to

disseminate / divulge

intervene / mediate

proxy / protocol',0,3,'2026-01-25 01:22:44','2026-01-25 10:29:16',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (260,60,'h1','発音練習',0,4,'2026-01-25 01:22:44','2026-01-25 01:22:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (261,60,'text','',0,5,'2026-01-25 01:22:44','2026-01-25 01:22:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (262,60,'h1','リスニング時間',0,6,'2026-01-25 01:22:44','2026-01-25 01:22:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (263,60,'text','',0,7,'2026-01-25 01:22:44','2026-01-25 01:22:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (264,60,'h1','気づいたこと',0,8,'2026-01-25 01:22:44','2026-01-25 01:22:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (265,60,'text','',0,9,'2026-01-25 01:22:44','2026-01-25 01:22:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (266,61,'h1','体調',0,1000,'2026-01-25 01:54:11','2026-01-25 01:54:11',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (267,61,'text','',0,2000,'2026-01-25 01:54:11','2026-01-25 01:54:11',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (268,61,'h1','天気',0,3000,'2026-01-25 01:54:11','2026-01-25 01:54:11',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (269,61,'text','',0,4000,'2026-01-25 01:54:11','2026-01-25 01:54:11',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (270,61,'h1','やったこと',0,5000,'2026-01-25 01:54:11','2026-01-25 01:54:11',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (271,61,'todo','',0,6000,'2026-01-25 01:54:11','2026-01-25 01:54:11',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (272,61,'h1','振り返り',0,7000,'2026-01-25 01:54:11','2026-01-25 01:54:11',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (273,61,'text','',0,8000,'2026-01-25 01:54:11','2026-01-25 01:54:11',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (274,62,'text','',0,1000,'2026-01-25 02:02:49','2026-01-25 02:02:49',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (275,63,'text','あい
記事
英語
日本語

',0,1000,'2026-01-25 02:02:59','2026-01-25 02:04:16',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (276,64,'text','昼休みに英単語
自動読み上げ機
ダイソー

',0,1000,'2026-01-25 02:14:00','2026-01-29 10:27:47',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (277,65,'text','後で調べるは一つにまとめる
本のページは使いやすく
速読 本を読みながら音楽ってどう？',0,1000,'2026-01-25 02:19:41','2026-01-27 10:12:49',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (278,66,'h1','',0,1000,'2026-01-25 02:19:41','2026-01-25 23:34:10',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (280,66,'h1','天気',0,3000,'2026-01-25 02:19:41','2026-01-25 02:19:41',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (281,66,'text','－５度　晴れ',0,4000,'2026-01-25 02:19:41','2026-01-27 11:16:48',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (282,66,'h1','読書',0,0,'2026-01-25 02:19:41','2026-01-28 11:43:25',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (284,66,'h1','振り返り',0,7000,'2026-01-25 02:19:41','2026-01-25 02:19:41',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (285,66,'text','クレーン組み立て作業計画書なかった反省
ジェームズ・クリア　1.01の法則

',0,8000,'2026-01-25 02:19:41','2026-01-27 11:18:10',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (286,67,'h1','今日のメニュー',0,1000,'2026-01-25 02:19:41','2026-01-25 02:19:41',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (287,67,'todo','',0,2000,'2026-01-25 02:19:41','2026-01-25 02:19:41',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (288,67,'h1','セット・回数',0,3000,'2026-01-25 02:19:41','2026-01-25 02:19:41',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (289,67,'text','',0,4000,'2026-01-25 02:19:41','2026-01-25 02:19:41',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (290,67,'h1','メモ',0,5000,'2026-01-25 02:19:41','2026-01-25 02:19:41',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (291,67,'text','',0,6000,'2026-01-25 02:19:41','2026-01-25 02:19:41',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (292,68,'h1','今日の学習内容',0,1000,'2026-01-25 02:19:41','2026-01-25 02:19:41',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (293,68,'text','',0,2000,'2026-01-25 02:19:41','2026-01-25 02:19:41',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (294,68,'h1','新しい単語',0,3000,'2026-01-25 02:19:41','2026-01-25 02:19:41',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (295,68,'todo','',0,4000,'2026-01-25 02:19:41','2026-01-25 02:19:41',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (296,68,'h1','発音練習',0,5000,'2026-01-25 02:19:41','2026-01-25 02:19:41',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (297,68,'text','',0,6000,'2026-01-25 02:19:41','2026-01-25 02:19:41',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (298,68,'h1','リスニング時間',0,7000,'2026-01-25 02:19:41','2026-01-25 02:19:41',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (299,68,'text','',0,8000,'2026-01-25 02:19:41','2026-01-25 02:19:41',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (300,68,'h1','気づいたこと',0,9000,'2026-01-25 02:19:41','2026-01-25 02:19:41',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (301,68,'text','',0,10000,'2026-01-25 02:19:41','2026-01-25 02:19:41',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (302,69,'text','魚AI？　浮世絵マシーン使ってみたい

ウェルビーイング

＃自宅

産廃看板　
産廃表示　
産廃ねっと
ダイソーで照明買う
本についてはページ数を入力するだけにしたい
インデックス
',0,0,'2026-01-25 21:30:16','2026-01-26 12:07:06',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (303,70,'h1','ランニング',0,0,'2026-01-25 21:30:16','2026-01-25 23:34:14',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (304,70,'text','×　寝坊！！　明日こそは
',0,1,'2026-01-25 21:30:16','2026-01-29 00:46:53',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (305,70,'h1','天気',0,2,'2026-01-25 21:30:16','2026-01-25 21:30:16',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (306,70,'text','晴　-4くらい


',0,3,'2026-01-25 21:30:16','2026-01-27 01:15:57',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (307,70,'h1','読書',0,4,'2026-01-25 21:30:16','2026-01-27 11:16:21',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (308,70,'todo','●おーい竜馬
○0P

●完全なる経営
◯5P

●ゴールドマンサックス
○5P
',0,5,'2026-01-25 21:30:16','2026-01-29 00:47:39',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (309,70,'h1','',0,7,'2026-01-25 21:30:16','2026-01-29 00:47:11',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (310,70,'text','●スリーグッドシングス
・持ち込み機械について勉強
・
・

',0,7,'2026-01-25 21:30:16','2026-01-29 00:47:47',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (311,71,'h1','今日のメニュー',0,0,'2026-01-25 21:30:16','2026-01-25 21:30:16',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (312,71,'todo','❌今日はできなかった　ウィング休み',0,1,'2026-01-25 21:30:16','2026-01-25 21:30:16',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (313,71,'h1','',0,2,'2026-01-25 21:30:16','2026-01-25 21:30:16',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (314,71,'h1','メモ',0,4,'2026-01-25 21:30:16','2026-01-25 21:30:16',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (315,71,'text','
アブドミナル 45kg

①45②52③52

フライリアデルト25.0kg→31.5kg

①31.5②31.5③31.5

バックエクステンション52kg 

①52②58.5③58.5

ラットプル31.5→38.5kg

①38.5②38.5③38.5

チェストプレス25kg→31.5kg

①31.5②31.5③31.5

鉄アレイ8kg

①8②9③9

ぶら下がり',0,5,'2026-01-25 21:30:16','2026-01-26 12:07:59',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (316,72,'h1','今日の学習内容',0,0,'2026-01-25 21:30:16','2026-01-25 21:30:16',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (317,72,'text','英検１級　20分　長文４ページ
',0,1,'2026-01-25 21:30:16','2026-01-29 00:47:58',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (318,72,'h1','新しい単語',0,2,'2026-01-25 21:30:16','2026-01-25 21:30:16',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (321,72,'text','（Gamma-ray bursts）

🌌 宇宙・科学系

 gamma-ray burst (GRB)：ガンマ線バースト

 neutron star：中性子星

 electromagnetic radiation：電磁放射線

 ultraviolet rays：紫外線

 ozone layer：オゾン層

☄️ 影響・結果（1級頻出）

 devastating (to ~)：壊滅的な

 wipe out ~：～を一掃する／絶滅させる

 deplete ~：～を枯渇させる

 usher in ~：～の時代を招く

 impact (v.)：～に影響を与える

🧠 抽象・論理語彙（差がつく）

 ripple effect：波及効果

 paradox：逆説

 relegate ~ to ...：～を…に追いやる

 pose a riddle/question：謎・疑問を投げかける

 theorize (that ~)：～と理論づける

🌍 数量・確率・頻度表現

 countless numbers of ~：無数の～

 roughly / some ~：およそ～

 a 60% chance that ~：～の確率が60%

 five times more frequent：5倍頻繁に

 within the last 1 billion years：過去10億年以内に

⭐ 構文・定型表現（即使える）

 be believed to ~：～と考えられている

 be unlikely to ~ anytime soon：近いうちに～しそうにない

 in astrophysics lingo：天体物理学用語では',0,5,'2026-01-25 21:30:16','2026-01-29 00:49:31',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (324,72,'h1','気づいたこと',0,8,'2026-01-25 21:30:16','2026-01-25 21:30:16',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (326,62,'calorie','ご飯
せんべい汁　
豚肉
納豆

',0,2000,'2026-01-26 12:05:31','2026-01-26 12:06:27',0,'','{"items":[{"amount":"1食","input":"ご飯","kcal":240,"matched":"ご飯","unit":"1杯(150g)"},{"amount":"-","input":"せんべい汁","kcal":null,"matched":null,"unit":"不明"},{"amount":"100g","input":"豚肉","kcal":250,"matched":"豚肉","unit":"100g"},{"amount":"1食","input":"納豆","kcal":100,"matched":"納豆","unit":"1パック"}],"note":"目安の計算です。食材や調理法で変動します。","total_kcal":590}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (327,63,'calorie','ご飯
せんべい汁
卵
味噌汁
',0,2000,'2026-01-26 12:09:17','2026-01-26 12:09:39',0,'','{"items":[{"amount":"1食","input":"ご飯","is_estimated":false,"kcal":240,"matched":"ご飯","unit":"1杯(150g)"},{"amount":"180ml","input":"せんべい汁","is_estimated":false,"kcal":80,"matched":"汁物","unit":"1杯(180ml)"},{"amount":"1食","input":"卵","is_estimated":false,"kcal":80,"matched":"卵","unit":"1個"},{"amount":"180ml","input":"味噌汁","is_estimated":false,"kcal":80,"matched":"汁物","unit":"1杯(180ml)"}],"note":"目安の計算です。食材や調理法で変動します。","total_kcal":480}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (328,71,'todo','',0,1005,'2026-01-26 12:11:38','2026-01-26 12:11:38',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (329,71,'todo','',0,2005,'2026-01-26 12:11:43','2026-01-26 12:11:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (330,73,'text','',0,1000,'2026-01-26 12:13:53','2026-01-26 12:13:53',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (331,73,'calorie','ごはん
卵
グラタン
昆布

',0,2000,'2026-01-26 12:13:58','2026-01-27 01:17:17',0,'','{"title":"朝飯","items":[{"amount":"-","input":"ごはん","is_estimated":true,"kcal":150,"matched":"不明(推定)","unit":"推定"},{"amount":"1食","input":"卵","is_estimated":false,"kcal":80,"matched":"卵","unit":"1個"},{"amount":"-","input":"グラタン","is_estimated":true,"kcal":150,"matched":"不明(推定)","unit":"推定"},{"amount":"-","input":"昆布","is_estimated":true,"kcal":150,"matched":"不明(推定)","unit":"推定"}],"note":"目安の計算です。食材や調理法で変動します。","total_kcal":530}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (332,73,'todo','',0,3000,'2026-01-26 12:14:45','2026-01-26 12:14:45',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (333,64,'todo','魚AI
',0,2000,'2026-01-26 12:18:45','2026-01-27 12:14:03',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (337,69,'text','',0,250,'2026-01-26 12:19:16','2026-01-26 12:19:16',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (342,74,'text','ああああ',0,1000,'2026-01-26 12:23:04','2026-01-26 12:23:56',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (343,74,'todo','あsあああああ',0,2000,'2026-01-26 12:23:10','2026-01-26 12:23:35',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (344,74,'todo','',0,1500,'2026-01-26 12:23:35','2026-01-26 12:23:35',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (345,74,'todo','',0,1750,'2026-01-26 12:23:36','2026-01-26 12:23:36',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (346,74,'todo','',0,1875,'2026-01-26 12:23:39','2026-01-26 12:23:39',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (347,74,'todo','',0,1250,'2026-01-26 12:23:52','2026-01-26 12:23:52',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (348,74,'todo','',0,1125,'2026-01-26 12:27:51','2026-01-26 12:27:51',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (351,69,'todo','',0,125,'2026-01-26 12:31:18','2026-01-26 12:31:18',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (352,70,'todo','',0,1007,'2026-01-27 01:16:21','2026-01-27 01:17:32',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (353,70,'todo','',0,507,'2026-01-27 01:16:22','2026-01-27 01:16:22',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (354,66,'text','ご飯
せんべい汁　
豚肉
納豆
',0,9000,'2026-01-27 11:17:18','2026-01-27 11:17:24',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (355,75,'text','後で調べるは一つにまとめる
本のページは使いやすく
速読 本を読みながら音楽ってどう？',0,1000,'2026-01-27 11:49:58','2026-01-27 11:49:58',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (356,76,'h1','',0,1000,'2026-01-27 11:49:58','2026-01-27 11:49:58',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (357,76,'text','',0,2000,'2026-01-27 11:49:58','2026-01-27 11:49:58',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (358,76,'h1','天気',0,3000,'2026-01-27 11:49:58','2026-01-27 11:49:58',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (359,76,'text','－５度　晴れ',0,4000,'2026-01-27 11:49:58','2026-01-27 11:49:58',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (360,76,'h1','読書',0,5000,'2026-01-27 11:49:58','2026-01-27 11:49:58',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (361,76,'todo','●おーい竜馬
○0P


●完全なる経営
◯5P


●ゴールドマンサックス
○10P
○5P',0,6000,'2026-01-27 11:49:58','2026-01-27 11:49:58',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (362,76,'h1','振り返り',0,7000,'2026-01-27 11:49:58','2026-01-27 11:49:58',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (363,76,'text','クレーン組み立て作業計画書なかった反省
ジェームズ・クリア　1.01の法則

',0,8000,'2026-01-27 11:49:58','2026-01-27 11:49:58',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (364,76,'text','ご飯
せんべい汁　
豚肉
納豆
',0,9000,'2026-01-27 11:49:58','2026-01-27 11:49:58',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (365,77,'h1','今日のメニュー',0,1000,'2026-01-27 11:49:58','2026-01-27 11:49:58',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (366,77,'todo','',0,2000,'2026-01-27 11:49:58','2026-01-27 11:49:58',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (367,77,'h1','セット・回数',0,3000,'2026-01-27 11:49:58','2026-01-27 11:49:58',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (368,77,'text','',0,4000,'2026-01-27 11:49:58','2026-01-27 11:49:58',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (369,77,'h1','メモ',0,5000,'2026-01-27 11:49:58','2026-01-27 11:49:58',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (370,77,'text','',0,6000,'2026-01-27 11:49:58','2026-01-27 11:49:58',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (371,78,'h1','今日の学習内容',0,1000,'2026-01-27 11:49:58','2026-01-27 11:49:58',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (372,78,'text','',0,2000,'2026-01-27 11:49:58','2026-01-27 11:49:58',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (373,78,'h1','新しい単語',0,3000,'2026-01-27 11:49:58','2026-01-27 11:49:58',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (374,78,'todo','',0,4000,'2026-01-27 11:49:58','2026-01-27 11:49:58',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (375,78,'h1','発音練習',0,5000,'2026-01-27 11:49:58','2026-01-27 11:49:58',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (376,78,'text','',0,6000,'2026-01-27 11:49:58','2026-01-27 11:49:58',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (377,78,'h1','リスニング時間',0,7000,'2026-01-27 11:49:58','2026-01-27 11:49:58',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (378,78,'text','',0,8000,'2026-01-27 11:49:58','2026-01-27 11:49:58',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (379,78,'h1','気づいたこと',0,9000,'2026-01-27 11:49:58','2026-01-27 11:49:58',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (380,78,'text','',0,10000,'2026-01-27 11:49:58','2026-01-27 11:49:58',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (381,79,'text','後で調べるは一つにまとめる
本のページは使いやすく
速読 本を読みながら音楽ってどう？',0,1000,'2026-01-27 11:50:43','2026-01-27 11:50:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (382,80,'h1','',0,1000,'2026-01-27 11:50:43','2026-01-27 11:50:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (383,80,'text','',0,2000,'2026-01-27 11:50:43','2026-01-27 11:50:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (384,80,'h1','天気',0,3000,'2026-01-27 11:50:43','2026-01-27 11:50:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (385,80,'text','－５度　晴れ',0,4000,'2026-01-27 11:50:43','2026-01-27 11:50:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (386,80,'h1','読書',0,5000,'2026-01-27 11:50:43','2026-01-27 11:50:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (387,80,'todo','●おーい竜馬
○0P


●完全なる経営
◯5P


●ゴールドマンサックス
○10P
○5P',0,6000,'2026-01-27 11:50:43','2026-01-27 11:50:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (388,80,'h1','振り返り',0,7000,'2026-01-27 11:50:43','2026-01-27 11:50:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (389,80,'text','クレーン組み立て作業計画書なかった反省
ジェームズ・クリア　1.01の法則

',0,8000,'2026-01-27 11:50:43','2026-01-27 11:50:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (390,80,'text','ご飯
せんべい汁　
豚肉
納豆
',0,9000,'2026-01-27 11:50:43','2026-01-27 11:50:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (391,81,'h1','今日のメニュー',0,1000,'2026-01-27 11:50:43','2026-01-27 11:50:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (392,81,'todo','',0,2000,'2026-01-27 11:50:43','2026-01-27 11:50:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (393,81,'h1','セット・回数',0,3000,'2026-01-27 11:50:43','2026-01-27 11:50:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (394,81,'text','',0,4000,'2026-01-27 11:50:43','2026-01-27 11:50:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (395,81,'h1','メモ',0,5000,'2026-01-27 11:50:43','2026-01-27 11:50:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (396,81,'text','',0,6000,'2026-01-27 11:50:43','2026-01-27 11:50:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (397,82,'h1','今日の学習内容',0,1000,'2026-01-27 11:50:43','2026-01-27 11:50:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (398,82,'text','',0,2000,'2026-01-27 11:50:43','2026-01-27 11:50:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (399,82,'h1','新しい単語',0,3000,'2026-01-27 11:50:43','2026-01-27 11:50:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (400,82,'todo','',0,4000,'2026-01-27 11:50:43','2026-01-27 11:50:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (401,82,'h1','発音練習',0,5000,'2026-01-27 11:50:43','2026-01-27 11:50:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (402,82,'text','',0,6000,'2026-01-27 11:50:43','2026-01-27 11:50:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (403,82,'h1','リスニング時間',0,7000,'2026-01-27 11:50:43','2026-01-27 11:50:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (404,82,'text','',0,8000,'2026-01-27 11:50:43','2026-01-27 11:50:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (405,82,'h1','気づいたこと',0,9000,'2026-01-27 11:50:43','2026-01-27 11:50:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (406,82,'text','',0,10000,'2026-01-27 11:50:43','2026-01-27 11:50:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (407,83,'text','後で調べるは一つにまとめる
本のページは使いやすく
速読 本を読みながら音楽ってどう？',0,1000,'2026-01-27 11:51:07','2026-01-27 11:51:07',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (408,84,'h1','',0,1000,'2026-01-27 11:51:07','2026-01-27 11:51:07',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (409,84,'text','',0,2000,'2026-01-27 11:51:07','2026-01-27 11:51:07',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (410,84,'h1','天気',0,3000,'2026-01-27 11:51:07','2026-01-27 11:51:07',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (411,84,'text','－５度　晴れ',0,4000,'2026-01-27 11:51:07','2026-01-27 11:51:07',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (412,84,'h1','読書',0,5000,'2026-01-27 11:51:07','2026-01-27 11:51:07',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (413,84,'todo','●おーい竜馬
○0P


●完全なる経営
◯5P


●ゴールドマンサックス
○10P
○5P',0,6000,'2026-01-27 11:51:07','2026-01-27 11:51:07',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (414,84,'h1','振り返り',0,7000,'2026-01-27 11:51:07','2026-01-27 11:51:07',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (415,84,'text','クレーン組み立て作業計画書なかった反省
ジェームズ・クリア　1.01の法則

',0,8000,'2026-01-27 11:51:07','2026-01-27 11:51:07',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (416,84,'text','ご飯
せんべい汁　
豚肉
納豆
',0,9000,'2026-01-27 11:51:07','2026-01-27 11:51:07',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (417,85,'h1','今日のメニュー',0,1000,'2026-01-27 11:51:07','2026-01-27 11:51:07',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (418,85,'todo','',0,2000,'2026-01-27 11:51:07','2026-01-27 11:51:07',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (419,85,'h1','セット・回数',0,3000,'2026-01-27 11:51:07','2026-01-27 11:51:07',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (420,85,'text','',0,4000,'2026-01-27 11:51:07','2026-01-27 11:51:07',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (421,85,'h1','メモ',0,5000,'2026-01-27 11:51:07','2026-01-27 11:51:07',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (422,85,'text','',0,6000,'2026-01-27 11:51:07','2026-01-27 11:51:07',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (423,86,'h1','今日の学習内容',0,1000,'2026-01-27 11:51:07','2026-01-27 11:51:07',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (424,86,'text','',0,2000,'2026-01-27 11:51:07','2026-01-27 11:51:07',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (425,86,'h1','新しい単語',0,3000,'2026-01-27 11:51:07','2026-01-27 11:51:07',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (426,86,'todo','',0,4000,'2026-01-27 11:51:07','2026-01-27 11:51:07',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (427,86,'h1','発音練習',0,5000,'2026-01-27 11:51:07','2026-01-27 11:51:07',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (428,86,'text','',0,6000,'2026-01-27 11:51:07','2026-01-27 11:51:07',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (429,86,'h1','リスニング時間',0,7000,'2026-01-27 11:51:07','2026-01-27 11:51:07',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (430,86,'text','',0,8000,'2026-01-27 11:51:07','2026-01-27 11:51:07',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (431,86,'h1','気づいたこと',0,9000,'2026-01-27 11:51:07','2026-01-27 11:51:07',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (432,86,'text','',0,10000,'2026-01-27 11:51:07','2026-01-27 11:51:07',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (433,87,'text','後で調べるは一つにまとめる
本のページは使いやすく
速読 本を読みながら音楽ってどう？',0,1000,'2026-01-27 11:53:44','2026-01-27 11:53:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (434,88,'h1','',0,1000,'2026-01-27 11:53:44','2026-01-27 11:53:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (435,88,'text','',0,2000,'2026-01-27 11:53:44','2026-01-27 11:53:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (436,88,'h1','天気',0,3000,'2026-01-27 11:53:44','2026-01-27 11:53:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (437,88,'text','－５度　晴れ',0,4000,'2026-01-27 11:53:44','2026-01-27 11:53:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (438,88,'h1','読書',0,5000,'2026-01-27 11:53:44','2026-01-27 11:53:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (439,88,'todo','●おーい竜馬
○0P


●完全なる経営
◯5P


●ゴールドマンサックス
○10P
○5P',0,6000,'2026-01-27 11:53:44','2026-01-27 11:53:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (440,88,'h1','振り返り',0,7000,'2026-01-27 11:53:44','2026-01-27 11:53:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (441,88,'text','クレーン組み立て作業計画書なかった反省
ジェームズ・クリア　1.01の法則

',0,8000,'2026-01-27 11:53:44','2026-01-27 11:53:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (442,88,'text','ご飯
せんべい汁　
豚肉
納豆
',0,9000,'2026-01-27 11:53:44','2026-01-27 11:53:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (443,89,'h1','今日のメニュー',0,1000,'2026-01-27 11:53:44','2026-01-27 11:53:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (444,89,'todo','',0,2000,'2026-01-27 11:53:44','2026-01-27 11:53:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (445,89,'h1','セット・回数',0,3000,'2026-01-27 11:53:44','2026-01-27 11:53:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (446,89,'text','',0,4000,'2026-01-27 11:53:44','2026-01-27 11:53:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (447,89,'h1','メモ',0,5000,'2026-01-27 11:53:44','2026-01-27 11:53:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (448,89,'text','',0,6000,'2026-01-27 11:53:44','2026-01-27 11:53:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (449,90,'h1','今日の学習内容',0,1000,'2026-01-27 11:53:44','2026-01-27 11:53:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (450,90,'text','',0,2000,'2026-01-27 11:53:44','2026-01-27 11:53:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (451,90,'h1','新しい単語',0,3000,'2026-01-27 11:53:44','2026-01-27 11:53:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (452,90,'todo','',0,4000,'2026-01-27 11:53:44','2026-01-27 11:53:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (453,90,'h1','発音練習',0,5000,'2026-01-27 11:53:44','2026-01-27 11:53:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (454,90,'text','',0,6000,'2026-01-27 11:53:44','2026-01-27 11:53:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (455,90,'h1','リスニング時間',0,7000,'2026-01-27 11:53:44','2026-01-27 11:53:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (456,90,'text','',0,8000,'2026-01-27 11:53:44','2026-01-27 11:53:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (457,90,'h1','気づいたこと',0,9000,'2026-01-27 11:53:44','2026-01-27 11:53:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (458,90,'text','',0,10000,'2026-01-27 11:53:44','2026-01-27 11:53:44',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (459,91,'text','',0,1000,'2026-01-27 11:53:55','2026-01-27 11:53:55',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (488,96,'h1','今日のメニュー',0,0,'2026-01-27 12:18:57','2026-01-27 12:18:57',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (489,96,'todo','',1,1,'2026-01-27 12:18:57','2026-01-27 12:19:32',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (490,96,'h1','',0,2,'2026-01-27 12:18:57','2026-01-27 12:18:57',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (491,96,'h1','メモ',0,4,'2026-01-27 12:18:57','2026-01-27 12:18:57',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (492,96,'text','
アブドミナル 45kg

①45②52③52

フライリアデルト25.0kg→31.5kg

①31.5②31.5③31.5

バックエクステンション52kg 

①52②58.5③58.5

ラットプル31.5→38.5kg

①38.5②38.5③38.5

チェストプレス25kg→31.5kg

①31.5②31.5③31.5

鉄アレイ8kg

①8②9③9

ぶら下がり',0,5,'2026-01-27 12:18:57','2026-01-27 12:18:57',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (497,66,'book','',0,5,'2026-01-27 12:31:19','2026-01-29 10:31:18',0,'','{"title":"●おーい竜馬","currentPage":390}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (498,66,'book','',0,502.5,'2026-01-27 12:32:00','2026-01-29 10:39:29',0,'','{"title":"ゴールドマンサックス王国の光と影","currentPage":80}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (499,66,'book','',0,751.25,'2026-01-27 12:32:03','2026-01-27 12:32:24',0,'','{"title":"完全なる経営"}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (500,97,'text','',0,1000,'2026-01-27 21:26:48','2026-01-27 21:26:48',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (501,98,'text','後で調べるは一つにまとめる
本のページは使いやすく
速読 本を読みながら音楽ってどう？',0,1000,'2026-01-28 03:13:43','2026-01-28 03:13:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (502,99,'book','',0,5,'2026-01-28 03:13:43','2026-01-28 03:14:04',0,'','{"title":"完全なる経営"}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (503,99,'book','',0,502.5,'2026-01-28 03:13:43','2026-01-28 03:14:08',0,'','{"title":"おーい竜馬"}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (504,99,'book','',0,751.25,'2026-01-28 03:13:43','2026-01-28 03:13:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (505,99,'h1','',0,1000,'2026-01-28 03:13:43','2026-01-28 03:13:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (506,99,'h1','天気',0,0,'2026-01-28 03:13:43','2026-01-28 11:43:46',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (507,99,'text','－3度　晴れ',0,1,'2026-01-28 03:13:43','2026-01-28 11:43:55',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (508,99,'h1','読書',0,0,'2026-01-28 03:13:43','2026-01-28 11:45:07',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (509,99,'h1','振り返り',0,7000,'2026-01-28 03:13:43','2026-01-28 03:13:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (510,99,'text','持ち込み機械点検表
り',0,8000,'2026-01-28 03:13:43','2026-01-28 11:44:29',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (511,99,'text','ご飯
たらこ
ニジマス？
鶏肉味噌汁

',0,9000,'2026-01-28 03:13:43','2026-01-28 11:52:28',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (512,100,'h1','今日のメニュー',0,1000,'2026-01-28 03:13:43','2026-01-28 03:13:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (513,100,'todo','',0,2000,'2026-01-28 03:13:43','2026-01-28 03:13:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (514,100,'h1','セット・回数',0,3000,'2026-01-28 03:13:43','2026-01-28 03:13:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (515,100,'text','',0,4000,'2026-01-28 03:13:43','2026-01-28 03:13:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (516,100,'h1','メモ',0,5000,'2026-01-28 03:13:43','2026-01-28 03:13:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (517,100,'text','',0,6000,'2026-01-28 03:13:43','2026-01-28 03:13:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (518,101,'h1','今日の学習内容',0,1000,'2026-01-28 03:13:43','2026-01-28 03:13:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (519,101,'text','🔑 今日の重要語彙まとめ
1️⃣ enduring
意味：長く続く、永続的な

例：enduring influence（永続的な影響）

✍️ 抽象論・歴史・政治系で超頻出

2️⃣ gain A through B
意味：Bを通じてAを得る

例：gain influence through public support

✍️ 因果関係をスマートに言える1級必須構文

3️⃣ ties to the masses
意味：大衆との結びつき

masses = 一般市民・庶民層

✍️ populism / democracy 論で使える

4️⃣ solidify one’s political grip
意味：政治的支配を固める

grip = 支配・掌握

✍️ 政治史・権力構造の説明で強い表現

5️⃣ power base
意味：権力の基盤・支持層

例：The poor formed its power base.

✍️ 抽象度が高く、論文調で使える

6️⃣ represent / represented
意味：代表する／象徴する

語源：re（再び）＋present（前に出す）

イメージ：
👉「本人がいない代わりに、存在・意思・数を前に出す」

✍️ 抽象語の理解として今日の重要ポイント

7️⃣ set out to ~
意味：〜しようと着手する

例：set out to court voters

✍️ フォーマル・論説向き

8️⃣ assimilate
意味：同化する・社会に溶け込む

例：immigrants assimilate into society

✍️ 移民・文化・教育テーマで頻出

9️⃣ extinct
意味：絶滅した

例：extinct species

✍️ 環境・生物系の定番語

🔟 by definition
意味：定義上、当然

例：Extinct species are, by definition, gone forever.

✍️ 論理を締める便利フレーズ

1️⃣1️⃣ resurrect / resurrection
意味：復活させる／復活

文脈：絶滅種の復活・科学技術

✍️ 倫理・テクノロジー論で映える語

1️⃣2️⃣ clone
意味：クローン化する

✍️ 科学系の基本語（だが正確さが問われる）

1️⃣3️⃣ controversy
意味：論争

例：The controversy surrounding robotic surgery

✍️ 1級超頻出「論点提示ワード」

1️⃣4️⃣ low-level / repetitive tasks
意味：単純作業／反復作業

✍️ AI・ロボット・労働論で使える

1️⃣5️⃣ free up
意味：（時間・人手を）解放する

例：free up human surgeons

✍️ 書き言葉でも口語でも使える万能句

🎯 今日の総評（講師として一言）
語彙レベルは完全に英検1級ゾーン

特に
gain through / represent / power base / set out to
この辺を“意味＋イメージ”で掴めているのが非常に良い
',0,2000,'2026-01-28 03:13:43','2026-01-28 11:37:00',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (528,102,'h1','今日のランニング',0,0,'2026-01-28 03:13:43','2026-01-28 11:45:23',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (529,102,'todo','',0,1,'2026-01-28 03:13:43','2026-01-28 11:45:37',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (530,102,'h1','',0,2,'2026-01-28 03:13:43','2026-01-28 03:13:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (531,102,'h1','ジム @5',0,4,'2026-01-28 03:13:43','2026-01-28 11:46:08',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (532,102,'text','
アブドミナル 45kg

①45②52③52

フライリアデルト25.0kg→31.5kg

①31.5②31.5③31.5

バックエクステンション52kg 

①52②58.5③58.5

ラットプル31.5→38.5kg

①38.5②38.5③38.5

チェストプレス25kg→31.5kg

①31.5②31.5③31.5

鉄アレイ8kg

①8②9③9

ぶら下がり',0,5,'2026-01-28 03:13:43','2026-01-28 03:13:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (533,102,'todo','9.1km',1,1,'2026-01-28 03:13:43','2026-01-28 11:45:58',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (534,102,'todo','',0,2005,'2026-01-28 03:13:43','2026-01-28 03:13:43',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (535,103,'text','後で調べるは一つにまとめる
本のページは使いやすく
速読 本を読みながら音楽ってどう？',0,1000,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (536,104,'book','',0,5,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (537,104,'book','',0,502.5,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (538,104,'book','',0,751.25,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (539,104,'h1','',0,1000,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (540,104,'h1','天気',0,3000,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (541,104,'text','－3度　晴れ',0,4000,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (542,104,'h1','読書',0,5000,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (543,104,'h1','振り返り',0,7000,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (544,104,'text','持ち込み機械点検表

',0,8000,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (545,104,'text','ご飯
せんべい汁　
豚肉
納豆
',0,9000,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (546,105,'h1','今日のメニュー',0,1000,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (547,105,'todo','',0,2000,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (548,105,'h1','セット・回数',0,3000,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (549,105,'text','',0,4000,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (550,105,'h1','メモ',0,5000,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (551,105,'text','',0,6000,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (552,106,'h1','今日の学習内容',0,1000,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (553,106,'text','',0,2000,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (554,106,'h1','新しい単語',0,3000,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (555,106,'todo','',0,4000,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (556,106,'h1','発音練習',0,5000,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (557,106,'text','',0,6000,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (558,106,'h1','リスニング時間',0,7000,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (559,106,'text','',0,8000,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (560,106,'h1','気づいたこと',0,9000,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (561,106,'text','',0,10000,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (562,107,'h1','今日のメニュー',0,0,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (563,107,'todo','',1,1,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (564,107,'h1','',0,2,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (565,107,'h1','メモ',0,4,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (566,107,'text','
アブドミナル 45kg

①45②52③52

フライリアデルト25.0kg→31.5kg

①31.5②31.5③31.5

バックエクステンション52kg 

①52②58.5③58.5

ラットプル31.5→38.5kg

①38.5②38.5③38.5

チェストプレス25kg→31.5kg

①31.5②31.5③31.5

鉄アレイ8kg

①8②9③9

ぶら下がり',0,5,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (567,107,'todo','',0,1005,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (568,107,'todo','',0,2005,'2026-01-28 11:31:27','2026-01-28 11:31:27',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (569,108,'text','後で調べるは一つにまとめる
本のページは使いやすく
速読 本を読みながら音楽ってどう？',0,1000,'2026-01-28 11:41:11','2026-01-28 11:41:11',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (570,109,'book','',0,5,'2026-01-28 11:41:11','2026-01-28 11:41:11',0,'','{"title":"完全なる経営"}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (571,109,'book','',0,502.5,'2026-01-28 11:41:11','2026-01-28 11:41:11',0,'','{"title":"おーい竜馬"}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (572,109,'book','',0,751.25,'2026-01-28 11:41:11','2026-01-28 11:41:11',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (573,109,'h1','',0,1000,'2026-01-28 11:41:11','2026-01-28 11:41:11',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (574,109,'h1','天気',0,3000,'2026-01-28 11:41:11','2026-01-28 11:41:11',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (575,109,'text','－3度　晴れ',0,4000,'2026-01-28 11:41:11','2026-01-28 11:41:11',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (576,109,'h1','読書',0,5000,'2026-01-28 11:41:11','2026-01-28 11:41:11',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (577,109,'h1','振り返り',0,7000,'2026-01-28 11:41:11','2026-01-28 11:41:11',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (578,109,'text','持ち込み機械点検表

',0,8000,'2026-01-28 11:41:11','2026-01-28 11:41:11',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (579,109,'text','ご飯
せんべい汁　
豚肉
納豆
',0,9000,'2026-01-28 11:41:11','2026-01-28 11:41:11',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (580,110,'h1','今日のメニュー',0,1000,'2026-01-28 11:41:11','2026-01-28 11:41:11',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (581,110,'todo','',0,2000,'2026-01-28 11:41:11','2026-01-28 11:41:11',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (582,110,'h1','セット・回数',0,3000,'2026-01-28 11:41:11','2026-01-28 11:41:11',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (583,110,'text','',0,4000,'2026-01-28 11:41:11','2026-01-28 11:41:11',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (584,110,'h1','メモ',0,5000,'2026-01-28 11:41:11','2026-01-28 11:41:11',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (585,110,'text','',0,6000,'2026-01-28 11:41:11','2026-01-28 11:41:11',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (586,111,'h1','今日の学習内容',0,1000,'2026-01-28 11:41:11','2026-01-28 11:41:11',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (587,111,'text','🔑 今日の重要語彙まとめ
1️⃣ enduring
意味：長く続く、永続的な

例：enduring influence（永続的な影響）

✍️ 抽象論・歴史・政治系で超頻出

2️⃣ gain A through B
意味：Bを通じてAを得る

例：gain influence through public support

✍️ 因果関係をスマートに言える1級必須構文

3️⃣ ties to the masses
意味：大衆との結びつき

masses = 一般市民・庶民層

✍️ populism / democracy 論で使える

4️⃣ solidify one’s political grip
意味：政治的支配を固める

grip = 支配・掌握

✍️ 政治史・権力構造の説明で強い表現

5️⃣ power base
意味：権力の基盤・支持層

例：The poor formed its power base.

✍️ 抽象度が高く、論文調で使える

6️⃣ represent / represented
意味：代表する／象徴する

語源：re（再び）＋present（前に出す）

イメージ：
👉「本人がいない代わりに、存在・意思・数を前に出す」

✍️ 抽象語の理解として今日の重要ポイント

7️⃣ set out to ~
意味：〜しようと着手する

例：set out to court voters

✍️ フォーマル・論説向き

8️⃣ assimilate
意味：同化する・社会に溶け込む

例：immigrants assimilate into society

✍️ 移民・文化・教育テーマで頻出

9️⃣ extinct
意味：絶滅した

例：extinct species

✍️ 環境・生物系の定番語

🔟 by definition
意味：定義上、当然

例：Extinct species are, by definition, gone forever.

✍️ 論理を締める便利フレーズ

1️⃣1️⃣ resurrect / resurrection
意味：復活させる／復活

文脈：絶滅種の復活・科学技術

✍️ 倫理・テクノロジー論で映える語

1️⃣2️⃣ clone
意味：クローン化する

✍️ 科学系の基本語（だが正確さが問われる）

1️⃣3️⃣ controversy
意味：論争

例：The controversy surrounding robotic surgery

✍️ 1級超頻出「論点提示ワード」

1️⃣4️⃣ low-level / repetitive tasks
意味：単純作業／反復作業

✍️ AI・ロボット・労働論で使える

1️⃣5️⃣ free up
意味：（時間・人手を）解放する

例：free up human surgeons

✍️ 書き言葉でも口語でも使える万能句

🎯 今日の総評（講師として一言）
語彙レベルは完全に英検1級ゾーン

特に
gain through / represent / power base / set out to
この辺を“意味＋イメージ”で掴めているのが非常に良い
',0,2000,'2026-01-28 11:41:11','2026-01-28 11:41:11',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (588,112,'h1','今日のメニュー',0,0,'2026-01-28 11:41:11','2026-01-28 11:41:11',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (589,112,'todo','',1,1,'2026-01-28 11:41:11','2026-01-28 11:41:11',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (590,112,'h1','',0,2,'2026-01-28 11:41:11','2026-01-28 11:41:11',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (591,112,'h1','メモ',0,4,'2026-01-28 11:41:11','2026-01-28 11:41:11',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (592,112,'text','
アブドミナル 45kg

①45②52③52

フライリアデルト25.0kg→31.5kg

①31.5②31.5③31.5

バックエクステンション52kg 

①52②58.5③58.5

ラットプル31.5→38.5kg

①38.5②38.5③38.5

チェストプレス25kg→31.5kg

①31.5②31.5③31.5

鉄アレイ8kg

①8②9③9

ぶら下がり',0,5,'2026-01-28 11:41:11','2026-01-28 11:41:11',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (593,112,'todo','',0,1005,'2026-01-28 11:41:11','2026-01-28 11:41:11',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (594,112,'todo','',0,2005,'2026-01-28 11:41:11','2026-01-28 11:41:11',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (595,66,'text','',0,4500,'2026-01-28 11:43:09','2026-01-28 11:43:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (596,99,'todo','',0,2000,'2026-01-28 11:44:54','2026-01-28 11:44:54',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (597,113,'text','',0,1000,'2026-01-28 11:46:33','2026-01-28 11:46:33',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (598,114,'text','後で調べるは一つにまとめる
本のページは使いやすく
速読 本を読みながら音楽ってどう？
７分瞑想
要はこういうこと
',0,1000,'2026-01-28 11:49:45','2026-01-29 09:22:00',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (599,115,'h1','天気',0,0,'2026-01-28 11:49:45','2026-01-28 11:49:45',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (600,115,'h1','読書',0,0,'2026-01-28 11:49:45','2026-01-28 11:49:45',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (601,115,'text','－3度　晴れ',0,1,'2026-01-28 11:49:45','2026-01-28 11:49:45',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (602,115,'book','',0,5,'2026-01-28 11:49:45','2026-01-28 11:49:45',0,'','{"title":"完全なる経営"}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (603,115,'book','',0,502.5,'2026-01-28 11:49:45','2026-01-28 23:39:59',0,'','{"title":"おーい竜馬","currentPage":10}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (604,115,'book','',0,751.25,'2026-01-28 11:49:45','2026-01-28 23:40:02',0,'','{"title":"ゴールドマンサックス","currentPage":10}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (605,115,'h1','',0,1000,'2026-01-28 11:49:45','2026-01-28 11:49:45',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (606,115,'todo','',0,2000,'2026-01-28 11:49:45','2026-01-28 11:49:45',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (607,115,'h1','振り返り',0,7000,'2026-01-28 11:49:45','2026-01-28 11:49:45',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (608,115,'text','持ち込み機械点検表 システム作成
機械　分電盤点検表　システム作成
システム作成能力上がった
吉田産業より嘆願される。
寝坊によりジョギングできなかったのがショック
',0,8000,'2026-01-28 11:49:45','2026-01-29 07:51:50',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (609,115,'text','',0,9000,'2026-01-28 11:49:45','2026-01-29 07:50:56',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (610,116,'h1','今日のメニュー',0,1000,'2026-01-28 11:49:45','2026-01-28 11:49:45',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (611,116,'todo','',0,2000,'2026-01-28 11:49:45','2026-01-28 11:49:45',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (612,116,'h1','セット・回数',0,3000,'2026-01-28 11:49:45','2026-01-28 11:49:45',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (613,116,'text','',0,4000,'2026-01-28 11:49:45','2026-01-28 11:49:45',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (614,116,'h1','メモ',0,5000,'2026-01-28 11:49:45','2026-01-28 11:49:45',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (615,116,'text','',0,6000,'2026-01-28 11:49:45','2026-01-28 11:49:45',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (616,117,'h1','今日の学習内容',0,1000,'2026-01-28 11:49:45','2026-01-28 11:49:45',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (617,117,'text','🔑 今日の重要語彙まとめ
1️⃣ enduring
意味：長く続く、永続的な

例：enduring influence（永続的な影響）

✍️ 抽象論・歴史・政治系で超頻出

2️⃣ gain A through B
意味：Bを通じてAを得る

例：gain influence through public support

✍️ 因果関係をスマートに言える1級必須構文

3️⃣ ties to the masses
意味：大衆との結びつき

masses = 一般市民・庶民層

✍️ populism / democracy 論で使える

4️⃣ solidify one’s political grip
意味：政治的支配を固める

grip = 支配・掌握

✍️ 政治史・権力構造の説明で強い表現

5️⃣ power base
意味：権力の基盤・支持層

例：The poor formed its power base.

✍️ 抽象度が高く、論文調で使える

6️⃣ represent / represented
意味：代表する／象徴する

語源：re（再び）＋present（前に出す）

イメージ：
👉「本人がいない代わりに、存在・意思・数を前に出す」

✍️ 抽象語の理解として今日の重要ポイント

7️⃣ set out to ~
意味：〜しようと着手する

例：set out to court voters

✍️ フォーマル・論説向き

8️⃣ assimilate
意味：同化する・社会に溶け込む

例：immigrants assimilate into society

✍️ 移民・文化・教育テーマで頻出

9️⃣ extinct
意味：絶滅した

例：extinct species

✍️ 環境・生物系の定番語

🔟 by definition
意味：定義上、当然

例：Extinct species are, by definition, gone forever.

✍️ 論理を締める便利フレーズ

1️⃣1️⃣ resurrect / resurrection
意味：復活させる／復活

文脈：絶滅種の復活・科学技術

✍️ 倫理・テクノロジー論で映える語

1️⃣2️⃣ clone
意味：クローン化する

✍️ 科学系の基本語（だが正確さが問われる）

1️⃣3️⃣ controversy
意味：論争

例：The controversy surrounding robotic surgery

✍️ 1級超頻出「論点提示ワード」

1️⃣4️⃣ low-level / repetitive tasks
意味：単純作業／反復作業

✍️ AI・ロボット・労働論で使える

1️⃣5️⃣ free up
意味：（時間・人手を）解放する

例：free up human surgeons

✍️ 書き言葉でも口語でも使える万能句

🎯 今日の総評（講師として一言）
語彙レベルは完全に英検1級ゾーン

特に
gain through / represent / power base / set out to
この辺を“意味＋イメージ”で掴めているのが非常に良い
',0,2000,'2026-01-28 11:49:45','2026-01-28 11:49:45',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (618,118,'h1','今日のランニング',0,0,'2026-01-28 11:49:45','2026-01-28 11:49:45',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (620,118,'todo','9.1km',1,1,'2026-01-28 11:49:45','2026-01-28 11:49:45',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (621,118,'h1','',0,2,'2026-01-28 11:49:45','2026-01-28 11:49:45',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (622,118,'h1','ジム @6',0,4,'2026-01-28 11:49:45','2026-01-29 10:03:17',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (623,118,'text','
アブドミナル 45kg

①45②52③52

フライリアデルト25.0kg→31.5kg

①31.5②31.5③31.5

バックエクステンション52kg 

①52②58.5③58.5

ラットプル31.5→38.5kg

①38.5②38.5③38.5

チェストプレス25kg→31.5kg

①31.5②31.5③31.5

鉄アレイ8kg

①8②9③9

ぶら下がり',0,5,'2026-01-28 11:49:45','2026-01-28 11:49:45',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (624,118,'todo','',0,2005,'2026-01-28 11:49:45','2026-01-28 11:49:45',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (625,119,'todo','',0,1000,'2026-01-28 11:50:24','2026-01-28 11:50:24',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (626,119,'calorie','ご飯１杯　
卵
牛肉１皿
味噌汁

昼ごはん
弁当

',0,2000,'2026-01-28 11:50:35','2026-01-28 11:51:46',0,'','{"items":[{"amount":"1食","input":"ご飯１杯","is_estimated":false,"kcal":240,"matched":"ご飯","unit":"1杯(150g)"},{"amount":"1食","input":"卵","is_estimated":false,"kcal":80,"matched":"卵","unit":"1個"},{"amount":"100g","input":"牛肉１皿","is_estimated":false,"kcal":280,"matched":"牛肉","unit":"100g"},{"amount":"180ml","input":"味噌汁","is_estimated":false,"kcal":80,"matched":"汁物","unit":"1杯(180ml)"},{"amount":"-","input":"昼ごはん","is_estimated":true,"kcal":150,"matched":"不明(推定)","unit":"推定"},{"amount":"1食","input":"弁当","is_estimated":false,"kcal":500,"matched":"弁当","unit":"1個"}],"note":"目安の計算です。食材や調理法で変動します。","total_kcal":1330}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (628,64,'todo','',0,3000,'2026-01-29 10:48:10','2026-01-29 10:48:10',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (629,117,'speak','🔑 今日の重要語彙まとめ
1️⃣ enduring
意味：長く続く、永続的な

',0,3000,'2026-01-29 11:36:31','2026-01-29 11:43:55',0,'','{"lang":"ja-JP","rate":1}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (630,117,'speak','明日　　tomorrow',0,4000,'2026-01-29 11:43:58','2026-01-29 11:44:09',0,'','{"lang":"ja-JP","rate":1}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (631,120,'text','っk
',0,1000,'2026-01-29 11:44:40','2026-01-29 11:47:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (632,120,'speak','明日aaa',0,2000,'2026-01-29 11:44:43','2026-01-29 11:45:03',0,'','{"lang":"ja-JP","rate":1}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (633,120,'speak','aaaa',0,1500,'2026-01-29 11:47:10','2026-01-29 11:47:24',0,'','{"lang":"en-US","rate":1.6}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (634,121,'text','後で調べるは一つにまとめる
本のページは使いやすく
速読 本を読みながら音楽ってどう？
７分瞑想
要はこういうこと
単語帳買う
発音記号覚える
項目ごとのリンク
もう少し音声システム精度上げる
ポジティブタスク
ネガティブタスクを使い分け
ペンを用意',0,1000,'2026-01-29 18:10:21','2026-01-30 11:52:30',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (635,122,'h1','天気',0,0,'2026-01-29 18:10:21','2026-01-29 18:10:21',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (636,122,'h1','読書',0,0,'2026-01-29 18:10:21','2026-01-29 18:10:21',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (637,122,'text','－3度　晴れ',0,1,'2026-01-29 18:10:21','2026-01-29 18:10:21',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (638,122,'book','',0,5,'2026-01-29 18:10:21','2026-01-29 22:04:13',0,'','{"title":"完全なる経営","currentPage":300}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (639,122,'book','',0,502.5,'2026-01-29 18:10:21','2026-01-29 22:04:40',0,'','{"title":"おーい竜馬","currentPage":0}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (640,122,'book','',0,751.25,'2026-01-29 18:10:21','2026-01-29 22:04:35',0,'','{"title":"ゴールドマンサックス","currentPage":90}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (641,122,'h1','',0,1000,'2026-01-29 18:10:21','2026-01-29 18:10:21',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (642,122,'todo','',0,2000,'2026-01-29 18:10:21','2026-01-29 18:10:21',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (643,122,'h1','振り返り',0,7000,'2026-01-29 18:10:21','2026-01-29 18:10:21',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (644,122,'text','止水板　チェックバックいただいたまだ甘い
鉄板はいだのを指摘された
杭工事設計説明会無事に終了',0,8000,'2026-01-29 18:10:21','2026-01-30 07:17:28',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (645,122,'text','',0,9000,'2026-01-29 18:10:21','2026-01-29 18:10:21',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (646,123,'h1','今日のメニュー',0,1000,'2026-01-29 18:10:21','2026-01-29 18:10:21',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (647,123,'todo','',0,2000,'2026-01-29 18:10:21','2026-01-29 18:10:21',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (648,123,'h1','セット・回数',0,3000,'2026-01-29 18:10:21','2026-01-29 18:10:21',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (649,123,'text','',0,4000,'2026-01-29 18:10:21','2026-01-29 18:10:21',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (650,123,'h1','メモ',0,5000,'2026-01-29 18:10:21','2026-01-29 18:10:21',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (651,123,'text','',0,6000,'2026-01-29 18:10:21','2026-01-29 18:10:21',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (652,124,'h1','今日の学習内容',0,1000,'2026-01-29 18:10:21','2026-01-29 18:10:21',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (653,124,'text','
',0,2000,'2026-01-29 18:10:21','2026-01-30 00:07:19',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (655,124,'speak','建築・評価・原因関係
	•	inspired：触発された／着想を得た
	•	constraint / constrained：制約（を受けた）
	•	removal：撤去
	•	greenery：緑地、植栽
	•	inferior：劣った、質の低い

⸻

経済・理論・変化
	•	underwent：経験した、経た
	•	regulated：規制された、統制された
	•	catastrophe：大惨事、破局
	•	turmoil：混乱、動乱
	•	unrestricted：制限のない、自由な

⸻

市場・行動・結果
	•	desirous：強く望んでいる
	•	trillions：数兆（ドルなど）
	•	borne（bearの過去分詞）：負担された、背負わされた
	•	self-correcting：自己修正する

⸻

新しい経済学・学際分野
	•	hypothesis：仮説
	•	perspective：観点、視点
	•	advocate：提唱者／擁護する
	•	mutation：変異、急激な変化
	•	merge：融合する
	•	neuroeconomics：神経経済学
	•	neuroscience：神経科学
	•	contend：主張する、論じる

⸻

抽象度の高い頻出語（英検1級）
	•	dominance：支配、優勢
	•	unlikely：ありそうもない
	•	unify / unifies：統合する
	•	model：理論モデル
	•	hybridization：融合、ハイブリッド化
	•	muddle (through)：混乱しながら何とか切り抜ける

⸻

🎯 使いこなしポイント（英検1級向け）
	•	**cause–effect（因果）**で使える語が多い
→ constraint, led to, resulted in, borne
	•	**評価語（批判・分析）**に直結
→ inferior, inefficient, irrational, unlikely
	•	抽象論・学際論で強い
→ hybridization, hypothesis, perspective
',0,4000,'2026-01-29 18:10:21','2026-01-30 21:49:23',0,'','{"lang":"en-US","rate":1}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (662,126,'todo','',0,1000,'2026-01-29 18:10:21','2026-01-29 18:10:21',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (663,126,'calorie','ご飯１杯　
卵
牛肉１皿
味噌汁

弁当

ご飯
納豆
牛乳
肉野菜
スープ

',0,2000,'2026-01-29 18:10:21','2026-01-30 21:52:35',0,'','{"items":[{"amount":"1食","input":"ご飯１杯","is_estimated":false,"kcal":240,"matched":"ご飯","unit":"1杯(150g)"},{"amount":"1食","input":"卵","is_estimated":false,"kcal":80,"matched":"卵","unit":"1個"},{"amount":"100g","input":"牛肉１皿","is_estimated":false,"kcal":280,"matched":"牛肉","unit":"100g"},{"amount":"180ml","input":"味噌汁","is_estimated":false,"kcal":80,"matched":"汁物","unit":"1杯(180ml)"},{"amount":"1食","input":"弁当","is_estimated":false,"kcal":500,"matched":"弁当","unit":"1個"},{"amount":"1食","input":"ご飯","is_estimated":false,"kcal":240,"matched":"ご飯","unit":"1杯(150g)"},{"amount":"1食","input":"納豆","is_estimated":false,"kcal":100,"matched":"納豆","unit":"1パック"},{"amount":"200ml","input":"牛乳","is_estimated":false,"kcal":130,"matched":"牛乳","unit":"200ml"},{"amount":"-","input":"肉野菜","is_estimated":true,"kcal":150,"matched":"不明(推定)","unit":"推定"},{"amount":"180ml","input":"スープ","is_estimated":false,"kcal":80,"matched":"汁物","unit":"1杯(180ml)"}],"note":"目安の計算です。食材や調理法で変動します。","total_kcal":1880,"title":"食事/カロリー　朝"}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (664,120,'speak','go back',0,3000,'2026-01-29 18:44:16','2026-01-29 18:44:49',0,'','{"lang":"en-US","rate":1}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (665,127,'text','後で調べるは一つにまとめる
大きい見出し追加作業
本のページは使いやすく
要はこういうこと
単語帳買う
発音記号覚える
項目ごとのリンク',0,1000,'2026-01-30 07:47:57','2026-01-31 10:03:22',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (666,128,'h1','天気',0,0,'2026-01-30 07:47:57','2026-01-30 07:47:57',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (667,128,'h1','読書',0,0,'2026-01-30 07:47:57','2026-01-30 07:47:57',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (668,128,'text','－3度　晴れ',0,1,'2026-01-30 07:47:57','2026-01-30 07:47:57',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (669,128,'book','',0,5,'2026-01-30 07:47:57','2026-01-30 07:47:57',0,'','{"title":"完全なる経営","currentPage":300}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (670,128,'book','',0,502.5,'2026-01-30 07:47:57','2026-01-30 07:47:57',0,'','{"title":"おーい竜馬","currentPage":0}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (671,128,'book','',0,751.25,'2026-01-30 07:47:57','2026-01-30 07:47:57',0,'','{"title":"ゴールドマンサックス","currentPage":90}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (672,128,'h1','',0,1000,'2026-01-30 07:47:57','2026-01-30 07:47:57',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (673,128,'todo','',0,2000,'2026-01-30 07:47:57','2026-01-30 07:47:57',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (674,128,'h1','振り返り',0,7000,'2026-01-30 07:47:57','2026-01-30 07:47:57',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (675,128,'text','止水板　チェックバックいただいたまだ甘い
鉄板はいだのを指摘された
杭工事設計説明会無事に終了',0,8000,'2026-01-30 07:47:57','2026-01-30 07:47:57',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (676,128,'text','',0,9000,'2026-01-30 07:47:57','2026-01-30 07:47:57',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (677,129,'h1','今日のメニュー',0,1000,'2026-01-30 07:47:57','2026-01-30 07:47:57',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (678,129,'todo','',0,2000,'2026-01-30 07:47:57','2026-01-30 07:47:57',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (679,129,'h1','セット・回数',0,3000,'2026-01-30 07:47:57','2026-01-30 07:47:57',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (680,129,'text','',0,4000,'2026-01-30 07:47:57','2026-01-30 07:47:57',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (681,129,'h1','メモ',0,5000,'2026-01-30 07:47:57','2026-01-30 07:47:57',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (682,129,'text','',0,6000,'2026-01-30 07:47:57','2026-01-30 07:47:57',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (683,130,'h1','今日の学習内容',0,1000,'2026-01-30 07:47:57','2026-01-30 07:47:57',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (684,130,'text','
',0,2000,'2026-01-30 07:47:57','2026-01-30 07:47:57',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (685,130,'speak','建築・評価・原因関係
	•	inspired：触発された／着想を得た
	•	constraint / constrained：制約（を受けた）
	•	removal：撤去
	•	greenery：緑地、植栽
	•	inferior：劣った、質の低い

⸻

経済・理論・変化
	•	underwent：経験した、経た
	•	regulated：規制された、統制された
	•	catastrophe：大惨事、破局
	•	turmoil：混乱、動乱
	•	unrestricted：制限のない、自由な

⸻

市場・行動・結果
	•	desirous：強く望んでいる
	•	trillions：数兆（ドルなど）
	•	borne（bearの過去分詞）：負担された、背負わされた
	•	self-correcting：自己修正する

⸻

新しい経済学・学際分野
	•	hypothesis：仮説
	•	perspective：観点、視点
	•	advocate：提唱者／擁護する
	•	mutation：変異、急激な変化
	•	merge：融合する
	•	neuroeconomics：神経経済学
	•	neuroscience：神経科学
	•	contend：主張する、論じる

⸻

抽象度の高い頻出語（英検1級）
	•	dominance：支配、優勢
	•	unlikely：ありそうもない
	•	unify / unifies：統合する
	•	model：理論モデル
	•	hybridization：融合、ハイブリッド化
	•	muddle (through)：混乱しながら何とか切り抜ける

⸻

🎯 使いこなしポイント（英検1級向け）
	•	**cause–effect（因果）**で使える語が多い
→ constraint, led to, resulted in, borne
	•	**評価語（批判・分析）**に直結
→ inferior, inefficient, irrational, unlikely
	•	抽象論・学際論で強い
→ hybridization, hypothesis, perspective
',0,4000,'2026-01-30 07:47:57','2026-01-31 10:05:10',0,'','{"lang":"auto","rate":2}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (692,132,'todo','',0,1000,'2026-01-30 07:47:57','2026-01-30 07:47:57',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (693,132,'calorie','ご飯１杯　
卵
牛肉１皿
味噌汁

昼ごはん
弁当

',0,2000,'2026-01-30 07:47:57','2026-01-30 07:47:57',0,'','{"items":[{"amount":"1食","input":"ご飯１杯","is_estimated":false,"kcal":240,"matched":"ご飯","unit":"1杯(150g)"},{"amount":"1食","input":"卵","is_estimated":false,"kcal":80,"matched":"卵","unit":"1個"},{"amount":"100g","input":"牛肉１皿","is_estimated":false,"kcal":280,"matched":"牛肉","unit":"100g"},{"amount":"180ml","input":"味噌汁","is_estimated":false,"kcal":80,"matched":"汁物","unit":"1杯(180ml)"},{"amount":"-","input":"昼ごはん","is_estimated":true,"kcal":150,"matched":"不明(推定)","unit":"推定"},{"amount":"1食","input":"弁当","is_estimated":false,"kcal":500,"matched":"弁当","unit":"1個"}],"note":"目安の計算です。食材や調理法で変動します。","total_kcal":1330}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (694,130,'speak','こんにちは
私の名前は音声読み上げだけのsiri
であります！！！！',0,5000,'2026-01-31 10:05:28','2026-01-31 10:06:11',0,'','{"lang":"ja-JP","rate":1}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (695,133,'text','後で調べるは一つにまとめる
大きい見出し追加作業
本のページは使いやすく
要はこういうこと
単語帳買う
発音記号覚える
項目ごとのリンク',0,1000,'2026-02-01 00:32:14','2026-02-01 00:32:14',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (696,134,'h1','天気',0,0,'2026-02-01 00:32:14','2026-02-01 00:32:14',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (697,134,'h1','読書',0,0,'2026-02-01 00:32:14','2026-02-01 00:32:14',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (698,134,'text','－3度　晴れ',0,1,'2026-02-01 00:32:14','2026-02-01 00:32:14',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (699,134,'book','',0,5,'2026-02-01 00:32:14','2026-02-01 00:32:14',0,'','{"title":"完全なる経営","currentPage":300}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (700,134,'book','',0,502.5,'2026-02-01 00:32:14','2026-02-01 00:32:14',0,'','{"title":"おーい竜馬","currentPage":0}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (701,134,'book','',0,751.25,'2026-02-01 00:32:14','2026-02-01 00:32:14',0,'','{"title":"ゴールドマンサックス","currentPage":90}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (702,134,'h1','',0,1000,'2026-02-01 00:32:14','2026-02-01 00:32:14',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (703,134,'todo','',0,2000,'2026-02-01 00:32:14','2026-02-01 00:32:14',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (704,134,'h1','振り返り',0,7000,'2026-02-01 00:32:14','2026-02-01 00:32:14',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (705,134,'text','止水板　チェックバックいただいたまだ甘い
鉄板はいだのを指摘された
杭工事設計説明会無事に終了',0,8000,'2026-02-01 00:32:14','2026-02-01 00:32:14',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (706,134,'text','',0,9000,'2026-02-01 00:32:14','2026-02-01 00:32:14',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (707,135,'h1','今日のメニュー',0,1000,'2026-02-01 00:32:14','2026-02-01 00:32:14',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (708,135,'todo','',0,2000,'2026-02-01 00:32:14','2026-02-01 00:32:14',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (709,135,'h1','セット・回数',0,3000,'2026-02-01 00:32:14','2026-02-01 00:32:14',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (710,135,'text','',0,4000,'2026-02-01 00:32:14','2026-02-01 00:32:14',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (711,135,'h1','メモ',0,5000,'2026-02-01 00:32:14','2026-02-01 00:32:14',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (712,135,'text','',0,6000,'2026-02-01 00:32:14','2026-02-01 00:32:14',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (713,136,'h1','今日の学習内容',0,1000,'2026-02-01 00:32:14','2026-02-01 00:32:14',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (714,136,'text','
',0,2000,'2026-02-01 00:32:14','2026-02-01 00:32:14',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (715,136,'speak','建築・評価・原因関係
	•	inspired：触発された／着想を得た
	•	constraint / constrained：制約（を受けた）
	•	removal：撤去
	•	greenery：緑地、植栽
	•	inferior：劣った、質の低い

⸻

経済・理論・変化
	•	underwent：経験した、経た
	•	regulated：規制された、統制された
	•	catastrophe：大惨事、破局
	•	turmoil：混乱、動乱
	•	unrestricted：制限のない、自由な

⸻

市場・行動・結果
	•	desirous：強く望んでいる
	•	trillions：数兆（ドルなど）
	•	borne（bearの過去分詞）：負担された、背負わされた
	•	self-correcting：自己修正する

⸻

新しい経済学・学際分野
	•	hypothesis：仮説
	•	perspective：観点、視点
	•	advocate：提唱者／擁護する
	•	mutation：変異、急激な変化
	•	merge：融合する
	•	neuroeconomics：神経経済学
	•	neuroscience：神経科学
	•	contend：主張する、論じる

⸻

抽象度の高い頻出語（英検1級）
	•	dominance：支配、優勢
	•	unlikely：ありそうもない
	•	unify / unifies：統合する
	•	model：理論モデル
	•	hybridization：融合、ハイブリッド化
	•	muddle (through)：混乱しながら何とか切り抜ける

⸻

🎯 使いこなしポイント（英検1級向け）
	•	**cause–effect（因果）**で使える語が多い
→ constraint, led to, resulted in, borne
	•	**評価語（批判・分析）**に直結
→ inferior, inefficient, irrational, unlikely
	•	抽象論・学際論で強い
→ hybridization, hypothesis, perspective
',0,4000,'2026-02-01 00:32:14','2026-02-01 00:32:14',0,'','{"lang":"auto","rate":2}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (716,136,'speak','こんにちは
私の名前は音声読み上げだけのsiri
であります！！！！',0,5000,'2026-02-01 00:32:14','2026-02-01 00:32:14',0,'','{"lang":"ja-JP","rate":1}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (717,137,'todo','',0,1000,'2026-02-01 00:32:14','2026-02-01 00:32:14',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (718,137,'calorie','ご飯１杯　
卵
牛肉１皿
味噌汁

昼ごはん
弁当

',0,2000,'2026-02-01 00:32:14','2026-02-01 00:32:14',0,'','{"items":[{"amount":"1食","input":"ご飯１杯","is_estimated":false,"kcal":240,"matched":"ご飯","unit":"1杯(150g)"},{"amount":"1食","input":"卵","is_estimated":false,"kcal":80,"matched":"卵","unit":"1個"},{"amount":"100g","input":"牛肉１皿","is_estimated":false,"kcal":280,"matched":"牛肉","unit":"100g"},{"amount":"180ml","input":"味噌汁","is_estimated":false,"kcal":80,"matched":"汁物","unit":"1杯(180ml)"},{"amount":"-","input":"昼ごはん","is_estimated":true,"kcal":150,"matched":"不明(推定)","unit":"推定"},{"amount":"1食","input":"弁当","is_estimated":false,"kcal":500,"matched":"弁当","unit":"1個"}],"note":"目安の計算です。食材や調理法で変動します。","total_kcal":1330}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (719,138,'text','',0,1000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (720,139,'h1','体調',0,1000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (721,139,'text','',0,2000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (722,139,'h1','天気',0,3000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (723,139,'text','',0,4000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (724,139,'h1','やったこと',0,5000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (725,139,'todo','',0,6000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (726,139,'h1','振り返り',0,7000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (727,139,'text','',0,8000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (728,140,'h1','今日のメニュー',0,1000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (729,140,'todo','',0,2000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (730,140,'h1','セット・回数',0,3000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (731,140,'text','',0,4000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (732,140,'h1','メモ',0,5000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (733,140,'text','',0,6000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (734,141,'h1','今日の学習内容',0,1000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (735,141,'text','',0,2000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (736,141,'h1','新しい単語',0,3000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (737,141,'todo','',0,4000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (738,141,'h1','発音練習',0,5000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (739,141,'text','',0,6000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (740,141,'h1','リスニング時間',0,7000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (741,141,'text','',0,8000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (742,141,'h1','気づいたこと',0,9000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (743,141,'text','',0,10000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (744,142,'h1','🌅 朝食',0,1000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (745,142,'todo','',0,2000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (746,142,'text','',0,3000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (747,142,'h1','🌞 昼食',0,4000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (748,142,'todo','',0,5000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (749,142,'text','',0,6000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (750,142,'h1','🌙 夕食',0,7000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (751,142,'todo','',0,8000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (752,142,'text','',0,9000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (753,142,'h1','カロリー記録',0,10000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (754,142,'calorie','',0,11000,'2026-02-04 12:55:34','2026-02-04 12:55:34',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (755,143,'text','',0,1000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (756,144,'h1','体調',0,1000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (757,144,'text','',0,2000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (758,144,'h1','天気',0,3000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (759,144,'text','',0,4000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (760,144,'h1','やったこと',0,5000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (761,144,'todo','',0,6000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (762,144,'h1','振り返り',0,7000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (763,144,'text','',0,8000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (764,145,'h1','今日のメニュー',0,1000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (765,145,'todo','',0,2000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (766,145,'h1','セット・回数',0,3000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (767,145,'text','',0,4000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (768,145,'h1','メモ',0,5000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (769,145,'text','',0,6000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (770,146,'h1','今日の学習内容',0,1000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (771,146,'text','',0,2000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (772,146,'h1','新しい単語',0,3000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (773,146,'todo','',0,4000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (774,146,'h1','発音練習',0,5000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (775,146,'text','',0,6000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (776,146,'h1','リスニング時間',0,7000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (777,146,'text','',0,8000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (778,146,'h1','気づいたこと',0,9000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (779,146,'text','',0,10000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (780,147,'h1','朝食',0,1000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (781,147,'text','',0,2000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (782,147,'h1','昼食',0,3000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (783,147,'text','',0,4000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (784,147,'h1','夕食',0,5000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (785,147,'text','',0,6000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (786,148,'h1','本のタイトル',0,1000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (787,148,'text','',0,2000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (788,148,'h1','著者',0,3000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (789,148,'text','',0,4000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (790,148,'h1','感想・メモ',0,5000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
INSERT INTO blocks (id,page_id,type,content,checked,position,created_at,updated_at,collapsed,details,props) VALUES (791,148,'text','',0,6000,'2026-02-12 12:09:09','2026-02-12 12:09:09',0,'','{}');
