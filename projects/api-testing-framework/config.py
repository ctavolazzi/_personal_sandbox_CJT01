"""
Mock/Live Configuration System

Single source of truth for controlling mock vs live API behavior.
Change ONE variable (global_mode) to toggle everything, or use
overrides dict for granular per-component control.

Usage:
    from config import api_config

    # Check mode for a component
    if api_config.get_mode("gemini") == "LIVE":
        # Make real API call
    else:
        # Use mock/fixture

    # Toggle everything to MOCK
    api_config.global_mode = "MOCK"

    # Override specific component to LIVE
    api_config.set_override("gemini", "LIVE")

    # Clear all overrides (revert to global)
    api_config.clear_overrides()
"""

from enum import Enum
from typing import Optional
import os


class Mode(str, Enum):
    LIVE = "LIVE"
    MOCK = "MOCK"


class MockConfig:
    """
    Configuration controller for mock/live API behavior.

    Priority: component override > global_mode

    Examples:
        # Everything MOCK except gemini
        config.global_mode = "MOCK"
        config.set_override("gemini", "LIVE")

        # Everything LIVE except two components
        config.global_mode = "LIVE"
        config.set_override("slow_service", "MOCK")
        config.set_override("expensive_api", "MOCK")
    """

    def __init__(
        self,
        global_mode: str = "MOCK",
        overrides: Optional[dict[str, str]] = None
    ):
        self._global_mode = Mode(global_mode)
        self._overrides: dict[str, Mode] = {}

        if overrides:
            for component, mode in overrides.items():
                self._overrides[component] = Mode(mode)

    @property
    def global_mode(self) -> str:
        """Get the global mode (LIVE or MOCK)."""
        return self._global_mode.value

    @global_mode.setter
    def global_mode(self, value: str):
        """Set the global mode. This is the ONE variable to change everything."""
        self._global_mode = Mode(value)

    def get_mode(self, component: str) -> str:
        """
        Get the effective mode for a component.

        Returns override if set, otherwise returns global_mode.
        """
        if component in self._overrides:
            return self._overrides[component].value
        return self._global_mode.value

    def set_override(self, component: str, mode: str):
        """Set a per-component override."""
        self._overrides[component] = Mode(mode)

    def remove_override(self, component: str):
        """Remove a specific component override."""
        self._overrides.pop(component, None)

    def clear_overrides(self):
        """Clear all overrides, reverting to pure global control."""
        self._overrides.clear()

    def is_live(self, component: str) -> bool:
        """Convenience method: returns True if component should use live API."""
        return self.get_mode(component) == Mode.LIVE.value

    def is_mock(self, component: str) -> bool:
        """Convenience method: returns True if component should use mock."""
        return self.get_mode(component) == Mode.MOCK.value

    @property
    def overrides(self) -> dict[str, str]:
        """Get current overrides as a plain dict."""
        return {k: v.value for k, v in self._overrides.items()}

    def __repr__(self) -> str:
        return f"MockConfig(global={self.global_mode}, overrides={self.overrides})"

    def status(self) -> str:
        """Return a human-readable status string."""
        lines = [f"Global Mode: {self.global_mode}"]
        if self._overrides:
            lines.append("Overrides:")
            for comp, mode in self._overrides.items():
                lines.append(f"  - {comp}: {mode.value}")
        else:
            lines.append("Overrides: None")
        return "\n".join(lines)


# =============================================================================
# GLOBAL INSTANCE - Import this in your code
# =============================================================================

# Default: Start in MOCK mode for safety (no accidental API calls)
# Override from environment if API_MODE is set
_default_mode = os.getenv("API_MODE", "MOCK")

api_config = MockConfig(global_mode=_default_mode)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def set_all_live():
    """Set everything to LIVE mode."""
    api_config.global_mode = "LIVE"
    api_config.clear_overrides()

def set_all_mock():
    """Set everything to MOCK mode."""
    api_config.global_mode = "MOCK"
    api_config.clear_overrides()

def mock_except(*components: str):
    """Set MOCK globally, but make specific components LIVE."""
    api_config.global_mode = "MOCK"
    api_config.clear_overrides()
    for comp in components:
        api_config.set_override(comp, "LIVE")

def live_except(*components: str):
    """Set LIVE globally, but make specific components MOCK."""
    api_config.global_mode = "LIVE"
    api_config.clear_overrides()
    for comp in components:
        api_config.set_override(comp, "MOCK")

