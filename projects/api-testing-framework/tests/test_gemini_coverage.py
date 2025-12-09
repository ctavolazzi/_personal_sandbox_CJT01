"""
Additional Gemini tests for coverage.

These tests mock the external API to test live code paths
without needing actual API keys.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from config import api_config
import gemini_client
from gemini_client import GeminiClient, FIXTURES_DIR, get_client, generate, generate_text


@pytest.mark.mock
class TestGeminiFixtures:
    """Tests for fixture save/load functionality."""

    def test_load_existing_fixture(self, mock_mode, tmp_path, monkeypatch):
        """Should load fixture from disk when it exists."""
        monkeypatch.setattr("gemini_client.FIXTURES_DIR", tmp_path)

        client = GeminiClient()
        prompt = "Test prompt for fixture loading"

        # Create a fixture file manually
        fixture_path = client._get_fixture_path(prompt)
        fixture_data = {
            "prompt": prompt,
            "response": {"text": "Mocked response from fixture"},
            "captured_at": "2025-01-01T00:00:00",
            "model": "gemini-2.5-flash"
        }
        with open(fixture_path, "w") as f:
            json.dump(fixture_data, f)

        # Should load and return the fixture
        result = client.generate(prompt)
        assert result["text"] == "Mocked response from fixture"

    def test_save_fixture(self, tmp_path, monkeypatch, config_snapshot):
        """Should save fixture when capture_fixtures is True."""
        monkeypatch.setattr("gemini_client.FIXTURES_DIR", tmp_path)
        api_config.global_mode = "LIVE"

        # Mock the Google API
        mock_response = Mock()
        mock_response.text = "Generated response"
        mock_response.prompt_feedback = None

        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response

        with patch("google.generativeai.configure"), \
             patch("google.generativeai.GenerativeModel", return_value=mock_model):

            client = GeminiClient(api_key="fake-key", capture_fixtures=True)
            result = client.generate("Test save prompt")

            # Verify fixture was saved
            fixture_files = list(tmp_path.glob("*.json"))
            assert len(fixture_files) == 1

            # Verify fixture content
            with open(fixture_files[0]) as f:
                saved = json.load(f)
            assert saved["prompt"] == "Test save prompt"
            assert saved["response"]["text"] == "Generated response"


@pytest.mark.mock
class TestGeminiLiveClientMocked:
    """Tests for live client with mocked external dependencies."""

    def test_live_api_call_mocked(self, config_snapshot, tmp_path, monkeypatch):
        """Test live API call with mocked Google API."""
        monkeypatch.setattr("gemini_client.FIXTURES_DIR", tmp_path)
        api_config.global_mode = "LIVE"

        mock_response = Mock()
        mock_response.text = "Hello from mocked Gemini!"
        mock_response.prompt_feedback = "SAFETY_OK"

        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response

        with patch("google.generativeai.configure") as mock_configure, \
             patch("google.generativeai.GenerativeModel", return_value=mock_model):

            client = GeminiClient(api_key="test-api-key", capture_fixtures=False)
            result = client.generate("Say hello")

            assert result["text"] == "Hello from mocked Gemini!"
            assert "SAFETY_OK" in result["prompt_feedback"]
            mock_model.generate_content.assert_called_once_with("Say hello")
            mock_configure.assert_called_once_with(api_key="test-api-key")

    def test_missing_api_key_raises(self, config_snapshot):
        """Should raise ValueError when API key is missing in LIVE mode."""
        api_config.global_mode = "LIVE"

        # Clear any env var
        with patch.dict("os.environ", {}, clear=True):
            client = GeminiClient(api_key=None)
            client.api_key = None  # Force no key

            with pytest.raises(ValueError) as exc_info:
                client.generate("Test prompt")

            assert "GEMINI_API_KEY not found" in str(exc_info.value)

    def test_import_error_handling(self, config_snapshot):
        """Should raise ImportError with helpful message if google-generativeai not installed."""
        api_config.global_mode = "LIVE"

        with patch.dict("sys.modules", {"google.generativeai": None}):
            with patch("builtins.__import__", side_effect=ImportError("No module")):
                client = GeminiClient(api_key="test-key")

                with pytest.raises(ImportError) as exc_info:
                    client._get_live_client()

                assert "google-generativeai package not installed" in str(exc_info.value)


@pytest.mark.mock
class TestGeminiConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_get_client_creates_singleton(self, mock_mode):
        """get_client should return same instance on repeated calls."""
        # Reset the module-level client
        gemini_client._default_client = None

        client1 = get_client()
        client2 = get_client()

        assert client1 is client2

    def test_generate_uses_default_client(self, mock_mode, tmp_path, monkeypatch):
        """Module-level generate should use default client."""
        monkeypatch.setattr("gemini_client.FIXTURES_DIR", tmp_path)
        gemini_client._default_client = None

        # Create fixture for the prompt
        client = GeminiClient()
        prompt = "Module level test"
        fixture_path = client._get_fixture_path(prompt)
        fixture_data = {
            "prompt": prompt,
            "response": {"text": "Module response"},
            "captured_at": "2025-01-01T00:00:00",
            "model": "gemini-2.5-flash"
        }
        with open(fixture_path, "w") as f:
            json.dump(fixture_data, f)

        gemini_client._default_client = None
        result = generate(prompt)
        assert result["text"] == "Module response"

    def test_generate_text_returns_string(self, mock_mode, tmp_path, monkeypatch):
        """generate_text should return just the text string."""
        monkeypatch.setattr("gemini_client.FIXTURES_DIR", tmp_path)
        gemini_client._default_client = None

        client = GeminiClient()
        prompt = "Text only test"
        fixture_path = client._get_fixture_path(prompt)
        fixture_data = {
            "prompt": prompt,
            "response": {"text": "Just text"},
            "captured_at": "2025-01-01T00:00:00",
            "model": "gemini-2.5-flash"
        }
        with open(fixture_path, "w") as f:
            json.dump(fixture_data, f)

        gemini_client._default_client = None
        result = generate_text(prompt)
        assert result == "Just text"
        assert isinstance(result, str)

    def test_client_generate_text_method(self, mock_mode, tmp_path, monkeypatch):
        """Client.generate_text should return just text."""
        monkeypatch.setattr("gemini_client.FIXTURES_DIR", tmp_path)

        client = GeminiClient()
        prompt = "Client method test"
        fixture_path = client._get_fixture_path(prompt)
        fixture_data = {
            "prompt": prompt,
            "response": {"text": "Client text"},
            "captured_at": "2025-01-01T00:00:00",
            "model": "gemini-2.5-flash"
        }
        with open(fixture_path, "w") as f:
            json.dump(fixture_data, f)

        result = client.generate_text(prompt)
        assert result == "Client text"
