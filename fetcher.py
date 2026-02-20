"""NET_WATCH feed fetching — RSS only."""

import random
import logging
from datetime import datetime, timedelta, timezone
from time import mktime
import feedparser
from config import CATEGORIES, MAX_ARTICLES_PER_FEED, MIN_ARTICLES_PER_CATEGORY, MAX_ARTICLES_PER_CATEGORY
from database import is_article_seen

logger = logging.getLogger(__name__)

# Articles older than this are skipped
MAX_AGE = timedelta(days=7)


def _parse_date(entry):
    """Extract a datetime from a feed entry, or None if unavailable."""
    for attr in ('published_parsed', 'updated_parsed'):
        parsed = getattr(entry, attr, None)
        if parsed:
            try:
                return datetime.fromtimestamp(mktime(parsed), tz=timezone.utc)
            except Exception:
                pass
    return None


ALLOWED_LANGS = {'en', 'sq', ''}  # English, Albanian, or unspecified


def _get_entry_lang(entry):
    """Get the language tag from a feed entry, normalized to 2-letter code."""
    lang = getattr(entry, 'language', '') or ''
    if not lang:
        # Some feeds put language on the summary_detail or title_detail
        for detail in ('title_detail', 'summary_detail'):
            d = getattr(entry, detail, None)
            if d and hasattr(d, 'language'):
                lang = d.language or ''
                break
    return lang[:2].lower()


def fetch_feed(url, category):
    """Fetches articles from an RSS feed URL, filtering out old and non-EN/SQ posts."""
    articles = []
    cutoff = datetime.now(timezone.utc) - MAX_AGE
    try:
        feed = feedparser.parse(url)
        source_name = feed.feed.get('title', 'RSS Feed')
        # Feed-level language
        feed_lang = (feed.feed.get('language', '') or '')[:2].lower()

        for entry in feed.entries[:MAX_ARTICLES_PER_FEED]:
            pub_date = _parse_date(entry)
            if pub_date and pub_date < cutoff:
                continue

            # Check entry-level or fall back to feed-level language
            entry_lang = _get_entry_lang(entry) or feed_lang
            if entry_lang and entry_lang not in ALLOWED_LANGS:
                continue

            articles.append({
                'title': entry.title,
                'url': entry.link,
                'category': category,
                'source': source_name,
                'date': pub_date,
            })
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
    return articles


def get_articles_batch(weights):
    """Returns a dict of {category: [articles]} with at least MIN per category, no duplicates."""
    sorted_cats = sorted(weights.keys(), key=lambda k: weights[k], reverse=True)
    result = {}

    for cat in sorted_cats:
        sources = list(CATEGORIES.get(cat, []))
        random.shuffle(sources)
        cat_articles = []
        seen_urls = set()

        for source in sources:
            articles = fetch_feed(source, cat)
            for article in articles:
                url = article['url']
                if url not in seen_urls and not is_article_seen(url):
                    seen_urls.add(url)
                    cat_articles.append(article)

        # Cap at MAX_ARTICLES_PER_CATEGORY
        if cat_articles:
            result[cat] = cat_articles[:MAX_ARTICLES_PER_CATEGORY]

    return result
