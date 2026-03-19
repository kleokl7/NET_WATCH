"""NET_WATCH article scraper — extracts body text with BeautifulSoup."""

import logging
import requests
from bs4 import BeautifulSoup
from config import HEADERS, MAX_SCRAPE_CHARS

logger = logging.getLogger(__name__)

_session = requests.Session()
_session.headers.update(HEADERS)


def scrape_article_text(url):
    """Extract main body text from an article URL. Returns empty string on failure."""
    try:
        resp = _session.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, 'lxml')

        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form']):
            tag.decompose()

        paragraphs = soup.find_all('p')
        text = " ".join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20)
        return text[:MAX_SCRAPE_CHARS]
    except Exception as e:
        logger.error(f"Scrape error {url}: {e}")
        return ""
