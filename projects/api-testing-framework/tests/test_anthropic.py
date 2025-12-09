"""
Tests for the Anthropic API Client.

These tests verify both mock and live functionality.
"""

import pytest
from pathlib import Path

from config import api_config
from anthropic_client import AnthropicClient, FIXTURES_DIR


class TestAnthropicClientMock:
    """Tests using mock mode (no API calls)."""

    def test_client_respects_config_mode(self, mock_mode):
        """Client should check config for mode."""
        client = AnthropicClient()
        assert client.is_live is False

        api_config.set_override("anthropic", "LIVE")
        assert client.is_live is True

    def test_mock_mode_requires_fixture(self, mock_mode):
        """In mock mode, missing fixture should raise error."""
        client = AnthropicClient()

        with pytest.raises(FileNotFoundError) as exc_info:
            client.generate("This prompt has no fixture saved")

        assert "No fixture found" in str(exc_info.value)

    def test_fixture_path_is_deterministic(self, mock_mode):
        """Same prompt should always generate same fixture path."""
        client = AnthropicClient()

        path1 = client._get_fixture_path("Hello world")
        path2 = client._get_fixture_path("Hello world")
        path3 = client._get_fixture_path("Different prompt")

        assert path1 == path2
        assert path1 != path3

    def test_default_model(self, mock_mode):
        """Should use claude-3-5-sonnet by default."""
        client = AnthropicClient()
        assert "claude-3-5-sonnet" in client.model

    def test_custom_model(self, mock_mode):
        """Should accept custom model."""
        client = AnthropicClient(model="claude-3-haiku-20240307")
        assert client.model == "claude-3-haiku-20240307"


@pytest.mark.live
class TestAnthropicClientLive:
    """
    Tests that make real API calls.

    Run with: pytest -m live
    Skip with: pytest -m "not live"
    """

    def test_live_api_connection(self, live_mode):
        """Verify we can connect to the live Anthropic API."""
        client = AnthropicClient()

        response = client.generate("Say 'Hello, test!' and nothing else.")

        assert "text" in response
        assert len(response["text"]) > 0
        print(f"\n[LIVE RESPONSE] {response['text']}")

    def test_live_generates_fixture(self, live_mode, tmp_path, monkeypatch):
        """Live mode should save fixture for future mock runs."""
        # Use temp directory for fixtures
        monkeypatch.setattr("anthropic_client.FIXTURES_DIR", tmp_path)

        client = AnthropicClient(capture_fixtures=True)
        prompt = "What is 2 + 2? Answer with just the number."

        response = client.generate(prompt)

        # Check fixture was saved
        fixture_files = list(tmp_path.glob("*.json"))
        assert len(fixture_files) == 1

        # Verify fixture content
        import json
        with open(fixture_files[0]) as f:
            fixture = json.load(f)

        assert fixture["prompt"] == prompt
        assert "text" in fixture["response"]

    def test_fixture_replay_matches_live(self, config_snapshot, tmp_path, monkeypatch):
        """Fixture replay should return same response as live call."""
        monkeypatch.setattr("anthropic_client.FIXTURES_DIR", tmp_path)

        client = AnthropicClient(capture_fixtures=True)
        prompt = "What color is the sky? One word answer."

        # First call: LIVE - captures fixture
        api_config.global_mode = "LIVE"
        live_response = client.generate(prompt)

        # Second call: MOCK - should use fixture
        api_config.global_mode = "MOCK"
        mock_response = client.generate(prompt)

        assert mock_response == live_response


class TestAnthropicClientIntegration:
    """Integration tests combining mock and live."""

    def test_can_switch_modes_mid_test(self, config_snapshot):
        """Should be able to switch between mock and live."""
        client = AnthropicClient()

        # Start in mock
        api_config.global_mode = "MOCK"
        assert client.is_live is False

        # Switch to live
        api_config.global_mode = "LIVE"
        assert client.is_live is True

        # Override back to mock
        api_config.set_override("anthropic", "MOCK")
        assert client.is_live is False
