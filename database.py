"""NET_WATCH state management — SQLite for seen articles and category weights."""

import sqlite3
from config import DB_FILE, CATEGORIES


def init_db():
    """Creates tables and initializes default category weights."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS seen_articles (url TEXT PRIMARY KEY)')
    c.execute('CREATE TABLE IF NOT EXISTS category_weights (category TEXT PRIMARY KEY, weight REAL)')

    for cat in CATEGORIES:
        c.execute("INSERT OR IGNORE INTO category_weights (category, weight) VALUES (?, ?)", (cat, 1.0))

    conn.commit()
    conn.close()


def is_article_seen(url):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT 1 FROM seen_articles WHERE url = ?", (url,))
    result = c.fetchone()
    conn.close()
    return bool(result)


def mark_article_seen(url):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO seen_articles (url) VALUES (?)", (url,))
    conn.commit()
    conn.close()


def get_category_weights():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT category, weight FROM category_weights")
    weights = dict(c.fetchall())
    conn.close()
    return weights


def update_category_weight(category, delta):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT weight FROM category_weights WHERE category = ?", (category,))
    current = c.fetchone()
    if current:
        new_weight = max(0.1, current[0] + delta)
        c.execute("UPDATE category_weights SET weight = ? WHERE category = ?", (new_weight, category))
        conn.commit()
    conn.close()
