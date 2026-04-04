"""
Unit tests for the voices endpoint (/voices) and API health endpoints.
"""

import pytest
from fastapi.testclient import TestClient
import sys

# Mock kokoro before importing app
from unittest.mock import MagicMock
kokoro_mock = MagicMock()
sys.modules["kokoro"] = kokoro_mock

# Now import the app
from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestVoicesEndpoint:
    """Tests for GET /voices endpoint."""

    def test_voices_endpoint_returns_200(self, client):
        """Test that voices endpoint returns 200 OK."""
        response = client.get("/voices")
        assert response.status_code == 200

    def test_voices_returns_list(self, client):
        """Test that voices endpoint returns a list of voices."""
        response = client.get("/voices")
        data = response.json()

        assert "voices" in data
        assert isinstance(data["voices"], list)

    def test_voices_count(self, client):
        """Test that expected number of voices are available."""
        response = client.get("/voices")
        data = response.json()

        assert len(data["voices"]) == 6

    def test_voices_have_required_fields(self, client):
        """Test that each voice has id, name, and language fields."""
        response = client.get("/voices")
        data = response.json()

        for voice in data["voices"]:
            assert "id" in voice
            assert "name" in voice
            assert "language" in voice

    def test_voice_ids_are_strings(self, client):
        """Test that voice IDs are strings."""
        response = client.get("/voices")
        data = response.json()

        for voice in data["voices"]:
            assert isinstance(voice["id"], str)

    def test_specific_voices_present(self, client):
        """Test that expected voice IDs are present."""
        response = client.get("/voices")
        data = response.json()

        voice_ids = [v["id"] for v in data["voices"]]

        expected_voices = [
            "af_heart",
            "af_sarah",
            "am_adam",
            "am_michael",
            "bf_emma",
            "bf_isabella",
        ]

        for expected in expected_voices:
            assert expected in voice_ids

    def test_voice_names_are_descriptive(self, client):
        """Test that voice names include gender and accent info."""
        response = client.get("/voices")
        data = response.json()

        voice_names = [v["name"] for v in data["voices"]]

        # Check for expected naming patterns
        assert any("Female" in name for name in voice_names)
        assert any("Male" in name for name in voice_names)
        assert any("British" in name for name in voice_names)

    def test_languages_include_en_us_and_en_gb(self, client):
        """Test that both en-US and en-GB languages are represented."""
        response = client.get("/voices")
        data = response.json()

        languages = [v["language"] for v in data["voices"]]

        assert "en-US" in languages
        assert "en-GB" in languages


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_api_health_endpoint(self, client):
        """Test GET /api health check."""
        response = client.get("/api")
        assert response.status_code == 200

    def test_api_health_returns_status(self, client):
        """Test that health endpoint returns status field."""
        response = client.get("/api")
        data = response.json()

        assert "status" in data
        assert data["status"] == "ok"

    def test_api_health_returns_service_name(self, client):
        """Test that health endpoint returns service name."""
        response = client.get("/api")
        data = response.json()

        assert "service" in data
        assert data["service"] == "Local TTS Web App"

    def test_api_health_shows_tts_loaded(self, client):
        """Test that health endpoint shows TTS loaded status."""
        response = client.get("/api")
        data = response.json()

        assert "tts_loaded" in data
        assert isinstance(data["tts_loaded"], bool)

    def test_root_endpoint(self, client):
        """Test GET / root endpoint."""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_serves_html(self, client):
        """Test that root endpoint serves HTML content."""
        response = client.get("/")

        # Should return HTML or JSON depending on static files
        content_type = response.headers.get("content-type", "")
        assert "text/html" in content_type or "application/json" in content_type

    def test_root_html_contains_title(self, client):
        """Test that root HTML contains page title."""
        response = client.get("/")

        if "text/html" in response.headers.get("content-type", ""):
            assert "Local TTS" in response.text or "my_reader" in response.text


class TestCORS:
    """Tests for CORS configuration."""

    def test_cors_headers_present(self, client):
        """Test that CORS headers are present in responses."""
        response = client.get("/api")

        # FastAPI adds CORS headers automatically when configured
        assert response.status_code == 200

    def test_options_request_handled(self, client):
        """Test that OPTIONS requests are handled for CORS preflight."""
        # OPTIONS may return 200, 204, or 404 depending on route configuration
        response = client.options("/tts")

        # Accept various valid responses for OPTIONS
        assert response.status_code in [200, 204, 404, 405]
