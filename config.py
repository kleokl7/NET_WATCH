"""NET_WATCH configuration — categories, feed URLs, constants."""

# User-Agent for HTTP requests
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 NetWatchBot/8.0'
}

# Gemini model for summarization and ranking
GEMINI_MODEL = 'gemini-2.5-flash'

# SQLite database file
DB_FILE = 'netwatch_state.db'

# Max articles to pull per RSS feed
MAX_ARTICLES_PER_FEED = 10

# Total articles to deliver per /news batch (after AI ranking)
MAX_ARTICLES_PER_BATCH = 15

# Max text sent to Gemini for summarization (tokens are proportional)
MAX_SCRAPE_CHARS = 1500

# Feed sources per category
CATEGORIES = {
    'Market News': [
        'https://feeds.bloomberg.com/markets/news.rss',
        'https://www.cnbc.com/id/100003114/device/rss/rss.html',   # CNBC Top News
        'https://www.cnbc.com/id/10000664/device/rss/rss.html',    # CNBC Markets
    ],
    'Macro & Central Banks': [
        'https://www.federalreserve.gov/feeds/press_all.xml',      # Fed all press releases
        'https://www.ecb.europa.eu/rss/press.html',                # ECB press releases
        'https://www.cnbc.com/id/20910258/device/rss/rss.html',    # CNBC Economy
    ],
    'Regulatory & Filings': [
        'https://www.sec.gov/news/pressreleases.rss',              # SEC press releases
        'https://efts.sec.gov/LATEST/search-index?q=%228-K%22&forms=8-K&dateRange=custom&startdt=2024-01-01',  # SEC 8-K filings
    ],
    'Geopolitics': [
        'https://feeds.bbci.co.uk/news/world/rss.xml',            # BBC World
        'https://rsshub.app/apnews/topics/ap-top-news',           # AP News via RSSHub
        'https://asiatimes.com/feed/',                              # Asia-Pacific geopolitics
    ],
    'EU & Europe': [
        'https://www.politico.eu/feed/',
        'https://www.consilium.europa.eu/en/press/press-releases/rss',  # EU Council
    ],
    'Commodities': [
        'https://oilprice.com/rss/main',
    ],
    'AI': [
        'https://openai.com/news/rss.xml',
    ],
    'Crypto': [
        'https://cointelegraph.com/rss',
        'https://www.coindesk.com/arc/outboundfeeds/rss/',
    ],
    'Albania': [
        'https://exit.al/en/feed/',
        'https://balkaninsight.com/feed/',
        'https://shqiptarja.com/feed/',
    ],
}

# Finnhub API settings (requires FINNHUB_API_KEY in .env)
FINNHUB_CATEGORIES = ['general', 'forex', 'merger']
FINNHUB_MAX_ARTICLES = 10
