"""
Additional Anthropic tests for coverage.

These tests mock the external API to test live code paths
without needing actual API keys.
"""

import pytest
import json
from unittest.mock import Mock, patch
from pathlib import Path

from config import api_config
import anthropic_client
from anthropic_client import AnthropicClient, FIXTURES_DIR


@pytest.mark.mock
class TestAnthropicFixtures:
    """Tests for fixture save/load functionality."""

    def test_load_existing_fixture(self, mock_mode, tmp_path, monkeypatch):
        """Should load fixture from disk when it exists."""
        monkeypatch.setattr("anthropic_client.FIXTURES_DIR", tmp_path)

        client = AnthropicClient()
        prompt = "Test prompt for fixture loading"

        # Create a fixture file manually
        fixture_path = client._get_fixture_path(prompt)
        fixture_data = {
            "prompt": prompt,
            "response": {"text": "Mocked response from fixture"},
            "captured_at": "2025-01-01T00:00:00",
            "model": "claude-3-5-sonnet-20241022"
        }
        with open(fixture_path, "w") as f:
            json.dump(fixture_data, f)

        # Should load and return the fixture
        result = client.generate(prompt)
        assert result["text"] == "Mocked response from fixture"

    def test_save_fixture(self, tmp_path, monkeypatch, config_snapshot):
        """Should save fixture when capture_fixtures is True."""
        monkeypatch.setattr("anthropic_client.FIXTURES_DIR", tmp_path)
        api_config.global_mode = "LIVE"

        # Mock the Anthropic API
        mock_message = Mock()
        mock_message.content = [Mock(text="Generated response")]
        mock_message.model = "claude-3-5-sonnet-20241022"
        mock_message.usage = Mock(input_tokens=10, output_tokens=20)
        mock_message.stop_reason = "end_turn"  # Required for JSON serialization

        mock_client = Mock()
        mock_client.messages.create.return_value = mock_message

        with patch("anthropic.Anthropic", return_value=mock_client):
            client = AnthropicClient(api_key="fake-key", capture_fixtures=True)
            result = client.generate("Test save prompt")

            # Verify fixture was saved
            fixture_files = list(tmp_path.glob("*.json"))
            assert len(fixture_files) == 1


@pytest.mark.mock
class TestAnthropicLiveClientMocked:
    """Tests for live client with mocked external dependencies."""

    def test_live_api_call_mocked(self, config_snapshot, tmp_path, monkeypatch):
        """Test live API call with mocked Anthropic API."""
        monkeypatch.setattr("anthropic_client.FIXTURES_DIR", tmp_path)
        api_config.global_mode = "LIVE"

        mock_message = Mock()
        mock_message.content = [Mock(text="Hello from mocked Claude!")]
        mock_message.model = "claude-3-5-sonnet-20241022"
        mock_message.usage = Mock(input_tokens=5, output_tokens=10)
        mock_message.stop_reason = "end_turn"

        mock_client = Mock()
        mock_client.messages.create.return_value = mock_message

        with patch("anthropic.Anthropic", return_value=mock_client):
            client = AnthropicClient(api_key="test-api-key", capture_fixtures=False)
            result = client.generate("Say hello")

            assert result["text"] == "Hello from mocked Claude!"
            mock_client.messages.create.assert_called_once()

    def test_missing_api_key_raises(self, config_snapshot):
        """Should raise ValueError when API key is missing in LIVE mode."""
        api_config.global_mode = "LIVE"

        with patch.dict("os.environ", {}, clear=True):
            client = AnthropicClient(api_key=None)
            client.api_key = None

            with pytest.raises(ValueError) as exc_info:
                client.generate("Test prompt")

            assert "ANTHROPIC_API_KEY not found" in str(exc_info.value)

    def test_import_error_handling(self, config_snapshot):
        """Should raise ImportError with helpful message if anthropic not installed."""
        api_config.global_mode = "LIVE"

        with patch.dict("sys.modules", {"anthropic": None}):
            with patch("builtins.__import__", side_effect=ImportError("No module")):
                client = AnthropicClient(api_key="test-key")

                with pytest.raises(ImportError) as exc_info:
                    client._get_live_client()

                assert "anthropic package not installed" in str(exc_info.value)
