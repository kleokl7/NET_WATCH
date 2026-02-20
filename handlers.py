"""NET_WATCH Telegram handlers — commands and inline button callbacks."""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_category_weights, update_category_weight, mark_article_seen
from fetcher import get_articles_batch
from scraper import scrape_article_text
from summarizer import summarize_text


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "🟢 *NET\\_WATCH 7.0 ONLINE*\n\n"
        "Your personalized, AI\\-powered intelligence terminal is ready\\.\n\n"
        "Send /news to fetch your news briefing\\.\n"
        "Send /weights to view your category priorities\\."
    )
    await update.message.reply_text(welcome, parse_mode='MarkdownV2')


async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_message = await update.message.reply_text("📡 *Scanning global feeds\\.\\.\\.*", parse_mode='MarkdownV2')

    weights = get_category_weights()
    batch = get_articles_batch(weights)

    if not batch:
        await status_message.edit_text("✅ You are caught up. No new articles found.")
        return

    total = sum(len(arts) for arts in batch.values())
    await status_message.edit_text(f"🧠 Processing {total} articles across {len(batch)} categories...")

    # Send articles grouped by category
    for category, articles in batch.items():
        for article in articles:
            mark_article_seen(article['url'])

            body_text = scrape_article_text(article['url'])
            summary = summarize_text(body_text)

            # Format the date if available
            date_str = ""
            if article.get('date'):
                date_str = f"\n🗓 {_escape_md(article['date'].strftime('%b %d, %Y'))}"

            message_text = (
                f"📰 *\\[{_escape_md(category)}\\] \\| {_escape_md(article['source'])}*{date_str}\n"
                f"*{_escape_md(article['title'])}*\n\n"
                f"{_escape_md(summary)}"
            )

            keyboard = [
                [InlineKeyboardButton("📖 Read Full Article", url=article['url'])],
                [
                    InlineKeyboardButton("👍 Boost", callback_data=f"up_{category}"),
                    InlineKeyboardButton("👎 Bury", callback_data=f"down_{category}"),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                message_text, parse_mode='MarkdownV2', reply_markup=reply_markup
            )

    await status_message.delete()

    # Show current weights after the briefing
    weights = get_category_weights()
    lines = ["📊 *Current Category Priorities:*\n"]
    for cat, weight in sorted(weights.items(), key=lambda item: item[1], reverse=True):
        lines.append(f"• {_escape_md(cat)}: `{weight:.1f}`")
    await update.message.reply_text("\n".join(lines), parse_mode='MarkdownV2')


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles 👍 Boost / 👎 Bury inline button clicks."""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("up_"):
        category = data[3:]
        update_category_weight(category, 0.5)
        await query.edit_message_reply_markup(reply_markup=None)
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"📈 *Priority Increased:* {_escape_md(category)}",
            parse_mode='MarkdownV2',
        )

    elif data.startswith("down_"):
        category = data[5:]
        update_category_weight(category, -0.5)
        await query.edit_message_reply_markup(reply_markup=None)
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"📉 *Priority Decreased:* {_escape_md(category)}",
            parse_mode='MarkdownV2',
        )


async def weights_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows current category weight priorities."""
    weights = get_category_weights()
    lines = ["📊 *Current Category Priorities:*\n"]
    for cat, weight in sorted(weights.items(), key=lambda item: item[1], reverse=True):
        lines.append(f"• {_escape_md(cat)}: `{weight:.1f}`")

    await update.message.reply_text("\n".join(lines), parse_mode='MarkdownV2')


def _escape_md(text):
    """Escapes special characters for Telegram MarkdownV2."""
    special = r'_*[]()~`>#+-=|{}.!'
    escaped = ""
    for ch in str(text):
        if ch in special:
            escaped += '\\' + ch
        else:
            escaped += ch
    return escaped
