"""NET_WATCH 7.0 — AI-powered news intelligence terminal."""

import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

from database import init_db
from summarizer import init_summarizer
from fetcher import init_finnhub
from handlers import start, news, button_handler, weights_command

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


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
    app.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Bot is polling...")
    # Python 3.14 removed implicit event loop creation.
    # Use async main + asyncio.run() instead of app.run_polling().
    async def run():
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

    asyncio.run(run())


if __name__ == '__main__':
    main()
