"""
Article extraction module using readability-lxml and language detection.
"""

from readability import Document
from bs4 import BeautifulSoup
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Set seed for consistent language detection results
DetectorFactory.seed = 0


def extract_article(html: str) -> dict:
    """Extract article content from HTML using readability-lxml.

    Args:
        html: The HTML string to parse

    Returns:
        Dictionary with 'title', 'html', and 'text' keys
    """
    doc = Document(html)
    summary = doc.summary()

    # Extract plain text from the summary HTML
    soup = BeautifulSoup(summary, "lxml")
    text = soup.get_text(separator=" ", strip=True)

    return {"title": doc.title(), "html": summary, "text": text}


def detect_language(text: str) -> str | None:
    """Detect the language of a text string.

    Args:
        text: The text to analyze

    Returns:
        ISO 639-1 language code (e.g., 'en', 'pt', 'es') or None if detection fails
    """
    if not text or len(text.strip()) < 10:
        return None

    try:
        return detect(text)
    except LangDetectException:
        return None
    except Exception:
        return None
