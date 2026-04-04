"""
Unit tests for app lifecycle, device detection, and configuration.
"""

import pytest
from unittest.mock import patch, MagicMock
import sys

# Mock kokoro before importing app
kokoro_mock = MagicMock()
sys.modules["kokoro"] = kokoro_mock

# Import app module for testing internal functions
import app as app_module


class TestDeviceDetection:
    """Tests for get_device() function."""

    def test_device_detection_mps_available(self):
        """Test device detection when MPS is available."""
        with patch("app.torch.backends.mps.is_available", return_value=True):
            with patch("app.torch.cuda.is_available", return_value=False):
                device = app_module.get_device()
                assert device == "mps"

    def test_device_detection_cuda_available(self):
        """Test device detection when CUDA is available."""
        with patch("app.torch.backends.mps.is_available", return_value=False):
            with patch("app.torch.cuda.is_available", return_value=True):
                device = app_module.get_device()
                assert device == "cuda"

    def test_device_detection_cpu_fallback(self):
        """Test device detection falls back to CPU when no GPU available."""
        with patch("app.torch.backends.mps.is_available", return_value=False):
            with patch("app.torch.cuda.is_available", return_value=False):
                device = app_module.get_device()
                assert device == "cpu"

    def test_device_detection_mps_priority(self):
        """Test that MPS takes priority over CUDA when both available."""
        with patch("app.torch.backends.mps.is_available", return_value=True):
            with patch("app.torch.cuda.is_available", return_value=True):
                device = app_module.get_device()
                assert device == "mps"  # MPS checked first


class TestKokoroPipelineLoading:
    """Tests for load_kokoro_pipeline() function."""

    def test_pipeline_loads_successfully(self):
        """Test that pipeline loads successfully."""
        with patch("app.get_device", return_value="mps"):
            with patch("app.KPipeline") as mock_pipeline_class:
                mock_instance = MagicMock()
                mock_pipeline_class.return_value = mock_instance

                # Temporarily set pipeline to None
                original_pipeline = app_module.pipeline
                app_module.pipeline = None

                try:
                    result = app_module.load_kokoro_pipeline()

                    assert result is True
                    assert app_module.pipeline is not None
                    mock_pipeline_class.assert_called_once()
                finally:
                    # Restore original pipeline
                    app_module.pipeline = original_pipeline

    def test_pipeline_load_failure(self):
        """Test that pipeline load failure is handled gracefully."""
        with patch("app.get_device", return_value="mps"):
            with patch("app.KPipeline") as mock_pipeline_class:
                mock_pipeline_class.side_effect = Exception("Failed to load")

                # Temporarily set pipeline to None
                original_pipeline = app_module.pipeline
                app_module.pipeline = None

                try:
                    result = app_module.load_kokoro_pipeline()

                    assert result is False
                    assert app_module.pipeline is None
                finally:
                    # Restore original pipeline
                    app_module.pipeline = original_pipeline

    def test_pipeline_uses_correct_lang_code(self):
        """Test that pipeline is initialized with correct language code."""
        with patch("app.get_device", return_value="mps"):
            with patch("app.KPipeline") as mock_pipeline_class:
                mock_instance = MagicMock()
                mock_pipeline_class.return_value = mock_instance

                original_pipeline = app_module.pipeline
                app_module.pipeline = None

                try:
                    app_module.load_kokoro_pipeline()

                    # Check that KPipeline was called with lang_code="a" (English)
                    call_args = mock_pipeline_class.call_args
                    assert call_args[1]["lang_code"] == "a"
                finally:
                    app_module.pipeline = original_pipeline

    def test_pipeline_uses_detected_device(self):
        """Test that pipeline uses the detected device."""
        with patch("app.get_device", return_value="mps"):
            with patch("app.KPipeline") as mock_pipeline_class:
                mock_instance = MagicMock()
                mock_pipeline_class.return_value = mock_instance

                original_pipeline = app_module.pipeline
                app_module.pipeline = None

                try:
                    app_module.load_kokoro_pipeline()

                    call_args = mock_pipeline_class.call_args
                    assert call_args[1]["device"] == "mps"
                finally:
                    app_module.pipeline = original_pipeline


