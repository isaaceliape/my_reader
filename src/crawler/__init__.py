"""
Web Crawler module for fetching and extracting article content from URLs.
"""

from .models import Article, CrawlResult
from .client import CrawlerClient
from .parser import parse_html
from .extractor import extract_article, detect_language
from .cache import url_cache, cached_fetch
from .robots import check_robots

__all__ = [
    "Article",
    "CrawlResult",
    "CrawlerClient",
    "parse_html",
    "extract_article",
    "detect_language",
    "url_cache",
    "cached_fetch",
    "check_robots",
]
