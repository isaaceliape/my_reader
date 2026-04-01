"""
Data models for the web crawler module.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Article:
    """Represents an extracted article from a web page."""

    url: str
    title: str
    text: str
    html: str | None = None
    language: str | None = None
    fetched_at: datetime = field(default_factory=datetime.now)


@dataclass
class CrawlResult:
    """Result of a crawl operation."""

    success: bool
    article: Article | None = None
    error: str | None = None
