"""
Tileset Manager - Generate and manage Wang tilesets via PixelLab API

Wraps PixelLab's create_topdown_tileset API to:
- Generate connected Wang tilesets (ocean -> beach -> grass -> stone)
- Chain tilesets using lower_base_tile_id / upper_base_tile_id
- Store and retrieve tilesets locally
- Poll background jobs until completion
"""

import os
import json
import time
import base64
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()

ASSETS_DIR = Path(__file__).parent / "assets" / "tilesets"
BASE_URL = "https://api.pixellab.ai/v2"


@dataclass
class TilesetConfig:
    """Configuration for a tileset."""
    lower_description: str
    upper_description: str
    transition_size: float = 0.0
    transition_description: Optional[str] = None
    tile_size: dict = field(default_factory=lambda: {"width": 16, "height": 16})
    outline: Optional[str] = None
    shading: Optional[str] = None
    detail: Optional[str] = None
    view: str = "high top-down"
    tile_strength: float = 1.0
    lower_base_tile_id: Optional[str] = None
    upper_base_tile_id: Optional[str] = None
    tileset_adherence: int = 100
    tileset_adherence_freedom: int = 500
    text_guidance_scale: int = 8


@dataclass
class TilesetResult:
    """Result from tileset generation."""
    tileset_id: str
    status: str
    lower_base_tile_id: Optional[str] = None
    upper_base_tile_id: Optional[str] = None
    tiles: list = field(default_factory=list)
    png_url: Optional[str] = None
    metadata_url: Optional[str] = None
    created_at: Optional[str] = None
    local_path: Optional[Path] = None

    def to_dict(self) -> dict:
        result = asdict(self)
        if self.local_path:
            result["local_path"] = str(self.local_path)
        return result


