# NET_WATCH

AI-powered news intelligence bot for Telegram. Aggregates articles from 30+ RSS feeds, ranks them by market impact using Google Gemini, and delivers concise briefings — so you only read what matters.

## Features

- **AI-ranked news** — Gemini 2.5 Flash scores every headline 1–10 by market impact, then selects the top 15
- **9 categories** — Market News, Macro & Central Banks, Regulatory, Geopolitics, EU & Europe, Commodities, AI, Crypto, Albania
- **Personalized weights** — Boost or bury categories with inline buttons; preferences persist across sessions
- **Guaranteed slots** — Albania articles always appear (relevance-ranked within category)
- **Smart summaries** — 2-bullet AI summaries generated from RSS descriptions or scraped article text
- **Deduplication** — SQLite tracks seen articles so you never get repeats
- **Finnhub integration** — Optional market news from Finnhub API (general, forex, M&A)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Bot framework | python-telegram-bot 21.6 |
| AI / LLM | Google Gemini 2.5 Flash |
| Feed parsing | feedparser, BeautifulSoup4, lxml |
| Market data | Finnhub API (optional) |
| State | SQLite (WAL mode) |
| Deployment | Render / any Procfile-based PaaS |

## Project Structure

```
bot.py           # Entry point — Telegram bot setup & polling
config.py        # RSS sources, categories, constants
database.py      # SQLite state (seen articles, category weights)
fetcher.py       # Concurrent RSS & Finnhub fetching
scraper.py       # HTML scraping with BeautifulSoup
summarizer.py    # Gemini ranking & summarization
handlers.py      # Telegram command & callback handlers
```

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file:

```
TELEGRAM_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key
FINNHUB_API_KEY=your_finnhub_key  # optional
```

### 3. Run

```bash
python bot.py
```

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Introduction and command list |
| `/news` | Fetch and send a ranked 15-article briefing |
| `/weights` | Show current category priority scores |

Each article includes **Read Full**, **Boost**, and **Bury** inline buttons.

## How It Works

1. **Fetch** — Pulls articles from 30+ RSS feeds concurrently (8 threads), plus optional Finnhub data
2. **Filter** — Removes duplicates, non-English/Albanian articles, and anything older than 3 days
3. **Rank** — Sends all headlines to Gemini in a single API call; each gets a 1–10 impact score
4. **Weight** — Multiplies AI score by user's category weight (`rank_score = ai_score × weight`)
5. **Select** — Picks the top 15, reserving guaranteed slots for Albania
6. **Summarize** — Generates 2-bullet summaries via Gemini
7. **Deliver** — Sends formatted messages to Telegram with inline action buttons

## Deployment

Configured for Render via `render.yaml` (worker service). Also works with any platform that supports a `Procfile`:

```
worker: python bot.py
```
