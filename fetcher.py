"""NET_WATCH feed fetching — RSS + Finnhub API with concurrent fetching."""

import logging
from datetime import datetime, timedelta, timezone
from time import mktime
from concurrent.futures import ThreadPoolExecutor, as_completed
from html import unescape
import re

import feedparser
import requests
from config import (
    CATEGORIES, HEADERS, MAX_ARTICLES_PER_FEED,
    FINNHUB_CATEGORIES, FINNHUB_MAX_ARTICLES,
)
from database import is_batch_seen

logger = logging.getLogger(__name__)

MAX_AGE = timedelta(days=3)
ALLOWED_LANGS = {'en', 'sq', ''}

# Reusable HTTP session
_session = requests.Session()
_session.headers.update(HEADERS)

# Finnhub API key
_finnhub_key = None


def init_finnhub(api_key):
    global _finnhub_key
    _finnhub_key = api_key


def _parse_date(entry):
    for attr in ('published_parsed', 'updated_parsed'):
        parsed = getattr(entry, attr, None)
        if parsed:
            try:
                return datetime.fromtimestamp(mktime(parsed), tz=timezone.utc)
            except Exception:
                pass
    return None


def _get_entry_lang(entry):
    lang = getattr(entry, 'language', '') or ''
    if not lang:
        for detail in ('title_detail', 'summary_detail'):
            d = getattr(entry, detail, None)
            if d and hasattr(d, 'language'):
                lang = d.language or ''
                break
    return lang[:2].lower()


_TAG_RE = re.compile(r'<[^>]+>')


def _extract_rss_summary(entry):
    """Extract a clean text summary from RSS entry description/summary."""
    raw = getattr(entry, 'summary', '') or getattr(entry, 'description', '') or ''
    if not raw:
        return ''
    text = _TAG_RE.sub('', raw)
    text = unescape(text).strip()
    return text[:500] if text else ''


def fetch_feed(url, category):
    """Fetch articles from one RSS feed. Returns list of article dicts."""
    articles = []
    cutoff = datetime.now(timezone.utc) - MAX_AGE
    try:
        feed = feedparser.parse(url)
        source_name = feed.feed.get('title', url.split('/')[2])
        feed_lang = (feed.feed.get('language', '') or '')[:2].lower()

        for entry in feed.entries[:MAX_ARTICLES_PER_FEED]:
            pub_date = _parse_date(entry)
            if pub_date and pub_date < cutoff:
                continue

            entry_lang = _get_entry_lang(entry) or feed_lang
            if entry_lang and entry_lang not in ALLOWED_LANGS:
                continue

            articles.append({
                'title': entry.title,
                'url': entry.link,
                'category': category,
                'source': source_name,
                'date': pub_date,
                'rss_summary': _extract_rss_summary(entry),
            })
    except Exception as e:
        logger.error(f"Feed error {url}: {e}")
    return articles


def fetch_finnhub():
    """Fetch market news from Finnhub API."""
    if not _finnhub_key:
        return []

    articles = []
    cutoff = datetime.now(timezone.utc) - MAX_AGE

    for fh_cat in FINNHUB_CATEGORIES:
        try:
            resp = _session.get(
                'https://finnhub.io/api/v1/news',
                params={'category': fh_cat, 'token': _finnhub_key},
                timeout=10,
            )
            resp.raise_for_status()

            for item in resp.json()[:FINNHUB_MAX_ARTICLES]:
                pub_date = datetime.fromtimestamp(item.get('datetime', 0), tz=timezone.utc)
                if pub_date < cutoff:
                    continue

                articles.append({
                    'title': item.get('headline', ''),
                    'url': item.get('url', ''),
                    'category': 'Market News',
                    'source': item.get('source', 'Finnhub'),
                    'date': pub_date,
                    'rss_summary': item.get('summary', ''),
                })
        except Exception as e:
            logger.error(f"Finnhub error ({fh_cat}): {e}")

    return articles


def _fetch_one(args):
    """Worker for concurrent feed fetching."""
    url, category = args
    return fetch_feed(url, category)


def get_all_articles():
    """Fetch all articles from all sources concurrently. Returns flat list, deduped."""
    # Build list of (url, category) tasks
    tasks = []
    for cat, sources in CATEGORIES.items():
        for url in sources:
            tasks.append((url, cat))

    # Fetch all feeds concurrently
    all_articles = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(_fetch_one, t): t for t in tasks}
        for future in as_completed(futures):
            try:
                all_articles.extend(future.result())
            except Exception as e:
                logger.error(f"Fetch worker error: {e}")

    # Add Finnhub articles
    all_articles.extend(fetch_finnhub())

    # Batch dedup against DB
    urls = [a['url'] for a in all_articles]
    seen = is_batch_seen(urls)
    unique = []
    local_seen = set()
    for article in all_articles:
        url = article['url']
        if url not in seen and url not in local_seen:
            local_seen.add(url)
            unique.append(article)

    logger.info(f"Fetched {len(all_articles)} raw, {len(unique)} new articles")
    return unique
