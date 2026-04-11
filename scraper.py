"""NET_WATCH article scraper — extracts body text with trafilatura + BeautifulSoup fallback."""

import logging
import requests
from config import HEADERS, MAX_SCRAPE_CHARS

logger = logging.getLogger(__name__)

_session = requests.Session()
_session.headers.update(HEADERS)

try:
    import trafilatura
    _HAS_TRAFILATURA = True
except ImportError:
    _HAS_TRAFILATURA = False
    logger.warning("trafilatura not installed — falling back to BeautifulSoup only")


def _extract_with_trafilatura(html):
    """Extract article text using trafilatura (better than raw BS4 for news sites)."""
    text = trafilatura.extract(html, include_comments=False, include_tables=False)
    return text.strip() if text else ''


def _extract_with_bs4(html):
    """Fallback: extract article text using BeautifulSoup."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'lxml')
    for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form']):
        tag.decompose()
    paragraphs = soup.find_all('p')
    text = " ".join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20)
    return text


def _fetch_html(url):
    """Fetch HTML with one retry on transient failures."""
    for attempt in range(2):
        try:
            resp = _session.get(url, timeout=15)
            resp.raise_for_status()
            return resp.content
        except requests.exceptions.ConnectionError:
            if attempt == 0:
                continue
        except requests.exceptions.Timeout:
            if attempt == 0:
                continue
        except requests.exceptions.HTTPError as e:
            # Don't retry client errors (403 paywall, 404 not found)
            if e.response is not None and e.response.status_code < 500:
                return None
            if attempt == 0:
                continue
        except Exception:
            return None
    return None


def scrape_article_text(url):
    """Extract main body text from an article URL. Returns empty string on failure."""
    try:
        html = _fetch_html(url)
        if not html:
            return ""

        # Try trafilatura first (much better at extracting article content)
        if _HAS_TRAFILATURA:
            text = _extract_with_trafilatura(html)
            if text and len(text) > 80:
                return text[:MAX_SCRAPE_CHARS]

        # Fallback to BeautifulSoup
        text = _extract_with_bs4(html)
        return text[:MAX_SCRAPE_CHARS] if text else ""

    except Exception as e:
        logger.error(f"Scrape error {url}: {e}")
        return ""