class TestGenerateAudio:
    """Tests for generate_audio() function."""

    def test_generate_audio_requires_pipeline(self):
        """Test that generate_audio raises error when pipeline not loaded."""
        with patch("app.pipeline", None):
            with pytest.raises(RuntimeError, match="TTS pipeline not loaded"):
                app_module.generate_audio("Hello", "af_heart")

    def test_generate_audio_with_mock_pipeline(self):
        """Test audio generation with mocked pipeline."""
        mock_result = MagicMock()
        mock_result.audio = [0.1, 0.2, 0.3]

        mock_pipeline = MagicMock()
        mock_pipeline.return_value = [mock_result]

        with patch("app.pipeline", mock_pipeline):
            audio_data = app_module.generate_audio("Hello", "af_heart", 1.0)

            assert audio_data is not None
            assert len(audio_data) > 0
            # Should be WAV format (starts with RIFF header)
            assert audio_data[:4] == b"RIFF"

    def test_generate_audio_with_torch_tensor(self):
        """Test audio generation handles torch.Tensor audio."""
        import torch

        mock_result = MagicMock()
        mock_result.audio = torch.tensor([0.1, 0.2, 0.3])

        mock_pipeline = MagicMock()
        mock_pipeline.return_value = [mock_result]

        with patch("app.pipeline", mock_pipeline):
            audio_data = app_module.generate_audio("Hello", "af_heart")

            assert audio_data is not None
            assert audio_data[:4] == b"RIFF"

    def test_generate_audio_concatenates_segments(self):
        """Test that multiple audio segments are concatenated."""
        mock_result1 = MagicMock()
        mock_result1.audio = [0.1, 0.2]
        mock_result2 = MagicMock()
        mock_result2.audio = [0.3, 0.4]

        mock_pipeline = MagicMock()
        mock_pipeline.return_value = [mock_result1, mock_result2]

        with patch("app.pipeline", mock_pipeline):
            audio_data = app_module.generate_audio("Long text", "af_heart")

            assert audio_data is not None
            assert audio_data[:4] == b"RIFF"

    def test_generate_audio_with_custom_speed(self):
        """Test audio generation with custom speed parameter."""
        mock_result = MagicMock()
        mock_result.audio = [0.1, 0.2, 0.3]

        mock_pipeline = MagicMock()
        mock_pipeline.return_value = [mock_result]

        with patch("app.pipeline", mock_pipeline):
            audio_data = app_module.generate_audio("Hello", "af_heart", speed=1.5)

            # Verify pipeline was called with speed parameter
            call_args = mock_pipeline.call_args
            assert call_args[1]["speed"] == 1.5


class TestLifespan:
    """Tests for FastAPI lifespan context manager."""

    @pytest.mark.asyncio
    async def test_lifespan_loads_pipeline(self):
        """Test that lifespan context manager loads Kokoro pipeline on startup."""
        with patch("app.load_kokoro_pipeline") as mock_load:
            mock_load.return_value = True

            # Test the lifespan context manager
            async with app_module.lifespan(app_module.app):
                # Inside the context, startup should have completed
                mock_load.assert_called_once()

            # After exiting context, shutdown would occur (nothing to test here)


class TestAppConfiguration:
    """Tests for FastAPI app configuration."""

    def test_app_has_title(self):
        """Test that FastAPI app has a title."""
        assert app_module.app.title == "Local TTS Web App"

    def test_app_has_description(self):
        """Test that FastAPI app has a description."""
        assert "Text-to-Speech" in app_module.app.description
        assert "Kokoro" in app_module.app.description

    def test_app_has_version(self):
        """Test that FastAPI app has a version."""
        assert app_module.app.version == "0.1.0"

    def test_cors_middleware_configured(self):
        """Test that CORS middleware is configured."""
        # FastAPI stores middleware in user_middleware before building the stack
        # Check that at least one middleware is registered (CORS)
        assert len(app_module.app.user_middleware) > 0, "Expected CORS middleware to be registered"
