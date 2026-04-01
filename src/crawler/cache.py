"""
Caching module with TTL (Time-To-Live) support for URL fetching.
"""

from cachetools import TTLCache, cached
from datetime import datetime
from typing import Any


# Cache: 1000 URLs max, expires in 1 hour (3600 seconds)
# For 24h TTL, use ttl=86400
url_cache: TTLCache = TTLCache(maxsize=1000, ttl=3600)


def get_cache_key(url: str) -> str:
    """Generate a cache key for a URL.

    Args:
        url: The URL to cache

    Returns:
        Cache key string
    """
    return f"url:{url}"


@cached(url_cache)
def cached_fetch(url: str) -> tuple[str | None, datetime]:
    """Fetch a URL with caching support.

    This function is decorated with @cached, so results are automatically
    stored in url_cache and retrieved on subsequent calls within TTL.

    Args:
        url: The URL to fetch

    Returns:
        Tuple of (html_content, fetched_at_timestamp)
        html_content is None if fetch fails
    """
    # This is a stub - actual fetching is done by CrawlerClient
    # The decorator handles caching automatically
    return (None, datetime.now())


def cache_set(url: str, html: str) -> None:
    """Manually set a value in the cache.

    Args:
        url: The URL as cache key
        html: The HTML content to cache
    """
    url_cache[get_cache_key(url)] = (html, datetime.now())


def cache_get(url: str) -> tuple[str | None, datetime] | None:
    """Get a value from the cache.

    Args:
        url: The URL to look up

    Returns:
        Tuple of (html_content, fetched_at) or None if not found/expired
    """
    return url_cache.get(get_cache_key(url))


def cache_invalidate(url: str) -> bool:
    """Invalidate a specific URL from the cache.

    Args:
        url: The URL to invalidate

    Returns:
        True if item was removed, False if not found
    """
    key = get_cache_key(url)
    if key in url_cache:
        del url_cache[key]
        return True
    return False


def cache_clear() -> None:
    """Clear all items from the cache."""
    url_cache.clear()


def cache_stats() -> dict[str, Any]:
    """Get cache statistics.

    Returns:
        Dictionary with cache stats
    """
    return {
        "maxsize": url_cache.maxsize,
        "ttl": url_cache.ttl,
        "currsize": len(url_cache),
    }
