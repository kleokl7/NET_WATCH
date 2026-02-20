"""NET_WATCH AI summarizer — Gemini-powered article summaries."""

import logging
import google.generativeai as genai
from config import GEMINI_MODEL

logger = logging.getLogger(__name__)

# Model instance (initialized after configure() is called in bot.py)
_model = None


def init_summarizer(api_key):
    """Configure Gemini and create the model instance."""
    global _model
    genai.configure(api_key=api_key)
    _model = genai.GenerativeModel(GEMINI_MODEL)


def summarize_text(text):
    """Returns a 2-bullet summary of the article text, or a fallback message."""
    if len(text.strip()) < 100:
        return "⚠️ Content too short or paywalled to summarize."

    prompt = (
        "Summarize the following news article in exactly 2 concise bullet points "
        "highlighting the most important facts. Keep it objective. "
        "Always respond in English.\n\n" + text
    )

    try:
        response = _model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Gemini summarization error: {e}")
        return "⚠️ Summary currently unavailable due to an API error."
