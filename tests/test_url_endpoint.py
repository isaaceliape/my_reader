"""
Integration tests for the URL endpoint (/api/url) and cache endpoints.

These tests use mocking to avoid requiring the full Kokoro TTS pipeline.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Mock kokoro before importing app
import sys
from unittest.mock import MagicMock

# Create mock for kokoro module
kokoro_mock = MagicMock()
sys.modules["kokoro"] = kokoro_mock

# Now import the app
from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_pipeline():
    """Mock the Kokoro pipeline for testing."""
    with patch("app.pipeline") as mock:
        # Mock pipeline call to return fake audio result
        mock_result = MagicMock()
        mock_result.audio = [0.1, 0.2, 0.3]  # Fake audio samples
        mock.return_value = [mock_result]
        yield mock


class TestUrlEndpoint:
    """Tests for POST /api/url endpoint."""

    def test_valid_url(self, client, mock_pipeline):
        """Test that a valid URL returns 200 with audio."""
        # Mock the process_url_to_audio function
        with patch("app.process_url_to_audio") as mock_process:
            from src.crawler.models import Article

            mock_article = Article(
                url="https://example.com/article",
                title="Test Article",
                text="This is test content from the article.",
                language="en",
            )
            mock_process.return_value = (mock_article, None, False)

            response = client.post(
                "/api/url",
                json={
                    "url": "https://example.com/article",
                    "voice": "af_heart",
                    "speed": 1.0,
                },
            )

            assert response.status_code == 200
            assert response.headers["content-type"] == "audio/wav"
            assert "X-Article-Title" in response.headers
            assert response.headers["X-Article-Title"] == "Test Article"
            assert response.headers["X-Cache"] == "MISS"

    def test_invalid_url_returns_400(self, client):
        """Test that invalid URL returns 400 error."""
        response = client.post(
            "/api/url",
            json={"url": "not-a-valid-url", "voice": "af_heart", "speed": 1.0},
        )
        assert response.status_code == 400

    def test_missing_url_returns_422(self, client):
        """Test that missing URL returns 422 validation error."""
        response = client.post(
            "/api/url",
            json={"voice": "af_heart", "speed": 1.0},
        )
        assert response.status_code == 422

    def test_empty_url_returns_400(self, client):
        """Test that empty URL returns 400 error."""
        response = client.post(
            "/api/url",
            json={"url": "", "voice": "af_heart", "speed": 1.0},
        )
        assert response.status_code == 400

    def test_cache_hit_header(self, client, mock_pipeline):
        """Test that cache hit is indicated in headers."""
        with patch("app.process_url_to_audio") as mock_process:
            from src.crawler.models import Article

            mock_article = Article(
                url="https://example.com/cached",
                title="Cached Article",
                text="This article was cached.",
                language="en",
            )
            # Third parameter is cache_hit=True
            mock_process.return_value = (mock_article, None, True)

            response = client.post(
                "/api/url",
                json={
                    "url": "https://example.com/cached",
                    "voice": "af_heart",
                    "speed": 1.0,
                },
            )

            assert response.status_code == 200
            assert response.headers["X-Cache"] == "HIT"


class TestCacheInvalidation:
    """Tests for cache invalidation endpoints."""

    def test_cache_invalidate_success(self, client):
        """Test cache invalidation endpoint."""
        response = client.request(
            "DELETE",
            "/api/cache",
            json="https://example.com/test",
        )
        # Returns success or not_found, both are 200
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["success", "not_found"]

    def test_cache_invalidate_missing_url(self, client):
        """Test cache invalidation without URL returns 422."""
        response = client.request(
            "DELETE",
            "/api/cache",
            json=None,
        )
        assert response.status_code == 422

    def test_cache_clear_all(self, client):
        """Test clearing all cache."""
        response = client.delete("/api/cache/all")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "cache cleared" in data["message"].lower()


class TestUrlValidation:
    """Tests for URL validation logic."""

    def test_malformed_url_rejected(self, client):
        """Test that malformed URLs are rejected."""
        malformed_urls = [
            "htp://invalid",  # Wrong scheme
            "://missing-scheme.com",
            "ftp://wrong-protocol.com",  # FTP not supported
        ]

        for url in malformed_urls:
            response = client.post(
                "/api/url",
                json={"url": url, "voice": "af_heart", "speed": 1.0},
            )
            assert response.status_code in [400, 422], f"URL {url} should be rejected"

    def test_no_text_content_returns_400(self, client, mock_pipeline):
        """Test that URL with no extractable text returns 400."""
        with patch("app.process_url_to_audio") as mock_process:
            from src.crawler.models import Article

            # Article with empty text
            mock_article = Article(
                url="https://example.com/empty",
                title="Empty Article",
                text="",  # No text content
                language="en",
            )
            mock_process.return_value = (mock_article, None, False)

            response = client.post(
                "/api/url",
                json={
                    "url": "https://example.com/empty",
                    "voice": "af_heart",
                    "speed": 1.0,
                },
            )

            assert response.status_code == 400
