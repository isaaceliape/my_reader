"""
Unit tests for the crawler client module.
"""

import pytest
from unittest.mock import patch, MagicMock
import httpx

from src.crawler.client import CrawlerClient


class TestCrawlerClientInit:
    """Tests for CrawlerClient initialization."""

    def test_client_creates_httpx_client(self):
        """Test that client creates an httpx.Client."""
        client = CrawlerClient()
        assert client.client is not None
        assert isinstance(client.client, httpx.Client)
        client.close()

    def test_client_sets_user_agent(self):
        """Test that client sets a custom User-Agent header."""
        client = CrawlerClient()
        assert "User-Agent" in client.client.headers
        assert "Mozilla" in client.client.headers["User-Agent"]
        client.close()

    def test_client_sets_timeout(self):
        """Test that client has timeout configured."""
        client = CrawlerClient()
        assert client.client.timeout is not None
        client.close()

    def test_client_with_custom_timeout(self):
        """Test that client accepts custom timeout."""
        client = CrawlerClient(timeout=60.0)
        assert client.client.timeout.connect == 60.0
        client.close()

    def test_client_follows_redirects(self):
        """Test that client follows redirects by default."""
        client = CrawlerClient()
        assert client.client.follow_redirects is True
        client.close()

    def test_client_custom_headers(self):
        """Test that client accepts custom headers."""
        custom_headers = {"X-Custom": "value"}
        client = CrawlerClient(headers=custom_headers)
        assert client.client.headers["X-Custom"] == "value"
        client.close()


class TestCrawlerClientFetch:
    """Tests for CrawlerClient.fetch() method."""

    def test_fetch_successful(self):
        """Test successful URL fetch."""
        with patch("httpx.Client.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "<html><body>Test content</body></html>"
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            client = CrawlerClient()
            result = client.fetch("https://example.com")

            assert result.success is True
            assert result.article is not None
            assert result.article.html == "<html><body>Test content</body></html>"
            assert result.error is None
            client.close()

    def test_fetch_404_error(self):
        """Test fetch with 404 error."""
        with patch("httpx.Client.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.reason_phrase = "Not Found"
            mock_get.side_effect = httpx.HTTPStatusError(
                "404 Not Found",
                request=MagicMock(),
                response=mock_response
            )

            client = CrawlerClient()
            result = client.fetch("https://example.com/notfound")

            assert result.success is False
            assert result.error is not None
            assert "404" in result.error
            client.close()

    def test_fetch_403_forbidden(self):
        """Test fetch with 403 forbidden (paywall)."""
        with patch("httpx.Client.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 403
            mock_response.reason_phrase = "Forbidden"
            mock_get.side_effect = httpx.HTTPStatusError(
                "403 Forbidden",
                request=MagicMock(),
                response=mock_response
            )

            client = CrawlerClient()
            result = client.fetch("https://example.com/premium")

            assert result.success is False
            assert result.error is not None
            assert "403" in result.error
            client.close()

    def test_fetch_timeout(self):
        """Test fetch with timeout error."""
        with patch("httpx.Client.get") as mock_get:
            mock_get.side_effect = httpx.ConnectTimeout("Timeout")

            client = CrawlerClient()
            result = client.fetch("https://slow-site.com")

            assert result.success is False
            assert result.error is not None
            client.close()

    def test_fetch_connection_error(self):
        """Test fetch with connection error."""
        with patch("httpx.Client.get") as mock_get:
            mock_get.side_effect = httpx.ConnectError("Connection failed")

            client = CrawlerClient()
            result = client.fetch("https://nonexistent-domain.xyz")

            assert result.success is False
            assert result.error is not None
            client.close()

    def test_fetch_request_exception(self):
        """Test fetch with general request exception."""
        with patch("httpx.Client.get") as mock_get:
            mock_get.side_effect = httpx.RequestError("Network error", request=MagicMock())

            client = CrawlerClient()
            result = client.fetch("https://example.com")

            assert result.success is False
            assert result.error is not None
            client.close()

    def test_fetch_empty_response(self):
        """Test fetch with empty response."""
        with patch("httpx.Client.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = ""
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            client = CrawlerClient()
            result = client.fetch("https://example.com/empty")

            # Should succeed but with empty HTML
            assert result.success is True
            assert result.article is not None
            assert result.article.html == ""
            client.close()

    def test_fetch_uses_correct_url(self):
        """Test that fetch uses the correct URL."""
        with patch("httpx.Client.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "<html></html>"
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            client = CrawlerClient()
            client.fetch("https://example.com/specific-page")

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][0] == "https://example.com/specific-page"
            client.close()

    def test_fetch_handles_http_status_error(self):
        """Test that fetch handles HTTPStatusError correctly."""
        with patch("httpx.Client.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.reason_phrase = "Internal Server Error"
            mock_get.side_effect = httpx.HTTPStatusError(
                "500 Error",
                request=MagicMock(),
                response=mock_response
            )

            client = CrawlerClient()
            result = client.fetch("https://example.com/error")

            assert result.success is False
            assert "500" in result.error
            client.close()


class TestCrawlerClientContextManager:
    """Tests for CrawlerClient as context manager."""

    def test_client_as_context_manager(self):
        """Test using client as context manager."""
        with patch("httpx.Client.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "<html></html>"
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            with CrawlerClient() as client:
                result = client.fetch("https://example.com")
                assert result.success is True

    def test_client_close(self):
        """Test explicit close method."""
        client = CrawlerClient()
        httpx_client = client.client

        client.close()

        # Client should be closed
        assert httpx_client.is_closed is True


class TestCrawlerClientHeaders:
    """Tests for HTTP headers in requests."""

    def test_request_includes_user_agent(self):
        """Test that requests include User-Agent header."""
        with patch("httpx.Client.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "<html></html>"
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            client = CrawlerClient()
            client.fetch("https://example.com")

            # Headers are in the client, passed automatically
            assert "User-Agent" in client.client.headers
            client.close()

    def test_default_user_agent(self):
        """Test that default User-Agent is Chrome on macOS."""
        client = CrawlerClient()
        user_agent = client.client.headers["User-Agent"]

        assert "Mozilla" in user_agent
        assert "Macintosh" in user_agent
        assert "Chrome" in user_agent
        client.close()
