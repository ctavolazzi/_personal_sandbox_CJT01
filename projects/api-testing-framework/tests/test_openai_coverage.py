"""
Additional OpenAI tests for coverage.

These tests mock the external API to test live code paths
without needing actual API keys.
"""

import pytest
import json
from unittest.mock import Mock, patch
from pathlib import Path

from config import api_config
import openai_client
from openai_client import OpenAIClient, FIXTURES_DIR


@pytest.mark.mock
class TestOpenAIFixtures:
    """Tests for fixture save/load functionality."""

    def test_load_existing_fixture(self, mock_mode, tmp_path, monkeypatch):
        """Should load fixture from disk when it exists."""
        monkeypatch.setattr("openai_client.FIXTURES_DIR", tmp_path)

        client = OpenAIClient()
        prompt = "Test prompt for fixture loading"

        # Create a fixture file manually
        fixture_path = client._get_fixture_path(prompt)
        fixture_data = {
            "prompt": prompt,
            "response": {"text": "Mocked response from fixture"},
            "captured_at": "2025-01-01T00:00:00",
            "model": "gpt-4o-mini"
        }
        with open(fixture_path, "w") as f:
            json.dump(fixture_data, f)

        # Should load and return the fixture
        result = client.generate(prompt)
        assert result["text"] == "Mocked response from fixture"

    def test_save_fixture(self, tmp_path, monkeypatch, config_snapshot):
        """Should save fixture when capture_fixtures is True."""
        monkeypatch.setattr("openai_client.FIXTURES_DIR", tmp_path)
        api_config.global_mode = "LIVE"

        # Mock the OpenAI API
        mock_choice = Mock()
        mock_choice.message.content = "Generated response"

        mock_response = Mock()
        mock_response.choices = [mock_choice]
        mock_response.model = "gpt-4o-mini"
        mock_response.usage = Mock(prompt_tokens=10, completion_tokens=20, total_tokens=30)

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch("openai.OpenAI", return_value=mock_client):
            client = OpenAIClient(api_key="fake-key", capture_fixtures=True)
            result = client.generate("Test save prompt")

            # Verify fixture was saved
            fixture_files = list(tmp_path.glob("*.json"))
            assert len(fixture_files) == 1


@pytest.mark.mock
class TestOpenAILiveClientMocked:
    """Tests for live client with mocked external dependencies."""

    def test_live_api_call_mocked(self, config_snapshot, tmp_path, monkeypatch):
        """Test live API call with mocked OpenAI API."""
        monkeypatch.setattr("openai_client.FIXTURES_DIR", tmp_path)
        api_config.global_mode = "LIVE"

        mock_choice = Mock()
        mock_choice.message.content = "Hello from mocked GPT!"

        mock_response = Mock()
        mock_response.choices = [mock_choice]
        mock_response.model = "gpt-4o-mini"
        mock_response.usage = Mock(prompt_tokens=5, completion_tokens=10, total_tokens=15)

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch("openai.OpenAI", return_value=mock_client):
            client = OpenAIClient(api_key="test-api-key", capture_fixtures=False)
            result = client.generate("Say hello")

            assert result["text"] == "Hello from mocked GPT!"
            mock_client.chat.completions.create.assert_called_once()

    def test_missing_api_key_raises(self, config_snapshot):
        """Should raise ValueError when API key is missing in LIVE mode."""
        api_config.global_mode = "LIVE"

        with patch.dict("os.environ", {}, clear=True):
            client = OpenAIClient(api_key=None)
            client.api_key = None

            with pytest.raises(ValueError) as exc_info:
                client.generate("Test prompt")

            assert "OPENAI_API_KEY not found" in str(exc_info.value)

    def test_import_error_handling(self, config_snapshot):
        """Should raise ImportError with helpful message if openai not installed."""
        api_config.global_mode = "LIVE"

        with patch.dict("sys.modules", {"openai": None}):
            with patch("builtins.__import__", side_effect=ImportError("No module")):
                client = OpenAIClient(api_key="test-key")

                with pytest.raises(ImportError) as exc_info:
                    client._get_live_client()

                assert "openai package not installed" in str(exc_info.value)
