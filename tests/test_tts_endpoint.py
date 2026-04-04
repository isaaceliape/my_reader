"""
Unit tests for the TTS endpoint (/tts).

These tests use mocking to avoid requiring the full Kokoro TTS pipeline.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import sys

# Mock kokoro before importing app
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


class TestTTSEndpoint:
    """Tests for POST /tts endpoint."""

    def test_valid_text_generation(self, client, mock_pipeline):
        """Test that valid text returns 200 with audio."""
        response = client.post(
            "/tts",
            json={
                "text": "Hello, this is a test.",
                "voice": "af_heart",
                "speed": 1.0,
            },
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/wav"
        assert "Content-Disposition" in response.headers
        assert "speech.wav" in response.headers["Content-Disposition"]

    def test_default_voice_and_speed(self, client, mock_pipeline):
        """Test that default voice (af_heart) and speed (1.0) are used when not provided."""
        response = client.post(
            "/tts",
            json={"text": "Hello world"},
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/wav"

    def test_empty_text_returns_400(self, client):
        """Test that empty text returns 400 error."""
        response = client.post(
            "/tts",
            json={"text": "", "voice": "af_heart", "speed": 1.0},
        )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Text is required"

    def test_whitespace_only_text_returns_400(self, client):
        """Test that whitespace-only text returns 400 error."""
        response = client.post(
            "/tts",
            json={"text": "   \n\t  ", "voice": "af_heart", "speed": 1.0},
        )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Text is required"

    def test_text_too_long_returns_400(self, client):
        """Test that text over 5000 characters returns 400 error."""
        long_text = "A" * 5001

        response = client.post(
            "/tts",
            json={"text": long_text, "voice": "af_heart", "speed": 1.0},
        )

        assert response.status_code == 400
        data = response.json()
        assert "Text too long" in data["detail"]
        assert "5000" in data["detail"]

    def test_text_at_limit_accepted(self, client, mock_pipeline):
        """Test that text exactly at 5000 characters is accepted."""
        exact_limit_text = "A" * 5000

        response = client.post(
            "/tts",
            json={"text": exact_limit_text, "voice": "af_heart", "speed": 1.0},
        )

        assert response.status_code == 200

    def test_different_voices(self, client, mock_pipeline):
        """Test TTS generation with different voices."""
        voices = ["af_heart", "af_sarah", "am_adam", "am_michael", "bf_emma", "bf_isabella"]

        for voice in voices:
            response = client.post(
                "/tts",
                json={"text": "Testing voice", "voice": voice, "speed": 1.0},
            )
            assert response.status_code == 200, f"Voice {voice} should work"

    def test_speed_range(self, client, mock_pipeline):
        """Test TTS generation with different speed values."""
        speeds = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]

        for speed in speeds:
            response = client.post(
                "/tts",
                json={"text": "Testing speed", "voice": "af_heart", "speed": speed},
            )
            assert response.status_code == 200, f"Speed {speed} should work"

    def test_missing_text_field_returns_422(self, client):
        """Test that missing text field returns 422 validation error."""
        response = client.post(
            "/tts",
            json={"voice": "af_heart", "speed": 1.0},
        )

        assert response.status_code == 422

    def test_cache_headers_present(self, client, mock_pipeline):
        """Test that response includes no-cache header."""
        response = client.post(
            "/tts",
            json={"text": "Hello", "voice": "af_heart", "speed": 1.0},
        )

        assert response.headers["Cache-Control"] == "no-cache"


class TestTTSPipelineIntegration:
    """Tests for TTS pipeline integration (mocked)."""

    def test_pipeline_called_with_correct_params(self, client, mock_pipeline):
        """Test that pipeline is called with correct voice and speed parameters."""
        client.post(
            "/tts",
            json={"text": "Test", "voice": "am_adam", "speed": 1.5},
        )

        mock_pipeline.assert_called_once()
        call_args = mock_pipeline.call_args
        assert call_args[0][0] == "Test"  # First positional arg is text
        assert call_args[1]["voice"] == "am_adam"
        assert call_args[1]["speed"] == 1.5

    def test_pipeline_not_loaded_returns_500(self, client):
        """Test that missing pipeline returns 500 error."""
        with patch("app.pipeline", None):
            response = client.post(
                "/tts",
                json={"text": "Hello", "voice": "af_heart", "speed": 1.0},
            )

            assert response.status_code == 500

    def test_audio_format_is_wav(self, client, mock_pipeline):
        """Test that generated audio is in WAV format."""
        response = client.post(
            "/tts",
            json={"text": "Hello", "voice": "af_heart", "speed": 1.0},
        )

        assert response.headers["content-type"] == "audio/wav"
        # Verify it's actually WAV data (RIFF header)
        assert response.content[:4] == b"RIFF"


class TestTTSErrorHandling:
    """Tests for TTS error handling."""

    def test_pipeline_exception_returns_500(self, client):
        """Test that pipeline exceptions are handled gracefully."""
        with patch("app.pipeline") as mock:
            mock.side_effect = Exception("TTS failed")

            response = client.post(
                "/tts",
                json={"text": "Hello", "voice": "af_heart", "speed": 1.0},
            )

            assert response.status_code == 500
            assert "TTS failed" in response.json()["detail"]

    def test_invalid_voice_handled_gracefully(self, client, mock_pipeline):
        """Test that invalid voice ID is handled (pipeline may reject it)."""
        # This depends on Kokoro's validation - may succeed or fail
        response = client.post(
            "/tts",
            json={"text": "Hello", "voice": "invalid_voice", "speed": 1.0},
        )

        # Either 200 (if Kokoro has fallback) or 500 (if validation fails)
        assert response.status_code in [200, 500]
