"""NET_WATCH state management — SQLite for seen articles and category weights."""

import sqlite3
import threading
from config import DB_FILE, CATEGORIES

# Thread-local storage for DB connections (one per thread, reused)
_local = threading.local()


def _get_conn():
    """Return a thread-local DB connection (created once per thread)."""
    if not hasattr(_local, 'conn') or _local.conn is None:
        _local.conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        _local.conn.execute("PRAGMA journal_mode=WAL")
    return _local.conn


def init_db():
    """Creates tables and initializes default category weights."""
    conn = _get_conn()
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS seen_articles (url TEXT PRIMARY KEY)')
    c.execute('CREATE TABLE IF NOT EXISTS category_weights (category TEXT PRIMARY KEY, weight REAL)')

    for cat in CATEGORIES:
        c.execute("INSERT OR IGNORE INTO category_weights (category, weight) VALUES (?, ?)", (cat, 1.0))

    conn.commit()


def is_article_seen(url):
    c = _get_conn().cursor()
    c.execute("SELECT 1 FROM seen_articles WHERE url = ?", (url,))
    return c.fetchone() is not None


def is_batch_seen(urls):
    """Check multiple URLs at once. Returns set of URLs already seen."""
    if not urls:
        return set()
    conn = _get_conn()
    placeholders = ','.join('?' for _ in urls)
    c = conn.cursor()
    c.execute(f"SELECT url FROM seen_articles WHERE url IN ({placeholders})", list(urls))
    return {row[0] for row in c.fetchall()}


def mark_articles_seen(urls):
    """Mark multiple URLs as seen in one transaction."""
    if not urls:
        return
    conn = _get_conn()
    conn.executemany("INSERT OR IGNORE INTO seen_articles (url) VALUES (?)", [(u,) for u in urls])
    conn.commit()


def get_category_weights():
    c = _get_conn().cursor()
    c.execute("SELECT category, weight FROM category_weights")
    return dict(c.fetchall())


def update_category_weight(category, delta):
    conn = _get_conn()
    c = conn.cursor()
    c.execute("SELECT weight FROM category_weights WHERE category = ?", (category,))
    current = c.fetchone()
    if current:
        new_weight = max(0.1, current[0] + delta)
        c.execute("UPDATE category_weights SET weight = ? WHERE category = ?", (new_weight, category))
        conn.commit()


def cleanup_old_articles(keep_count=5000):
    """Remove oldest seen articles if table exceeds keep_count."""
    conn = _get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM seen_articles")
    count = c.fetchone()[0]
    if count > keep_count:
        c.execute(f"DELETE FROM seen_articles WHERE rowid IN "
                  f"(SELECT rowid FROM seen_articles ORDER BY rowid ASC LIMIT {count - keep_count})")
        conn.commit()
