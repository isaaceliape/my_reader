"""
robots.txt checker for ethical web crawling.
"""

from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import httpx


# Cache for robots.txt parsers per domain
_robots_cache: dict[str, RobotFileParser] = {}


def _get_domain(url: str) -> str:
    """Extract domain from URL.

    Args:
        url: The URL to extract domain from

    Returns:
        Domain string (e.g., 'example.com')
    """
    parsed = urlparse(url)
    return parsed.netloc


def _get_robots_url(domain: str) -> str:
    """Build robots.txt URL for a domain.

    Args:
        domain: The domain

    Returns:
        Full URL to robots.txt
    """
    return f"https://{domain}/robots.txt"


def _load_robots_txt(domain: str) -> RobotFileParser:
    """Load and parse robots.txt for a domain.

    Args:
        domain: The domain to fetch robots.txt for

    Returns:
        RobotFileParser instance
    """
    if domain in _robots_cache:
        return _robots_cache[domain]

    rp = RobotFileParser()
    robots_url = _get_robots_url(domain)

    try:
        response = httpx.get(robots_url, timeout=10.0)
        if response.status_code == 200:
            rp.parse(response.text.splitlines())
        # If 404 or error, rp remains empty (allows all)
    except Exception:
        # If we can't fetch robots.txt, assume it allows all
        pass

    _robots_cache[domain] = rp
    return rp


def check_robots(url: str, user_agent: str = "*") -> tuple[bool, str | None]:
    """Check if a URL is allowed by robots.txt.

    Args:
        url: The URL to check
        user_agent: User agent string (default: '*' for all)

    Returns:
        Tuple of (allowed: bool, reason: str | None)
        - (True, None) if allowed
        - (False, reason) if blocked
    """
    domain = _get_domain(url)

    # Skip check for empty domain or non-http URLs
    if not domain:
        return (True, None)

    rp = _load_robots_txt(domain)

    # If robots.txt couldn't be loaded, allow by default
    if not rp.mtime():
        return (True, None)

    if rp.can_fetch(user_agent, url):
        return (True, None)
    else:
        return (False, f"Blocked by robots.txt for {domain}")


def clear_robots_cache() -> None:
    """Clear the robots.txt cache."""
    _robots_cache.clear()
