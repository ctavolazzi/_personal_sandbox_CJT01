"""
Anthropic API Client with Mock/Live Support

Automatically switches between live API calls and mock fixtures
based on the global configuration.

Usage:
    from anthropic_client import AnthropicClient

    client = AnthropicClient()
    response = client.generate("Hello, world!")

    # Response comes from live API or mock fixture based on config
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

from config import api_config

# Load .env file
load_dotenv()

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "anthropic"


class AnthropicClient:
    """
    Anthropic API client that respects mock/live configuration.

    When LIVE: Makes real API calls, optionally saves responses as fixtures
    When MOCK: Returns saved fixtures, raises if fixture not found
    """

    COMPONENT_NAME = "anthropic"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-5-sonnet-20241022",
        capture_fixtures: bool = True
    ):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self.capture_fixtures = capture_fixtures
        self._client = None

        # Ensure fixtures directory exists
        FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

    @property
    def is_live(self) -> bool:
        """Check if this client should use live API."""
        return api_config.is_live(self.COMPONENT_NAME)

    def _get_fixture_path(self, prompt: str) -> Path:
        """Generate a deterministic fixture path for a prompt."""
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:12]
        safe_prefix = "".join(c if c.isalnum() else "_" for c in prompt[:30])
        return FIXTURES_DIR / f"{safe_prefix}_{prompt_hash}.json"

    def _load_fixture(self, prompt: str) -> Optional[dict]:
        """Load a fixture if it exists."""
        path = self._get_fixture_path(prompt)
        if path.exists():
            with open(path) as f:
                return json.load(f)
        return None

    def _save_fixture(self, prompt: str, response: dict):
        """Save a response as a fixture."""
        path = self._get_fixture_path(prompt)
        fixture_data = {
            "prompt": prompt,
            "response": response,
            "captured_at": datetime.now().isoformat(),
            "model": self.model,
        }
        with open(path, "w") as f:
            json.dump(fixture_data, f, indent=2)
        print(f"[FIXTURE] Saved: {path.name}")

    def _get_live_client(self):
        """Lazy-load the Anthropic client."""
        if self._client is None:
            if not self.api_key:
                raise ValueError(
                    "ANTHROPIC_API_KEY not found. Set it in .env or pass to constructor."
                )
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "anthropic package not installed. "
                    "Run: pip install anthropic"
                )
        return self._client

    def generate(self, prompt: str, use_fixture_if_available: bool = True) -> dict:
        """
        Generate a response for the given prompt.

        Args:
            prompt: The input prompt
            use_fixture_if_available: If MOCK mode, use cached fixture if exists

        Returns:
            dict with 'text' key containing the response
        """
        mode = api_config.get_mode(self.COMPONENT_NAME)

        # MOCK MODE: Return fixture
        if mode == "MOCK":
            fixture = self._load_fixture(prompt)
            if fixture:
                print(f"[MOCK] Using fixture for prompt: {prompt[:50]}...")
                return fixture["response"]
            else:
                raise FileNotFoundError(
                    f"No fixture found for prompt: {prompt[:50]}...\n"
                    f"Run in LIVE mode first to capture fixtures, or create manually."
                )

        # LIVE MODE: Make real API call
        print(f"[LIVE] Calling Anthropic API ({self.model}) for prompt: {prompt[:50]}...")

        client = self._get_live_client()
        raw_response = client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )

        response = {
            "text": raw_response.content[0].text,
            "model": raw_response.model,
            "stop_reason": raw_response.stop_reason,
            "usage": {
                "input_tokens": raw_response.usage.input_tokens,
                "output_tokens": raw_response.usage.output_tokens,
            },
        }

        # Capture fixture for future mock runs
        if self.capture_fixtures:
            self._save_fixture(prompt, response)

        return response

    def generate_text(self, prompt: str) -> str:
        """Convenience method that returns just the text."""
        return self.generate(prompt)["text"]


# =============================================================================
# MODULE-LEVEL CONVENIENCE
# =============================================================================

_default_client: Optional[AnthropicClient] = None


def get_client() -> AnthropicClient:
    """Get or create the default client instance."""
    global _default_client
    if _default_client is None:
        _default_client = AnthropicClient()
    return _default_client


def generate(prompt: str) -> dict:
    """Generate using the default client."""
    return get_client().generate(prompt)


def generate_text(prompt: str) -> str:
    """Generate text using the default client."""
    return get_client().generate_text(prompt)
