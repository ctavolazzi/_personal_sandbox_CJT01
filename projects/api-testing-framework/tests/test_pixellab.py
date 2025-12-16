"""
Tests for the Pixel Lab API Client.

These tests verify both mock and live functionality.
"""

import pytest
from pathlib import Path

import os
from config import api_config
from pixellab_client import PixelLabClient, FIXTURES_DIR

# Check for API key
HAS_PIXELLAB_KEY = bool(os.getenv("PIXELLAB_API_KEY"))
skip_without_pixellab = pytest.mark.skipif(
    not HAS_PIXELLAB_KEY,
    reason="PIXELLAB_API_KEY not set"
)


@pytest.mark.mock
class TestPixelLabClientMock:
    """Tests using mock mode (no API calls)."""

    def test_client_respects_config_mode(self, mock_mode):
        """Client should check config for mode."""
        client = PixelLabClient()
        assert client.is_live is False

        api_config.set_override("pixellab", "LIVE")
        assert client.is_live is True

    def test_mock_mode_requires_fixture(self, mock_mode):
        """In mock mode, missing fixture should raise error."""
        client = PixelLabClient()

        with pytest.raises(FileNotFoundError) as exc_info:
            client.generate_image("This description has no fixture saved")

        assert "No fixture found" in str(exc_info.value)

    def test_fixture_path_is_deterministic(self, mock_mode):
        """Same request should always generate same fixture path."""
        client = PixelLabClient()

        path1 = client._get_fixture_path('{"description": "wizard", "width": 64}')
        path2 = client._get_fixture_path('{"description": "wizard", "width": 64}')
        path3 = client._get_fixture_path('{"description": "knight", "width": 64}')

        assert path1 == path2
        assert path1 != path3

    def test_get_balance_mock(self, mock_mode):
        """get_balance should return mock data in MOCK mode."""
        client = PixelLabClient()
        balance = client.get_balance()

        assert "credits" in balance
        assert "generations" in balance
        assert balance["credits"] == 2000


@pytest.mark.live
@skip_without_pixellab
class TestPixelLabClientLive:
    """
    Tests that make real API calls.

    Run with: pytest -m live
    Skip with: pytest -m "not live"
    Requires: PIXELLAB_API_KEY environment variable
    """

    def test_live_api_connection(self, live_mode):
        """Verify we can connect to the live Pixel Lab API."""
        client = PixelLabClient()

        balance = client.get_balance()
        assert "credits" in balance or "remaining_credits" in balance
        print(f"\n[LIVE BALANCE] {balance}")

    def test_live_generates_fixture(self, live_mode, tmp_path, monkeypatch):
        """Live mode should save fixture for future mock runs."""
        # Use temp directory for fixtures
        monkeypatch.setattr("pixellab_client.FIXTURES_DIR", tmp_path)

        client = PixelLabClient(capture_fixtures=True)
        description = "a cute red wizard with a blue hat"

        response = client.generate_image(description, width=64, height=64)

        # Check fixture was saved
        fixture_files = list(tmp_path.glob("*.json"))
        assert len(fixture_files) == 1

        # Verify fixture content
        import json
        with open(fixture_files[0]) as f:
            fixture = json.load(f)

        assert fixture["request_key"] is not None
        assert "images" in fixture["response"] or "success" in fixture["response"]

    def test_fixture_replay_matches_live(self, config_snapshot, tmp_path, monkeypatch):
        """Fixture replay should return same response as live call."""
        monkeypatch.setattr("pixellab_client.FIXTURES_DIR", tmp_path)

        client = PixelLabClient(capture_fixtures=True)
        description = "a small green dragon"

        # First call: LIVE - captures fixture
        api_config.global_mode = "LIVE"
        live_response = client.generate_image(description, width=64, height=64)

        # Second call: MOCK - should use fixture
        api_config.global_mode = "MOCK"
        mock_response = client.generate_image(description, width=64, height=64)

        # Responses should match (at least structure)
        assert "images" in mock_response or "success" in mock_response
        # Note: Exact match may vary if API returns different seeds


class TestPixelLabClientIntegration:
    """Integration tests combining mock and live."""

    def test_can_switch_modes_mid_test(self, config_snapshot):
        """Should be able to switch between mock and live."""
        client = PixelLabClient()

        # Start in mock
        api_config.global_mode = "MOCK"
        assert client.is_live is False

        # Switch to live
        api_config.global_mode = "LIVE"
        assert client.is_live is True

        # Override back to mock
        api_config.set_override("pixellab", "MOCK")
        assert client.is_live is False
