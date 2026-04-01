"""
Unit tests for the web crawler module.
"""

import pytest
from bs4 import BeautifulSoup

from src.crawler.models import Article, CrawlResult
from src.crawler.parser import parse_html, extract_title, extract_text
from src.crawler.extractor import extract_article, detect_language
from src.crawler.cache import (
    url_cache,
    get_cache_key,
    cache_set,
    cache_get,
    cache_invalidate,
    cache_clear,
    cache_stats,
)


# HTML de exemplo para testes
SAMPLE_HTML = """
<html>
    <head><title>Test Article</title></head>
    <body>
        <article>
            <h1>Test Article</h1>
            <p>This is test content.</p>
            <p>It has multiple paragraphs.</p>
        </article>
    </body>
</html>
"""

SAMPLE_HTML_NO_TITLE = """
<html>
    <head></head>
    <body>
        <p>Content without title</p>
    </body>
</html>
"""

SIMPLE_HTML = """
<html>
    <head><title>Simple Page</title></head>
    <body>
        <p>Hello world</p>
    </body>
</html>
"""


class TestParseHTML:
    """Tests for parser.py functions."""

    def test_parse_html_extracts_title(self):
        """Test that parse_html correctly parses HTML and title can be extracted."""
        soup = parse_html(SAMPLE_HTML)
        assert soup.title is not None
        assert soup.title.string == "Test Article"

    def test_parse_html_returns_beautifulsoup(self):
        """Test that parse_html returns a BeautifulSoup object."""
        soup = parse_html(SAMPLE_HTML)
        assert isinstance(soup, BeautifulSoup)

    def test_extract_title_from_valid_html(self):
        """Test extract_title with valid HTML containing title."""
        soup = parse_html(SAMPLE_HTML)
        title = extract_title(soup)
        assert title == "Test Article"

    def test_extract_title_from_html_without_title(self):
        """Test extract_title with HTML that has no title."""
        soup = parse_html(SAMPLE_HTML_NO_TITLE)
        title = extract_title(soup)
        assert title is None

    def test_extract_text_from_html(self):
        """Test extract_text extracts all text content."""
        soup = parse_html(SAMPLE_HTML)
        text = extract_text(soup)
        assert "Test Article" in text
        assert "test content" in text.lower()
        assert "multiple paragraphs" in text.lower()


class TestExtractArticle:
    """Tests for extractor.py functions."""

    def test_extract_article_returns_content(self):
        """Test that extract_article returns title and text content."""
        result = extract_article(SAMPLE_HTML)
        assert "Test Article" in result["title"]
        assert "test content" in result["text"].lower()

    def test_extract_article_returns_dict_with_keys(self):
        """Test that extract_article returns dict with required keys."""
        result = extract_article(SAMPLE_HTML)
        assert "title" in result
        assert "html" in result
        assert "text" in result

    def test_extract_article_handles_simple_html(self):
        """Test extract_article with simple HTML structure."""
        result = extract_article(SIMPLE_HTML)
        assert "Simple Page" in result["title"]


class TestDetectLanguage:
    """Tests for language detection."""

    def test_detect_language_english(self):
        """Test language detection for English text."""
        text = "This is a sample English text. It contains multiple sentences."
        lang = detect_language(text)
        assert lang == "en"

    def test_detect_language_portuguese(self):
        """Test language detection for Portuguese text."""
        text = "Este é um texto de exemplo em português. Contém múltiplas frases."
        lang = detect_language(text)
        assert lang == "pt"

    def test_detect_language_spanish(self):
        """Test language detection for Spanish text."""
        text = "Este es un texto de ejemplo en español. Contiene múltiples frases."
        lang = detect_language(text)
        assert lang == "es"

    def test_detect_language_short_text(self):
        """Test that short text returns None."""
        text = "Hi"
        lang = detect_language(text)
        assert lang is None

    def test_detect_language_empty_text(self):
        """Test that empty text returns None."""
        lang = detect_language("")
        assert lang is None

    def test_detect_language_none_text(self):
        """Test that None text returns None."""
        lang = detect_language(None)
        assert lang is None


class TestCache:
    """Tests for cache.py functions."""

    def setup_method(self):
        """Clear cache before each test."""
        cache_clear()

    def teardown_method(self):
        """Clear cache after each test."""
        cache_clear()

    def test_cache_key_generation(self):
        """Test that cache keys are generated correctly."""
        url = "https://example.com/article"
        key = get_cache_key(url)
        assert key == "url:https://example.com/article"

    def test_cache_set_and_get(self):
        """Test setting and getting values from cache."""
        url = "https://example.com/test"
        html = "<html><body>Test</body></html>"

        cache_set(url, html)
        result = cache_get(url)

        assert result is not None
        assert result[0] == html

    def test_cache_miss(self):
        """Test cache miss returns None."""
        result = cache_get("https://nonexistent.com")
        assert result is None

    def test_cache_invalidate(self):
        """Test cache invalidation."""
        url = "https://example.com/invalidate"
        html = "<html><body>Invalidate test</body></html>"

        cache_set(url, html)
        assert cache_get(url) is not None

        removed = cache_invalidate(url)
        assert removed is True
        assert cache_get(url) is None

    def test_cache_invalidate_nonexistent(self):
        """Test invalidating non-existent key returns False."""
        removed = cache_invalidate("https://nonexistent.com")
        assert removed is False

    def test_cache_clear(self):
        """Test clearing all cache."""
        cache_set("https://example.com/1", "<html>1</html>")
        cache_set("https://example.com/2", "<html>2</html>")

        stats_before = cache_stats()
        assert stats_before["currsize"] == 2

        cache_clear()

        stats_after = cache_stats()
        assert stats_after["currsize"] == 0

    def test_cache_stats(self):
        """Test cache statistics."""
        cache_clear()
        stats = cache_stats()

        assert "maxsize" in stats
        assert "ttl" in stats
        assert "currsize" in stats
        assert stats["currsize"] == 0

    def test_cache_hit_miss_tracking(self):
        """Test that cache tracks hits and misses through size changes."""
        cache_clear()

        # Miss (doesn't add to cache)
        cache_get("https://miss.com")
        stats = cache_stats()
        assert stats["currsize"] == 0

        # Set and hit
        cache_set("https://hit.com", "<html>hit</html>")
        result = cache_get("https://hit.com")

        stats = cache_stats()
        assert stats["currsize"] == 1
        assert result is not None


class TestModels:
    """Tests for models.py dataclasses."""

    def test_article_creation(self):
        """Test Article dataclass creation."""
        article = Article(
            url="https://example.com",
            title="Test Article",
            text="Test content",
            language="en",
        )
        assert article.url == "https://example.com"
        assert article.title == "Test Article"
        assert article.text == "Test content"
        assert article.language == "en"

    def test_crawl_result_creation(self):
        """Test CrawlResult dataclass creation."""
        result = CrawlResult(
            success=True,
            article=None,
            error=None,
        )
        assert result.success is True
        assert result.article is None
        assert result.error is None
