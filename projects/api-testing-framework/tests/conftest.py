"""
Pytest Configuration and Fixtures

Provides fixtures for controlling mock/live behavior in tests.
"""

import os
import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import api_config, MockConfig


# =============================================================================
# API KEY AVAILABILITY CHECKS
# =============================================================================

HAS_ANTHROPIC_KEY = bool(os.getenv("ANTHROPIC_API_KEY"))
HAS_OPENAI_KEY = bool(os.getenv("OPENAI_API_KEY"))
HAS_GOOGLE_KEY = bool(os.getenv("GOOGLE_API_KEY"))

# Skip decorators for live tests
skip_without_anthropic = pytest.mark.skipif(
    not HAS_ANTHROPIC_KEY,
    reason="ANTHROPIC_API_KEY not set"
)
skip_without_openai = pytest.mark.skipif(
    not HAS_OPENAI_KEY,
    reason="OPENAI_API_KEY not set"
)
skip_without_google = pytest.mark.skipif(
    not HAS_GOOGLE_KEY,
    reason="GOOGLE_API_KEY not set"
)


@pytest.fixture
def mock_mode():
    """
    Fixture that sets MOCK mode for the test, restores after.

    Usage:
        def test_something(mock_mode):
            # api_config is now in MOCK mode
            ...
    """
    original_mode = api_config.global_mode
    original_overrides = api_config.overrides.copy()

    api_config.global_mode = "MOCK"
    api_config.clear_overrides()

    yield api_config

    # Restore
    api_config.global_mode = original_mode
    api_config.clear_overrides()
    for comp, mode in original_overrides.items():
        api_config.set_override(comp, mode)


@pytest.fixture
def live_mode():
    """
    Fixture that sets LIVE mode for the test, restores after.

    Usage:
        def test_real_api(live_mode):
            # api_config is now in LIVE mode
            ...
    """
    original_mode = api_config.global_mode
    original_overrides = api_config.overrides.copy()

    api_config.global_mode = "LIVE"
    api_config.clear_overrides()

    yield api_config

    # Restore
    api_config.global_mode = original_mode
    api_config.clear_overrides()
    for comp, mode in original_overrides.items():
        api_config.set_override(comp, mode)


@pytest.fixture
def fresh_config():
    """
    Fixture that provides a fresh MockConfig instance for the test.
    Does not affect the global api_config.

    Usage:
        def test_config_behavior(fresh_config):
            fresh_config.global_mode = "LIVE"
            assert fresh_config.get_mode("test") == "LIVE"
    """
    return MockConfig(global_mode="MOCK")


@pytest.fixture
def config_snapshot():
    """
    Fixture that saves and restores config state around a test.
    Use when you need to modify api_config but want automatic restoration.

    Usage:
        def test_modifies_config(config_snapshot):
            api_config.global_mode = "LIVE"
            api_config.set_override("something", "MOCK")
            # ... test ...
        # Config automatically restored after test
    """
    original_mode = api_config.global_mode
    original_overrides = api_config.overrides.copy()

    yield api_config

    # Restore
    api_config.global_mode = original_mode
    api_config.clear_overrides()
    for comp, mode in original_overrides.items():
        api_config.set_override(comp, mode)


# =============================================================================
# MARKERS
# =============================================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "live: mark test as requiring live API access"
    )
    config.addinivalue_line(
        "markers", "mock: mark test as using mock mode (no API calls)"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


# =============================================================================
# HELPFUL TEST COMMANDS
# =============================================================================
# Run only mock tests (always pass, no API keys needed):
#   pytest -m mock
#
# Run only live tests (requires API keys):
#   pytest -m live
#
# Run everything except live tests:
#   pytest -m "not live"
#
# Run tests for a specific provider:
#   pytest tests/test_gemini.py
#   pytest tests/test_anthropic.py
#   pytest tests/test_openai.py

