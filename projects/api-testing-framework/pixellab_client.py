"""
Pixel Lab API Client with Mock/Live Support

Automatically switches between live API calls and mock fixtures
based on the global configuration.

Usage:
    from pixellab_client import PixelLabClient

    client = PixelLabClient()
    response = client.generate_image(
        description="cute wizard",
        width=64,
        height=64
    )

    # Response comes from live API or mock fixture based on config
"""

import os
import json
import hashlib
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv

from config import api_config

# Load .env file
load_dotenv()

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "pixellab"
BASE_URL = "https://api.pixellab.ai/v2"


class PixelLabClient:
    """
    Pixel Lab API client that respects mock/live configuration.

    When LIVE: Makes real API calls, optionally saves responses as fixtures
    When MOCK: Returns saved fixtures, raises if fixture not found
    """

    COMPONENT_NAME = "pixellab"

    def __init__(
        self,
        api_key: Optional[str] = None,
        capture_fixtures: bool = True,
        base_url: str = BASE_URL
    ):
        self.api_key = api_key or os.getenv("PIXELLAB_API_KEY")
        self.capture_fixtures = capture_fixtures
        self.base_url = base_url

        # Ensure fixtures directory exists
        FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

    @property
    def is_live(self) -> bool:
        """Check if this client should use live API."""
        return api_config.is_live(self.COMPONENT_NAME)

    def _get_fixture_path(self, request_key: str) -> Path:
        """Generate a deterministic fixture path for a request."""
        request_hash = hashlib.md5(request_key.encode()).hexdigest()[:12]
        safe_prefix = "".join(c if c.isalnum() else "_" for c in request_key[:30])
        return FIXTURES_DIR / f"{safe_prefix}_{request_hash}.json"

    def _load_fixture(self, request_key: str) -> Optional[dict]:
        """Load a fixture if it exists."""
        path = self._get_fixture_path(request_key)
        if path.exists():
            with open(path) as f:
                return json.load(f)
        return None

    def _save_fixture(self, request_key: str, response: dict):
        """Save a response as a fixture."""
        path = self._get_fixture_path(request_key)
        fixture_data = {
            "request_key": request_key,
            "response": response,
            "captured_at": datetime.now().isoformat(),
            "api": "pixellab-v2",
        }
        with open(path, "w") as f:
            json.dump(fixture_data, f, indent=2)
        print(f"[FIXTURE] Saved: {path.name}")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> dict:
        """Make an HTTP request to the Pixel Lab API."""
        try:
            import requests
        except ImportError:
            raise ImportError(
                "requests package not installed. "
                "Run: pip install requests"
            )

        if not self.api_key:
            raise ValueError(
                "PIXELLAB_API_KEY not found. Set it in .env or pass to constructor."
            )

        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        return response.json()

    def _poll_background_job(self, job_id: str, max_wait: int = 300) -> dict:
        """Poll a background job until completion."""
        start_time = time.time()
        while time.time() - start_time < max_wait:
            response = self._make_request("GET", f"/background-jobs/{job_id}")

            status = response.get("data", {}).get("status")
            if status == "completed":
                return response.get("data", {})
            elif status == "failed":
                raise RuntimeError(f"Job {job_id} failed: {response.get('error')}")

            time.sleep(2)  # Poll every 2 seconds

        raise TimeoutError(f"Job {job_id} did not complete within {max_wait} seconds")

    def generate_image(
        self,
        description: str,
        width: int = 64,
        height: int = 64,
        seed: Optional[int] = None,
        no_background: bool = False,
        reference_images: Optional[list] = None,
        style_image: Optional[dict] = None,
        style_options: Optional[dict] = None
    ) -> dict:
        """
        Generate pixel art image from text description.

        Args:
            description: Text description of the image to generate
            width: Image width in pixels (32, 64, 128, or 256)
            height: Image height in pixels (32, 64, 128, or 256)
            seed: Seed for reproducible generation
            no_background: Remove background from generated images
            reference_images: Optional reference images for subject guidance (up to 4)
            style_image: Optional style image for pixel size and style reference
            style_options: Options for what to copy from the style image

        Returns:
            dict with 'images' key containing list of base64-encoded images
        """
        mode = api_config.get_mode(self.COMPONENT_NAME)

        # Create request key for fixture lookup
        request_data = {
            "description": description,
            "width": width,
            "height": height,
            "seed": seed,
            "no_background": no_background,
        }
        request_key = json.dumps(request_data, sort_keys=True)

        # MOCK MODE: Return fixture
        if mode == "MOCK":
            fixture = self._load_fixture(request_key)
            if fixture:
                print(f"[MOCK] Using fixture for: {description[:50]}...")
                return fixture["response"]
            else:
                raise FileNotFoundError(
                    f"No fixture found for description: {description[:50]}...\n"
                    f"Run in LIVE mode first to capture fixtures, or create manually."
                )

        # LIVE MODE: Make real API call
        print(f"[LIVE] Calling Pixel Lab API for: {description[:50]}...")

        payload = {
            "description": description,
            "image_size": {
                "width": width,
                "height": height
            }
        }

        if seed is not None:
            payload["seed"] = seed
        if no_background:
            payload["no_background"] = True
        if reference_images:
            payload["reference_images"] = reference_images
        if style_image:
            payload["style_image"] = style_image
        if style_options:
            payload["style_options"] = style_options

        response = self._make_request("POST", "/generate-image-v2", data=payload)

        # Extract response data
        result = {
            "images": response.get("data", {}).get("images", []),
            "usage": response.get("usage", {}),
            "success": response.get("success", False)
        }

        # Capture fixture for future mock runs
        if self.capture_fixtures:
            self._save_fixture(request_key, result)

        return result

    def create_character_4_directions(
        self,
        description: str,
        width: int = 64,
        height: int = 64,
        **kwargs
    ) -> dict:
        """
        Create character with 4 directional views (south, west, east, north).

        Args:
            description: Description of the character or object to generate
            width: Canvas width in pixels (32-400)
            height: Canvas height in pixels (32-400)
            **kwargs: Additional parameters (text_guidance_scale, outline, shading, etc.)

        Returns:
            dict with character_id and background_job_id
        """
        mode = api_config.get_mode(self.COMPONENT_NAME)

        request_data = {
            "description": description,
            "width": width,
            "height": height,
            **kwargs
        }
        request_key = json.dumps(request_data, sort_keys=True)

        if mode == "MOCK":
            fixture = self._load_fixture(request_key)
            if fixture:
                print(f"[MOCK] Using fixture for character: {description[:50]}...")
                return fixture["response"]
            else:
                raise FileNotFoundError(
                    f"No fixture found for character: {description[:50]}...\n"
                    f"Run in LIVE mode first to capture fixtures."
                )

        print(f"[LIVE] Creating 4-direction character: {description[:50]}...")

        payload = {
            "description": description,
            "image_size": {"width": width, "height": height},
            **kwargs
        }

        response = self._make_request(
            "POST",
            "/create-character-with-4-directions",
            data=payload
        )

        result = {
            "character_id": response.get("data", {}).get("character_id"),
            "background_job_id": response.get("data", {}).get("background_job_id"),
            "usage": response.get("usage", {}),
            "success": response.get("success", False)
        }

        if self.capture_fixtures:
            self._save_fixture(request_key, result)

        return result

    def get_balance(self) -> dict:
        """Get account balance and usage information."""
        mode = api_config.get_mode(self.COMPONENT_NAME)

        if mode == "MOCK":
            # Return mock balance data
            return {
                "credits": 2000,
                "generations": 2000,
                "remaining_credits": 1500,
                "remaining_generations": 1500
            }

        response = self._make_request("GET", "/balance")
        return response.get("data", {})


# =============================================================================
# MODULE-LEVEL CONVENIENCE
# =============================================================================

_default_client: Optional[PixelLabClient] = None


def get_client() -> PixelLabClient:
    """Get or create the default client instance."""
    global _default_client
    if _default_client is None:
        _default_client = PixelLabClient()
    return _default_client


def generate_image(description: str, width: int = 64, height: int = 64, **kwargs) -> dict:
    """Generate image using the default client."""
    return get_client().generate_image(description, width, height, **kwargs)
