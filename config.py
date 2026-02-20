"""NET_WATCH configuration — categories, feed URLs, constants."""

# User-Agent for HTTP requests
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 NetWatchBot/7.0'
}

# Gemini model for summarization
GEMINI_MODEL = 'gemini-2.5-flash'

# SQLite database file
DB_FILE = 'netwatch_state.db'

# Max articles to pull per feed
MAX_ARTICLES_PER_FEED = 10

# Articles per category in a /news batch
MIN_ARTICLES_PER_CATEGORY = 2
MAX_ARTICLES_PER_CATEGORY = 5

# RSS-only feed sources per category
CATEGORIES = {
    'Albanian Politics': [
        'https://exit.al/en/feed/',
    ],
    'Macroeconomics': [
        'https://feeds.reuters.com/reuters/businessNews',
    ],
    'Investing': [
        'https://feeds.bloomberg.com/markets/news.rss',
    ],
    'EU News': [
        'https://www.politico.eu/feed/',
    ],
    'Balkan News': [
        'https://balkaninsight.com/feed/',
    ],
    'Commodities': [
        'https://oilprice.com/rss/main',
    ],
    'Tech & Business': [
        'https://feeds.arstechnica.com/arstechnica/index',
        'https://lobste.rs/hottest.rss',
    ],
    'World News': [
        'https://feeds.bbci.co.uk/news/world/rss.xml',
    ],
    'Crypto': [
        'https://cointelegraph.com/rss',
        'https://www.coindesk.com/arc/outboundfeeds/rss/',
    ],
}
