"""NET_WATCH configuration — categories, feed URLs, constants."""

import os

# User-Agent for HTTP requests
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

# Gemini model for summarization and ranking
GEMINI_MODEL = 'gemini-2.5-flash'

# SQLite database file — use DATA_DIR env var for Docker volume mount
_data_dir = os.environ.get('DATA_DIR', '')
DB_FILE = os.path.join(_data_dir, 'netwatch_state.db') if _data_dir else 'netwatch_state.db'

# Max articles to pull per RSS feed
MAX_ARTICLES_PER_FEED = 10

# Total articles to deliver per /news batch (after AI ranking)
MAX_ARTICLES_PER_BATCH = 15

# Max text sent to Gemini for summarization (tokens are proportional)
MAX_SCRAPE_CHARS = 1500

# How many extra articles to rank (buffer for quality-gate filtering)
RANK_BUFFER_MULTIPLIER = 2

# Webhook server port for n8n trigger
WEBHOOK_PORT = int(os.environ.get('WEBHOOK_PORT', '8080'))

# Feed sources per category
CATEGORIES = {
    'Market News': [
        'https://www.cnbc.com/id/100003114/device/rss/rss.html',   # CNBC Top News
        'https://www.cnbc.com/id/10000664/device/rss/rss.html',    # CNBC Markets
        'https://feeds.content.dowjones.io/public/rss/mw_topstories',  # MarketWatch Top Stories
        'https://feeds.content.dowjones.io/public/rss/RSSMarketsMain',  # WSJ Markets
        'https://rss.nytimes.com/services/xml/rss/nyt/Business.xml',  # NYT Business
        'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10001147',  # CNBC Finance
    ],
    'Macro & Central Banks': [
        'https://www.federalreserve.gov/feeds/press_all.xml',      # Fed all press releases
        'https://www.ecb.europa.eu/rss/press.html',                # ECB press releases
        'https://www.cnbc.com/id/20910258/device/rss/rss.html',    # CNBC Economy
        'https://www.imf.org/en/News/Rss?language=eng',            # IMF News
        'https://www.bis.org/rss/cbspeeches.rss',                 # BIS central bank speeches
        'https://www.bis.org/rss/press.rss',                       # BIS press releases
    ],
    'Regulatory & Filings': [
        'https://www.sec.gov/news/pressreleases.rss',              # SEC press releases
        'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&type=8-K&dateb=&owner=include&count=10&search_text=&action=getcompany&output=atom',  # SEC 8-K filings (Atom)
        'https://www.cftc.gov/Newsroom/PressReleases/rss.xml',     # CFTC press releases
        'https://www.esma.europa.eu/press-news/esma-news/feed',    # ESMA (EU securities regulator)
    ],
    'Geopolitics': [
        'https://feeds.bbci.co.uk/news/world/rss.xml',            # BBC World
        'https://rsshub.app/apnews/topics/ap-top-news',           # AP News via RSSHub
        'https://feeds.skynews.com/feeds/rss/world.xml',          # Sky News World
        'https://asiatimes.com/feed/',                              # Asia-Pacific geopolitics
        'https://www.aljazeera.com/xml/rss/all.xml',              # Al Jazeera
        'https://feeds.content.dowjones.io/public/rss/RSSWorldNews',  # WSJ World News
        'https://feeds.npr.org/1004/rss.xml',                     # NPR World
    ],
    'EU & Europe': [
        'https://www.politico.eu/feed/',
        'https://www.consilium.europa.eu/en/press/press-releases/rss',  # EU Council
        'https://www.euractiv.com/feed/',                          # EurActiv
        'https://euobserver.com/rss.xml',                          # EUobserver
        'https://www.europarl.europa.eu/rss/doc/top-stories/en.xml',  # EU Parliament
    ],
    'Commodities': [
        'https://oilprice.com/rss/main',
        'https://www.kitco.com/news/category/mining/rss',           # Kitco (gold & precious metals)
        'https://www.mining.com/feed/',                             # Mining.com
    ],
    'AI': [
        'https://openai.com/news/rss.xml',
        'https://deepmind.google/blog/rss.xml',                    # Google DeepMind
        'https://blog.research.google/feeds/posts/default',        # Google AI Blog
        'https://techcrunch.com/category/artificial-intelligence/feed/',  # TechCrunch AI
        'https://www.technologyreview.com/feed/',                  # MIT Technology Review
        'https://www.wired.com/feed/rss',                          # Wired
    ],
    'Crypto': [
        'https://cointelegraph.com/rss',
        'https://www.coindesk.com/arc/outboundfeeds/rss/',
        'https://decrypt.co/feed',                                 # Decrypt
        'https://www.theblock.co/rss.xml',                         # The Block
        'https://blockworks.co/feed',                              # Blockworks
        'https://bitcoinmagazine.com/feed',                        # Bitcoin Magazine
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