class TilesetManager:
    """
    Manages Wang tileset generation and storage.

    Usage:
        manager = TilesetManager()

        # Create a single tileset
        result = manager.create_tileset("ocean water", "sandy beach")
        manager.wait_for_completion(result.tileset_id)
        paths = manager.save_tileset_images(result.tileset_id)

        # Create a terrain chain
        results = manager.create_terrain_chain(["ocean water", "sandy beach", "grass"])
    """

    COMPONENT_NAME = "pixellab"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = BASE_URL,
        assets_dir: Optional[Path] = None
    ):
        self.api_key = api_key or os.getenv("PIXELLAB_API_KEY")
        self.base_url = base_url
        self.assets_dir = assets_dir or ASSETS_DIR
        self.assets_dir.mkdir(parents=True, exist_ok=True)

        # Cache for tileset results
        self._cache: dict[str, TilesetResult] = {}

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None,
        params: Optional[dict] = None
    ) -> dict:
        """Make an HTTP request to the PixelLab API."""
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

    def create_tileset(
        self,
        lower_description: str,
        upper_description: str,
        transition_size: float = 0.0,
        transition_description: Optional[str] = None,
        tile_size: int = 16,
        outline: Optional[str] = None,
        shading: Optional[str] = None,
        detail: Optional[str] = None,
        view: str = "high top-down",
        lower_base_tile_id: Optional[str] = None,
        upper_base_tile_id: Optional[str] = None,
        **kwargs
    ) -> TilesetResult:
        """
        Create a Wang tileset with two terrain types.

        Args:
            lower_description: Lower terrain (e.g., "ocean water")
            upper_description: Upper terrain (e.g., "sandy beach")
            transition_size: Size of transition (0.0, 0.25, 0.5, or 1.0)
            transition_description: Blending description if transition_size > 0
            tile_size: Tile dimensions (16 or 32)
            outline: "single color outline", "selective outline", or "lineless"
            shading: "flat shading" to "highly detailed shading"
            detail: "low detail", "medium detail", or "highly detailed"
            view: "low top-down" or "high top-down"
            lower_base_tile_id: ID of existing tile for lower terrain reference
            upper_base_tile_id: ID of existing tile for upper terrain reference

        Returns:
            TilesetResult with tileset_id (async, use wait_for_completion)
        """
        print(f"[LIVE] Creating tileset: {lower_description} → {upper_description}")

        payload = {
            "lower_description": lower_description,
            "upper_description": upper_description,
            "transition_size": transition_size,
            "tile_size": {"width": tile_size, "height": tile_size},
            "view": view,
        }

        if transition_size > 0 and transition_description:
            payload["transition_description"] = transition_description
        if outline:
            payload["outline"] = outline
        if shading:
            payload["shading"] = shading
        if detail:
            payload["detail"] = detail
        if lower_base_tile_id:
            payload["lower_base_tile_id"] = lower_base_tile_id
        if upper_base_tile_id:
            payload["upper_base_tile_id"] = upper_base_tile_id

        payload.update(kwargs)

        response = self._make_request("POST", "/create-topdown-tileset", data=payload)

        data = response.get("data", {})
        result = TilesetResult(
            tileset_id=data.get("tileset_id", ""),
            status="pending",
            created_at=datetime.now().isoformat()
        )

        self._cache[result.tileset_id] = result
        return result

    def get_tileset(self, tileset_id: str) -> TilesetResult:
        """
        Get tileset status and data.

        Args:
            tileset_id: The tileset UUID

        Returns:
            TilesetResult with current status and data
        """
        response = self._make_request("GET", f"/topdown-tilesets/{tileset_id}")
        data = response.get("data", {})

        result = TilesetResult(
            tileset_id=tileset_id,
            status=data.get("status", "unknown"),
            lower_base_tile_id=data.get("lower_base_tile_id"),
            upper_base_tile_id=data.get("upper_base_tile_id"),
            tiles=data.get("tiles", []),
            png_url=data.get("png_url"),
            metadata_url=data.get("metadata_url"),
        )

        self._cache[tileset_id] = result
        return result

    def wait_for_completion(
        self,
        tileset_id: str,
        max_wait: int = 300,
        poll_interval: int = 5
    ) -> TilesetResult:
        """
        Poll until tileset generation completes.

        Args:
            tileset_id: The tileset UUID
            max_wait: Maximum seconds to wait
            poll_interval: Seconds between polls

        Returns:
            TilesetResult with completed data

        Raises:
            TimeoutError: If generation doesn't complete in time
            RuntimeError: If generation fails
        """
        print(f"[WAIT] Waiting for tileset {tileset_id[:8]}...")
        start_time = time.time()

        while time.time() - start_time < max_wait:
            result = self.get_tileset(tileset_id)

            if result.status == "completed":
                print(f"[DONE] Tileset {tileset_id[:8]} completed")
                return result
            elif result.status == "failed":
                raise RuntimeError(f"Tileset generation failed: {tileset_id}")

            elapsed = int(time.time() - start_time)
            print(f"[WAIT] Status: {result.status} ({elapsed}s elapsed)")
            time.sleep(poll_interval)

        raise TimeoutError(
            f"Tileset {tileset_id} did not complete within {max_wait} seconds"
        )

    def save_tileset_images(
        self,
        tileset_id: str,
        output_dir: Optional[Path] = None
    ) -> list[Path]:
        """
        Download and save tileset images locally.

        Args:
            tileset_id: The tileset UUID
            output_dir: Directory to save images (defaults to assets/tilesets/{id})

        Returns:
            List of saved file paths
        """
        result = self.get_tileset(tileset_id)

        if result.status != "completed":
            raise ValueError(f"Tileset not completed: {result.status}")

        output_dir = output_dir or self.assets_dir / tileset_id[:8]
        output_dir.mkdir(parents=True, exist_ok=True)

        saved_paths = []

        # Save main tileset PNG if available
        if result.png_url:
            png_path = output_dir / "tileset.png"
            response = requests.get(result.png_url)
            response.raise_for_status()
            png_path.write_bytes(response.content)
            saved_paths.append(png_path)
            print(f"[SAVE] Tileset PNG: {png_path}")

        # Save individual tiles
        for i, tile in enumerate(result.tiles):
            if isinstance(tile, dict) and "image" in tile:
                tile_path = output_dir / f"tile_{i:02d}.png"
                image_data = base64.b64decode(tile["image"])
                tile_path.write_bytes(image_data)
                saved_paths.append(tile_path)

        # Save metadata
        metadata_path = output_dir / "metadata.json"
        metadata = {
            "tileset_id": tileset_id,
            "lower_base_tile_id": result.lower_base_tile_id,
            "upper_base_tile_id": result.upper_base_tile_id,
            "tile_count": len(result.tiles),
            "saved_at": datetime.now().isoformat()
        }
        metadata_path.write_text(json.dumps(metadata, indent=2))
        saved_paths.append(metadata_path)

        result.local_path = output_dir
        print(f"[SAVE] Saved {len(saved_paths)} files to {output_dir}")

        return saved_paths

    def create_terrain_chain(
        self,
        terrains: list[str],
        transition_size: float = 0.0,
        tile_size: int = 16,
        wait: bool = True,
        **kwargs
    ) -> list[TilesetResult]:
        """
        Create a chain of connected tilesets.

        Example: ["ocean water", "sandy beach", "grass"] creates:
        - ocean → beach tileset
        - beach → grass tileset (using beach base tile from first)

        Args:
            terrains: List of terrain descriptions (at least 2)
            transition_size: Size of terrain transitions
            tile_size: Tile dimensions
            wait: Wait for each tileset to complete before creating next
            **kwargs: Additional parameters for all tilesets

        Returns:
            List of TilesetResult objects
        """
        if len(terrains) < 2:
            raise ValueError("Need at least 2 terrains for a chain")

        results = []
        upper_base_tile_id = None

        for i in range(len(terrains) - 1):
            lower = terrains[i]
            upper = terrains[i + 1]

            # Use previous upper as current lower reference
            lower_base = upper_base_tile_id

            print(f"\n[CHAIN] Creating tileset {i + 1}/{len(terrains) - 1}: {lower} → {upper}")

            result = self.create_tileset(
                lower_description=lower,
                upper_description=upper,
                transition_size=transition_size,
                tile_size=tile_size,
                lower_base_tile_id=lower_base,
                **kwargs
            )

            if wait:
                result = self.wait_for_completion(result.tileset_id)
                # Get the upper base tile ID for the next tileset
                upper_base_tile_id = result.upper_base_tile_id

            results.append(result)

        return results

    def list_local_tilesets(self) -> list[dict]:
        """List all locally saved tilesets."""
        tilesets = []

        for tileset_dir in self.assets_dir.iterdir():
            if tileset_dir.is_dir():
                metadata_path = tileset_dir / "metadata.json"
                if metadata_path.exists():
                    metadata = json.loads(metadata_path.read_text())
                    metadata["local_path"] = str(tileset_dir)
                    tilesets.append(metadata)

        return tilesets

    def load_tileset_metadata(self, tileset_dir: Path) -> dict:
        """Load metadata for a locally saved tileset."""
        metadata_path = tileset_dir / "metadata.json"
        if not metadata_path.exists():
            raise FileNotFoundError(f"No metadata found at {metadata_path}")
        return json.loads(metadata_path.read_text())
