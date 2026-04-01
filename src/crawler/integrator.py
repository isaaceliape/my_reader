"""
Integration module for connecting web crawler to TTS pipeline.
"""

from datetime import datetime
from urllib.parse import urlparse

from .client import CrawlerClient
from .parser import parse_html, extract_title
from .extractor import extract_article, detect_language
from .models import Article, CrawlResult
from .cache import cache_get, cache_set, cache_invalidate


def validate_url(url: str) -> tuple[bool, str | None]:
    """Validate a URL for crawling.

    Args:
        url: The URL to validate

    Returns:
        Tuple of (is_valid, error_message)
        error_message is None if valid
    """
    try:
        parsed = urlparse(url)
    except Exception as e:
        return (False, f"Invalid URL format: {str(e)}")

    # Check scheme
    if parsed.scheme not in ("http", "https"):
        return (False, f"URL must use http or https scheme, got: {parsed.scheme}")

    # Check netloc (domain)
    if not parsed.netloc:
        return (False, "URL must have a valid domain")

    return (True, None)


def process_url_to_audio(
    url: str, voice: str = "af_heart", speed: float = 1.0
) -> tuple[Article | None, str | None, bool]:
    """Process a URL to extract article content for TTS.

    This function fetches the URL, extracts the article content,
    and returns an Article object ready for audio generation.

    Args:
        url: The URL to process
        voice: Voice ID for TTS (default: "af_heart")
        speed: Playback speed (default: 1.0)

    Returns:
        Tuple of (article, error, cache_hit)
        - article: Article object if successful, None otherwise
        - error: Error message if failed, None otherwise
        - cache_hit: True if content was served from cache
    """
    # Validate URL first
    is_valid, error = validate_url(url)
    if not is_valid:
        return (None, error, False)

    # Check cache first
    cached = cache_get(url)
    if cached is not None:
        html, fetched_at = cached
        if html:
            # Parse and extract from cached content
            soup = parse_html(html)
            title = extract_title(soup) or "Unknown"
            extracted = extract_article(html)
            language = detect_language(extracted["text"])

            article = Article(
                url=url,
                title=title,
                text=extracted["text"],
                html=extracted["html"],
                language=language,
                fetched_at=fetched_at,
            )
            return (article, None, True)

    # Fetch URL
    client = CrawlerClient()
    try:
        result = client.fetch(url)

        if not result.success:
            error_msg = result.error or "Unknown error"

            # Detect paywall (403)
            if "403" in error_msg or "forbidden" in error_msg.lower():
                return (
                    None,
                    "Site requires authentication or is blocking automated access",
                    False,
                )

            # Detect timeout
            if "timeout" in error_msg.lower():
                return (None, "Request timed out", False)

            return (None, error_msg, False)

        # result.article should have the html from the fetch
        if result.article is None:
            return (None, "No content received", False)

        html = result.article.html
        if not html:
            return (None, "Empty content received", False)

        # Cache the HTML
        cache_set(url, html)
        fetched_at = datetime.now()

        # Parse HTML
        soup = parse_html(html)

        # Extract title
        title = extract_title(soup) or "Unknown"

        # Extract article content using readability
        extracted = extract_article(html)

        # Detect language
        language = detect_language(extracted["text"])

        # Create Article object
        article = Article(
            url=url,
            title=title,
            text=extracted["text"],
            html=extracted["html"],
            language=language,
            fetched_at=fetched_at,
        )

        return (article, None, False)

    finally:
        client.close()
