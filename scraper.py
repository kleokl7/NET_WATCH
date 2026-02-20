"""NET_WATCH article scraper — extracts body text with BeautifulSoup."""

import logging
import requests
from bs4 import BeautifulSoup
from config import HEADERS

logger = logging.getLogger(__name__)


def scrape_article_text(url):
    """Extracts main body text from an article URL. Returns empty string on failure."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, 'html.parser')

        # Remove non-content elements
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()

        paragraphs = soup.find_all('p')
        text = " ".join(p.get_text(strip=True) for p in paragraphs)
        return text[:4000]
    except Exception as e:
        logger.error(f"Scraping error for {url}: {e}")
        return ""
