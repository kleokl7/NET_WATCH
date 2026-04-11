"""NET_WATCH 9.0 — AI-powered news intelligence terminal with n8n webhook support."""

import os
import asyncio
import logging
from dotenv import load_dotenv
from aiohttp import web
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

from database import init_db
from summarizer import init_summarizer
from fetcher import init_finnhub
from handlers import start, news, button_handler, weights_command, health
from config import WEBHOOK_PORT

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def _trigger_news(request):
    """HTTP endpoint for n8n to trigger a news briefing.

    POST /trigger-news  { "chat_id": 123456789 }
    """
    bot = request.app['telegram_bot']
    try:
        data = await request.json()
        chat_id = data.get('chat_id')
        if not chat_id:
            return web.json_response({'error': 'chat_id required'}, status=400)

        # Import here to avoid circular dependency
        from fetcher import get_all_articles, get_feed_health
        from summarizer import rank_articles, summarize_text
        from scraper import scrape_article_text
        from database import get_category_weights, mark_articles_seen, cleanup_old_articles
        from config import MAX_ARTICLES_PER_BATCH, GUARANTEED_CATEGORIES, RANK_BUFFER_MULTIPLIER

        await bot.send_message(chat_id=chat_id, text="📡 Scheduled scan starting...")

        articles = get_all_articles()
        if not articles:
            await bot.send_message(chat_id=chat_id, text="No new articles found.")
            return web.json_response({'status': 'ok', 'delivered': 0})

        weights = get_category_weights()
        ranked = rank_articles(articles, weights)

        # Reserve guaranteed slots + over-fetch buffer
        candidates = []
        used_urls = set()
        for cat, max_count in GUARANTEED_CATEGORIES.items():
            cat_articles = [a for a in ranked if a['category'] == cat][:max_count]
            for a in cat_articles:
                candidates.append(a)
                used_urls.add(a['url'])

        max_candidates = MAX_ARTICLES_PER_BATCH * RANK_BUFFER_MULTIPLIER
        for a in ranked:
            if a['url'] not in used_urls:
                candidates.append(a)
                if len(candidates) >= max_candidates:
                    break

        dead_summaries = {'Content too short or paywalled.', 'Summary unavailable.', ''}
        delivered_urls = []

        for article in candidates:
            if len(delivered_urls) >= MAX_ARTICLES_PER_BATCH:
                break

            text = article.get('rss_summary', '')
            if len(text) < 80:
                scraped = scrape_article_text(article['url'])
                if scraped:
                    text = scraped

            summary = summarize_text(text)
            if summary in dead_summaries:
                continue

            score_str = f" [{article['ai_score']}/10]" if 'ai_score' in article else ""
            date_str = ""
            if article.get('date'):
                date_str = f"\n🗓 {article['date'].strftime('%b %d, %H:%M UTC')}"

            msg = (
                f"📰 [{article['category']}]{score_str}"
                f" | {article['source']}{date_str}\n"
                f"<b>{article['title']}</b>\n\n"
                f"{summary}\n\n"
                f"<a href=\"{article['url']}\">📖 Read Full</a>"
            )

            await bot.send_message(chat_id=chat_id, text=msg, parse_mode='HTML')
            delivered_urls.append(article['url'])

        if delivered_urls:
            mark_articles_seen(delivered_urls)

        cleanup_old_articles()

        await bot.send_message(
            chat_id=chat_id,
            text=f"✅ Scheduled briefing complete — {len(delivered_urls)} articles delivered."
        )
        return web.json_response({'status': 'ok', 'delivered': len(delivered_urls)})

    except Exception as e:
        logger.error(f"Webhook trigger error: {e}")
        return web.json_response({'error': str(e)}, status=500)


async def _health_check(request):
    """Simple health check endpoint."""
    return web.json_response({'status': 'ok'})


def main():
    load_dotenv()

    telegram_token = os.environ.get("TELEGRAM_TOKEN")
    gemini_api_key = os.environ.get("GEMINI_API_KEY")

    if not telegram_token or not gemini_api_key:
        logger.error("Missing TELEGRAM_TOKEN or GEMINI_API_KEY in .env")
        return

    logger.info("Initializing database...")
    init_db()

    logger.info("Initializing Gemini summarizer...")
    init_summarizer(gemini_api_key)

    finnhub_api_key = os.environ.get("FINNHUB_API_KEY")
    if finnhub_api_key:
        init_finnhub(finnhub_api_key)
        logger.info("Finnhub API enabled.")
    else:
        logger.info("No FINNHUB_API_KEY found — Finnhub disabled (RSS-only mode).")

    logger.info("Starting Telegram bot...")
    app = ApplicationBuilder().token(telegram_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("news", news))
    app.add_handler(CommandHandler("weights", weights_command))
    app.add_handler(CommandHandler("health", health))
    app.add_handler(CallbackQueryHandler(button_handler))

    # Create a standalone Bot instance for the webhook endpoint
    bot = Bot(token=telegram_token)

    logger.info("Bot is polling...")

    async def run():
        # Start webhook HTTP server for n8n triggers
        web_app = web.Application()
        web_app['telegram_bot'] = bot
        web_app.router.add_post('/trigger-news', _trigger_news)
        web_app.router.add_get('/health', _health_check)
        runner = web.AppRunner(web_app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', WEBHOOK_PORT)
        await site.start()
        logger.info(f"Webhook server listening on port {WEBHOOK_PORT}")

        # Start Telegram polling
        async with app:
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
            logger.info("Bot is running. Press Ctrl+C to stop.")
            try:
                await asyncio.Event().wait()  # Run forever
            except asyncio.CancelledError:
                pass
            finally:
                await app.updater.stop()
                await app.stop()
                await app.shutdown()
                await runner.cleanup()

    asyncio.run(run())


if __name__ == '__main__':
    main()
