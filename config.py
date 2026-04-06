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
        'https://feeds.marketwatch.com/marketwatch/topstories/',    # MarketWatch Top Stories
        'https://rss.nytimes.com/services/xml/rss/nyt/Business.xml',  # NYT Business
        'https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC&region=US&lang=en-US',  # Yahoo Finance S&P
    ],
    'Macro & Central Banks': [
        'https://www.federalreserve.gov/feeds/press_all.xml',      # Fed all press releases
        'https://www.ecb.europa.eu/rss/press.html',                # ECB press releases
        'https://www.cnbc.com/id/20910258/device/rss/rss.html',    # CNBC Economy
        'https://www.imf.org/en/News/Rss?language=eng',            # IMF News
        'https://www.boj.or.jp/en/rss/whatsnew.xml',               # Bank of Japan
        'https://www.bankofengland.co.uk/rss/news',                # Bank of England
    ],
    'Regulatory & Filings': [
        'https://www.sec.gov/news/pressreleases.rss',              # SEC press releases
        'https://efts.sec.gov/LATEST/search-index?q=%228-K%22&forms=8-K&dateRange=custom&startdt=2024-01-01',  # SEC 8-K filings
        'https://www.cftc.gov/Newsroom/PressReleases/rss.xml',     # CFTC press releases
        'https://www.esma.europa.eu/press-news/esma-news?f%5B0%5D=news_category%3A72/feed',  # ESMA (EU securities regulator)
    ],
    'Geopolitics': [
        'https://feeds.bbci.co.uk/news/world/rss.xml',            # BBC World
        'https://rsshub.app/apnews/topics/ap-top-news',           # AP News via RSSHub
        'https://asiatimes.com/feed/',                              # Asia-Pacific geopolitics
        'https://www.aljazeera.com/xml/rss/all.xml',              # Al Jazeera
        'https://rss.dw.com/rdf/rss-en-all',                      # Deutsche Welle
        'https://www.reutersagency.com/feed/',                     # Reuters Agency
    ],
    'EU & Europe': [
        'https://www.politico.eu/feed/',
        'https://www.consilium.europa.eu/en/press/press-releases/rss',  # EU Council
        'https://www.euractiv.com/feed/',                          # EurActiv
        'https://www.euronews.com/rss',                            # Euronews
        'https://ec.europa.eu/eurostat/web/rss/notifications.rss', # Eurostat data releases
    ],
    'Commodities': [
        'https://oilprice.com/rss/main',
        'https://www.kitco.com/feed/rss/news/',                    # Kitco (gold & precious metals)
        'https://www.mining.com/feed/',                             # Mining.com
    ],
    'AI': [
        'https://openai.com/news/rss.xml',
        'https://www.anthropic.com/feed.xml',                      # Anthropic
        'https://deepmind.google/blog/rss.xml',                    # Google DeepMind
        'https://techcrunch.com/category/artificial-intelligence/feed/',  # TechCrunch AI
        'https://www.technologyreview.com/feed/',                  # MIT Technology Review
        'https://feeds.arstechnica.com/arstechnica/index',         # Ars Technica
    ],
    'Crypto': [
        'https://cointelegraph.com/rss',
        'https://www.coindesk.com/arc/outboundfeeds/rss/',
        'https://decrypt.co/feed',                                 # Decrypt
        'https://cryptoslate.com/feed/',                            # CryptoSlate
        'https://www.theblock.co/rss.xml',                         # The Block
    ],
    'Albania': [
        'https://exit.al/en/feed/',
        'https://balkaninsight.com/feed/',
        'https://shqiptarja.com/feed/',
    ],
}

# Categories that always get slots regardless of market-impact score.
# These are ranked by relevance within their own category, not market impact.
GUARANTEED_CATEGORIES = {
    'Albania': 3,  # Always deliver up to 3 Albanian articles
}

# Finnhub API settings (requires FINNHUB_API_KEY in .env)
FINNHUB_CATEGORIES = ['general', 'forex', 'merger']
FINNHUB_MAX_ARTICLES = 10
