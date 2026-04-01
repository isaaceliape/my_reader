"""
HTTP client wrapper for fetching web pages.
"""

import httpx
from .models import CrawlResult, Article


class CrawlerClient:
    """HTTP client for crawling web pages with automatic retries and error handling."""

    def __init__(
        self,
        timeout: float = 30.0,
        follow_redirects: bool = True,
        headers: dict | None = None,
    ):
        """Initialize the crawler client.

        Args:
            timeout: Request timeout in seconds
            follow_redirects: Whether to follow HTTP redirects
            headers: Custom headers to send with requests
        """
        self.client = httpx.Client(
            timeout=timeout,
            follow_redirects=follow_redirects,
            headers=headers
            or {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            },
        )

    def fetch(self, url: str) -> CrawlResult:
        """Fetch a URL and return the response content.

        Args:
            url: The URL to fetch

        Returns:
            CrawlResult with success status and article data or error
        """
        try:
            response = self.client.get(url)
            response.raise_for_status()

            # httpx automatically detects encoding, use response.text
            html = response.text

            return CrawlResult(
                success=True,
                article=Article(url=url, title="", text="", html=html),
                error=None,
            )

        except httpx.HTTPStatusError as e:
            return CrawlResult(
                success=False,
                article=None,
                error=f"HTTP error {e.response.status_code}: {e.response.reason_phrase}",
            )
        except httpx.RequestError as e:
            return CrawlResult(
                success=False, article=None, error=f"Request failed: {str(e)}"
            )
        except Exception as e:
            return CrawlResult(success=False, article=None, error=str(e))

    def close(self):
        """Close the underlying HTTP client."""
        self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
