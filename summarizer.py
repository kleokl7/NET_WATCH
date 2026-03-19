"""NET_WATCH AI — Gemini-powered article ranking and summarization."""

import json
import logging
import google.generativeai as genai
from config import GEMINI_MODEL

logger = logging.getLogger(__name__)

_model = None


def init_summarizer(api_key):
    global _model
    genai.configure(api_key=api_key)
    _model = genai.GenerativeModel(GEMINI_MODEL)


def rank_articles(articles, weights):
    """Rank articles by market impact using Gemini. Returns articles sorted best-first.

    Sends all headlines in one API call. Gemini returns a score 1-10 for each.
    Final sort key = ai_score * category_weight.
    """
    if not articles or not _model:
        return articles

    # Build numbered headline list for the prompt
    lines = []
    for i, a in enumerate(articles):
        lines.append(f"{i}. [{a['category']}] {a['title']}")
    headline_block = "\n".join(lines)

    prompt = (
        "You are a financial news editor. Rate each headline below for market impact "
        "on a scale of 1-10 where:\n"
        "10 = major market mover (central bank rate decision, war, trade policy shift, "
        "major earnings miss/beat, regulatory action on large cap)\n"
        "7-9 = significant (sector-moving, geopolitical escalation, macro data surprise)\n"
        "4-6 = moderate (industry news, mid-cap earnings, policy proposals)\n"
        "1-3 = low impact (opinion pieces, minor updates, human interest)\n\n"
        "Respond ONLY with a JSON array of integers in the same order. "
        "Example for 3 headlines: [7, 3, 9]\n\n"
        f"{headline_block}"
    )

    try:
        response = _model.generate_content(prompt)
        text = response.text.strip()
        # Extract JSON array from response (handle markdown code blocks)
        if '```' in text:
            text = text.split('```')[1]
            if text.startswith('json'):
                text = text[4:]
        scores = json.loads(text.strip())

        if len(scores) != len(articles):
            logger.warning(f"Score count mismatch: got {len(scores)}, expected {len(articles)}")
            return articles

        # Apply scores and sort by score * category_weight
        for i, article in enumerate(articles):
            ai_score = max(1, min(10, scores[i]))
            cat_weight = weights.get(article['category'], 1.0)
            article['ai_score'] = ai_score
            article['rank_score'] = ai_score * cat_weight

        articles.sort(key=lambda a: a['rank_score'], reverse=True)
        return articles

    except Exception as e:
        logger.error(f"Ranking error: {e}")
        return articles


def summarize_text(text):
    """Returns a 2-bullet summary. Input should be pre-trimmed."""
    if not text or len(text.strip()) < 80:
        return "Content too short or paywalled."

    prompt = (
        "Summarize in exactly 2 concise bullet points. "
        "Focus on facts and market implications. English only.\n\n" + text
    )

    try:
        response = _model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Summary error: {e}")
        return "Summary unavailable."
