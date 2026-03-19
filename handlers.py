"""NET_WATCH Telegram handlers — commands and inline button callbacks."""

import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_category_weights, update_category_weight, mark_articles_seen, cleanup_old_articles
from fetcher import get_all_articles
from scraper import scrape_article_text
from summarizer import rank_articles, summarize_text
from config import MAX_ARTICLES_PER_BATCH, GUARANTEED_CATEGORIES

# Pre-compiled regex for MarkdownV2 escaping
_MD_ESCAPE = re.compile(r'([_*\[\]()~`>#\+\-=|{}.!])')


def _escape_md(text):
    return _MD_ESCAPE.sub(r'\\\1', str(text))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🟢 *NET\\_WATCH 8\\.0 ONLINE*\n\n"
        "AI\\-ranked news intelligence terminal\\.\n\n"
        "/news \\— fetch ranked briefing\n"
        "/weights \\— view category priorities",
        parse_mode='MarkdownV2',
    )


async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = await update.message.reply_text("📡 *Scanning feeds\\.\\.\\.*", parse_mode='MarkdownV2')

    # 1. Fetch all articles concurrently
    articles = get_all_articles()
    if not articles:
        await status.edit_text("No new articles found.")
        return

    await status.edit_text(f"🧠 Ranking {len(articles)} articles...")

    # 2. AI rank all headlines in one Gemini call
    weights = get_category_weights()
    ranked = rank_articles(articles, weights)

    # 3. Reserve guaranteed category slots, then fill remaining with ranked articles
    top = []
    used_urls = set()
    for cat, max_count in GUARANTEED_CATEGORIES.items():
        cat_articles = [a for a in ranked if a['category'] == cat][:max_count]
        for a in cat_articles:
            top.append(a)
            used_urls.add(a['url'])

    remaining_slots = MAX_ARTICLES_PER_BATCH - len(top)
    for a in ranked:
        if a['url'] not in used_urls:
            top.append(a)
            if len(top) >= MAX_ARTICLES_PER_BATCH:
                break
    await status.edit_text(f"📝 Summarizing top {len(top)} articles...")

    # 4. Mark all as seen in one batch
    mark_articles_seen([a['url'] for a in top])

    # 5. Scrape + summarize only the top articles
    for article in top:
        # Prefer RSS summary; scrape only if too short
        text = article.get('rss_summary', '')
        if len(text) < 80:
            text = scrape_article_text(article['url'])
        summary = summarize_text(text)

        score_str = ""
        if 'ai_score' in article:
            score_str = f" \\[{article['ai_score']}/10\\]"

        date_str = ""
        if article.get('date'):
            date_str = f"\n🗓 {_escape_md(article['date'].strftime('%b %d, %H:%M UTC'))}"

        msg = (
            f"📰 *\\[{_escape_md(article['category'])}\\]*{score_str}"
            f" \\| {_escape_md(article['source'])}{date_str}\n"
            f"*{_escape_md(article['title'])}*\n\n"
            f"{_escape_md(summary)}"
        )

        keyboard = [
            [InlineKeyboardButton("📖 Read Full", url=article['url'])],
            [
                InlineKeyboardButton("👍 Boost", callback_data=f"up_{article['category']}"),
                InlineKeyboardButton("👎 Bury", callback_data=f"down_{article['category']}"),
            ],
        ]

        await update.message.reply_text(
            msg, parse_mode='MarkdownV2', reply_markup=InlineKeyboardMarkup(keyboard),
        )

    await status.delete()

    # Show weights summary
    weights = get_category_weights()
    lines = ["📊 *Category Priorities:*\n"]
    cats_shown = {a['category'] for a in top}
    for cat, w in sorted(weights.items(), key=lambda x: x[1], reverse=True):
        marker = " 🇦🇱" if cat in GUARANTEED_CATEGORIES else ""
        if cat in cats_shown:
            lines.append(f"• {_escape_md(cat)}: `{w:.1f}`{marker}")
    await update.message.reply_text("\n".join(lines), parse_mode='MarkdownV2')

    # Periodic DB cleanup
    cleanup_old_articles()


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("up_"):
        category = data[3:]
        update_category_weight(category, 0.5)
        await query.edit_message_reply_markup(reply_markup=None)
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"📈 *Boosted:* {_escape_md(category)}",
            parse_mode='MarkdownV2',
        )
    elif data.startswith("down_"):
        category = data[5:]
        update_category_weight(category, -0.5)
        await query.edit_message_reply_markup(reply_markup=None)
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"📉 *Buried:* {_escape_md(category)}",
            parse_mode='MarkdownV2',
        )


async def weights_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    weights = get_category_weights()
    lines = ["📊 *Category Priorities:*\n"]
    for cat, w in sorted(weights.items(), key=lambda x: x[1], reverse=True):
        lines.append(f"• {_escape_md(cat)}: `{w:.1f}`")
    await update.message.reply_text("\n".join(lines), parse_mode='MarkdownV2')
