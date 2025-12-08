"""
Tests for the MockConfig system.

These tests verify the mock/live toggle system works correctly.
"""

import pytest
from config import MockConfig, api_config, mock_except, live_except


class TestMockConfig:
    """Tests for MockConfig class."""

    def test_default_mode_is_mock(self, fresh_config):
        """Default mode should be MOCK for safety."""
        assert fresh_config.global_mode == "MOCK"

    def test_global_mode_affects_all_components(self, fresh_config):
        """When no overrides, all components follow global mode."""
        fresh_config.global_mode = "LIVE"
        assert fresh_config.get_mode("gemini") == "LIVE"
        assert fresh_config.get_mode("openai") == "LIVE"
        assert fresh_config.get_mode("anything") == "LIVE"

        fresh_config.global_mode = "MOCK"
        assert fresh_config.get_mode("gemini") == "MOCK"
        assert fresh_config.get_mode("openai") == "MOCK"

    def test_override_takes_precedence(self, fresh_config):
        """Component override should override global mode."""
        fresh_config.global_mode = "MOCK"
        fresh_config.set_override("gemini", "LIVE")

        assert fresh_config.get_mode("gemini") == "LIVE"  # Override
        assert fresh_config.get_mode("openai") == "MOCK"  # Global

    def test_multiple_overrides(self, fresh_config):
        """Multiple overrides should work independently."""
        fresh_config.global_mode = "LIVE"
        fresh_config.set_override("slow_api", "MOCK")
        fresh_config.set_override("expensive_api", "MOCK")

        assert fresh_config.get_mode("fast_api") == "LIVE"      # Global
        assert fresh_config.get_mode("slow_api") == "MOCK"      # Override
        assert fresh_config.get_mode("expensive_api") == "MOCK" # Override

    def test_remove_override(self, fresh_config):
        """Removing override should revert to global."""
        fresh_config.global_mode = "MOCK"
        fresh_config.set_override("gemini", "LIVE")
        assert fresh_config.get_mode("gemini") == "LIVE"

        fresh_config.remove_override("gemini")
        assert fresh_config.get_mode("gemini") == "MOCK"

    def test_clear_overrides(self, fresh_config):
        """Clear should remove all overrides."""
        fresh_config.set_override("a", "LIVE")
        fresh_config.set_override("b", "LIVE")
        fresh_config.set_override("c", "LIVE")

        fresh_config.clear_overrides()

        assert fresh_config.overrides == {}
        assert fresh_config.get_mode("a") == "MOCK"

    def test_is_live_helper(self, fresh_config):
        """is_live() should return boolean."""
        fresh_config.global_mode = "LIVE"
        assert fresh_config.is_live("gemini") is True
        assert fresh_config.is_mock("gemini") is False

        fresh_config.global_mode = "MOCK"
        assert fresh_config.is_live("gemini") is False
        assert fresh_config.is_mock("gemini") is True

    def test_invalid_mode_raises(self, fresh_config):
        """Invalid mode should raise ValueError."""
        with pytest.raises(ValueError):
            fresh_config.global_mode = "INVALID"

        with pytest.raises(ValueError):
            fresh_config.set_override("gemini", "INVALID")

    def test_repr(self, fresh_config):
        """repr should be informative."""
        fresh_config.set_override("gemini", "LIVE")
        r = repr(fresh_config)
        assert "MOCK" in r
        assert "gemini" in r
        assert "LIVE" in r


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_mock_except(self, config_snapshot):
        """mock_except should set global MOCK with specific LIVE overrides."""
        mock_except("gemini", "fast_api")

        assert api_config.global_mode == "MOCK"
        assert api_config.get_mode("gemini") == "LIVE"
        assert api_config.get_mode("fast_api") == "LIVE"
        assert api_config.get_mode("other") == "MOCK"

    def test_live_except(self, config_snapshot):
        """live_except should set global LIVE with specific MOCK overrides."""
        live_except("slow_api", "expensive_api")

        assert api_config.global_mode == "LIVE"
        assert api_config.get_mode("slow_api") == "MOCK"
        assert api_config.get_mode("expensive_api") == "MOCK"
        assert api_config.get_mode("other") == "LIVE"


class TestScenarios:
    """Real-world usage scenarios."""

    def test_scenario_all_mock(self, fresh_config):
        """Scenario: Run all tests with mocked APIs."""
        fresh_config.global_mode = "MOCK"

        # All components should be mocked
        for comp in ["gemini", "openai", "database", "cache"]:
            assert fresh_config.is_mock(comp)

    def test_scenario_integration_test_one_live(self, fresh_config):
        """Scenario: Integration test with one live component."""
        fresh_config.global_mode = "MOCK"
        fresh_config.set_override("gemini", "LIVE")

        # Only gemini is live
        assert fresh_config.is_live("gemini")
        assert fresh_config.is_mock("openai")
        assert fresh_config.is_mock("database")

    def test_scenario_production_two_mocked(self, fresh_config):
        """Scenario: Production-like with two expensive APIs mocked."""
        fresh_config.global_mode = "LIVE"
        fresh_config.set_override("billing_api", "MOCK")
        fresh_config.set_override("analytics_api", "MOCK")

        # Most things live, two mocked
        assert fresh_config.is_live("gemini")
        assert fresh_config.is_live("database")
        assert fresh_config.is_mock("billing_api")
        assert fresh_config.is_mock("analytics_api")

