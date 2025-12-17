"""
MapForge - High-level API for pixel art map generation

Combines TilesetManager, MapGenerator, and MapAssembler into
a simple, unified interface.

Usage:
    from mapforge import MapForge

    mf = MapForge()

    # Workflow 1: Tileset-based
    tileset = mf.create_tileset_chain(["ocean water", "sandy beach", "grass"])
    map_img = mf.generate_map_from_tileset(tileset, width=10, height=10)
    mf.save_map(map_img, "beach_map.png")

    # Workflow 2: Direct generation
    region = mf.generate_region("stairs in a cave", init_image="cave_sketch.png")
    region = mf.expand_region(region, direction="right", description="treasure chest area")
    mf.save_map(region.image, "cave_map.png")
"""

import os
from pathlib import Path
from typing import Optional, Union

from PIL import Image

from .tileset_manager import TilesetManager, TilesetResult
from .map_generator import MapGenerator, MapRegion
from .map_assembler import MapAssembler, WangTileset

ASSETS_DIR = Path(__file__).parent / "assets"


class MapForge:
    """
    High-level API for generating pixel art maps.

    Provides two main workflows:
    1. Tileset-based: Generate Wang tilesets and assemble maps
    2. Direct generation: Generate map regions with AI

    Example - Tileset workflow:
        mf = MapForge()
        results = mf.create_tileset_chain(["ocean", "beach", "grass"])
        map_img = mf.generate_map_from_tileset(results[0], width=10, height=10)
        mf.save_map(map_img, "my_map.png")

    Example - Direct generation:
        mf = MapForge()
        region = mf.generate_region("dungeon floor with torches")
        region = mf.expand_region(region, "right", "treasure room")
        mf.save_map(region.image, "dungeon.png")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        assets_dir: Optional[Path] = None
    ):
        """
        Initialize MapForge.

        Args:
            api_key: PixelLab API key (defaults to PIXELLAB_API_KEY env var)
            assets_dir: Directory for storing assets
        """
        self.api_key = api_key or os.getenv("PIXELLAB_API_KEY")
        self.assets_dir = assets_dir or ASSETS_DIR
        self.assets_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.tileset_manager = TilesetManager(
            api_key=self.api_key,
            assets_dir=self.assets_dir / "tilesets"
        )
        self.map_generator = MapGenerator(
            api_key=self.api_key,
            assets_dir=self.assets_dir
        )
        self.map_assembler = MapAssembler(
            assets_dir=self.assets_dir
        )

    # =========================================================================
    # Tileset Workflow
    # =========================================================================

    def create_tileset(
        self,
        lower_terrain: str,
        upper_terrain: str,
        transition_size: float = 0.0,
        tile_size: int = 16,
        wait: bool = True,
        save: bool = True,
        **kwargs
    ) -> TilesetResult:
        """
        Create a single Wang tileset with two terrain types.

        Args:
            lower_terrain: Lower terrain description (e.g., "ocean water")
            upper_terrain: Upper terrain description (e.g., "sandy beach")
            transition_size: Transition size (0.0, 0.25, 0.5, or 1.0)
            tile_size: Tile size in pixels (16 or 32)
            wait: Wait for generation to complete
            save: Save tileset images locally
            **kwargs: Additional API parameters

        Returns:
            TilesetResult with tileset data
        """
        result = self.tileset_manager.create_tileset(
            lower_terrain,
            upper_terrain,
            transition_size=transition_size,
            tile_size=tile_size,
            **kwargs
        )

        if wait:
            result = self.tileset_manager.wait_for_completion(result.tileset_id)

            if save:
                self.tileset_manager.save_tileset_images(result.tileset_id)

        return result

    def create_tileset_chain(
        self,
        terrains: list[str],
        transition_size: float = 0.0,
        tile_size: int = 16,
        save: bool = True,
        **kwargs
    ) -> list[TilesetResult]:
        """
        Create a chain of connected tilesets.

        Example: ["ocean", "beach", "grass"] creates tilesets for
        ocean→beach and beach→grass with consistent visuals.

        Args:
            terrains: List of terrain descriptions (at least 2)
            transition_size: Transition size for all tilesets
            tile_size: Tile size in pixels
            save: Save tileset images locally
            **kwargs: Additional API parameters

        Returns:
            List of TilesetResult objects
        """
        results = self.tileset_manager.create_terrain_chain(
            terrains,
            transition_size=transition_size,
            tile_size=tile_size,
            wait=True,
            **kwargs
        )

        if save:
            for result in results:
                self.tileset_manager.save_tileset_images(result.tileset_id)

        return results

    def generate_map_from_tileset(
        self,
        tileset: Union[TilesetResult, str, Path],
        width: int = 10,
        height: int = 10,
        pattern: str = "random"
    ) -> Image.Image:
        """
        Generate a map from a tileset.

        Args:
            tileset: TilesetResult, tileset ID, or path to tileset directory
            width: Map width in tiles
            height: Map height in tiles
            pattern: "random", "gradient", "checkerboard", "solid_lower", "solid_upper"

        Returns:
            Map as PIL Image
        """
        if isinstance(tileset, TilesetResult):
            tileset_dir = tileset.local_path
            if not tileset_dir:
                # Save tileset first
                self.tileset_manager.save_tileset_images(tileset.tileset_id)
                tileset_dir = self.assets_dir / "tilesets" / tileset.tileset_id[:8]
        elif isinstance(tileset, str):
            # Could be ID or path
            tileset_path = Path(tileset)
            if tileset_path.exists():
                tileset_dir = tileset_path
            else:
                tileset_dir = self.assets_dir / "tilesets" / tileset[:8]
        else:
            tileset_dir = tileset

        return self.map_assembler.create_simple_map(
            tileset_dir,
            width=width,
            height=height,
            pattern=pattern
        )

    def generate_map_from_terrain(
        self,
        tileset: Union[TilesetResult, str, Path],
        terrain_map: list[list[int]]
    ) -> Image.Image:
        """
        Generate a map using a custom terrain layout.

        The terrain_map defines terrain type at each vertex.
        Values are 0 (lower terrain) or 1 (upper terrain).

        Args:
            tileset: TilesetResult, tileset ID, or path to tileset directory
            terrain_map: 2D list of terrain values at vertices

        Returns:
            Map as PIL Image
        """
        if isinstance(tileset, TilesetResult):
            tileset_dir = tileset.local_path
            if not tileset_dir:
                self.tileset_manager.save_tileset_images(tileset.tileset_id)
                tileset_dir = self.assets_dir / "tilesets" / tileset.tileset_id[:8]
        elif isinstance(tileset, str):
            tileset_path = Path(tileset)
            if tileset_path.exists():
                tileset_dir = tileset_path
            else:
                tileset_dir = self.assets_dir / "tilesets" / tileset[:8]
        else:
            tileset_dir = tileset

        return self.map_assembler.create_map_from_terrain(tileset_dir, terrain_map)

    # =========================================================================
    # Direct Generation Workflow
    # =========================================================================

    def generate_region(
        self,
        description: str,
        width: int = 64,
        height: int = 64,
        init_image: Optional[Union[str, Path, Image.Image]] = None,
        **kwargs
    ) -> MapRegion:
        """
        Generate a map region directly from a description.

        Args:
            description: Text description of the region
            width: Region width in pixels
            height: Region height in pixels
            init_image: Optional starting image/sketch
            **kwargs: Additional API parameters

        Returns:
            MapRegion with generated image
        """
        return self.map_generator.create_initial_region(
            description=description,
            width=width,
            height=height,
            init_image=init_image,
            **kwargs
        )

    def expand_region(
        self,
        region: MapRegion,
        direction: str,
        description: str,
        overlap: int = 16,
        **kwargs
    ) -> MapRegion:
        """
        Expand an existing region in a direction.

        Args:
            region: Region to expand from
            direction: "up", "down", "left", or "right"
            description: Description for the new area
            overlap: Pixels of overlap for context
            **kwargs: Additional API parameters

        Returns:
            New MapRegion
        """
        return self.map_generator.expand_region(
            region,
            direction=direction,
            description=description,
            overlap=overlap,
            **kwargs
        )

    def create_map_object(
        self,
        description: str,
        width: int = 64,
        height: int = 64,
        **kwargs
    ) -> MapRegion:
        """
        Create a map object with transparent background.

        Args:
            description: Object description
            width: Object width in pixels
            height: Object height in pixels
            **kwargs: Additional API parameters

        Returns:
            MapRegion with transparent object
        """
        return self.map_generator.create_map_object(
            description=description,
            width=width,
            height=height,
            **kwargs
        )

    def stitch_regions(
        self,
        regions: list[MapRegion]
    ) -> Image.Image:
        """
        Stitch multiple regions into a single map.

        Args:
            regions: List of MapRegion objects with x, y positions

        Returns:
            Combined map as PIL Image
        """
        region_tuples = [(r.image, r.x, r.y) for r in regions]
        return self.map_assembler.stitch_regions(region_tuples)

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def save_map(
        self,
        map_image: Union[Image.Image, MapRegion],
        output_path: Union[str, Path],
        scale: int = 1
    ) -> Path:
        """
        Save a map image to file.

        Args:
            map_image: Map image or MapRegion
            output_path: Output file path
            scale: Scale factor (1 = original, 2 = 2x, etc.)

        Returns:
            Path to saved file
        """
        if isinstance(map_image, MapRegion):
            map_image = map_image.image

        return self.map_assembler.export_png(map_image, output_path, scale=scale)

    def list_tilesets(self) -> list[dict]:
        """List all locally saved tilesets."""
        return self.tileset_manager.list_local_tilesets()

    def get_tileset_dir(self, tileset_id: str) -> Path:
        """Get the directory path for a tileset."""
        return self.assets_dir / "tilesets" / tileset_id[:8]


# =============================================================================
# Module-level convenience
# =============================================================================

_default_forge: Optional[MapForge] = None


def get_forge() -> MapForge:
    """Get or create the default MapForge instance."""
    global _default_forge
    if _default_forge is None:
        _default_forge = MapForge()
    return _default_forge


def create_tileset(lower: str, upper: str, **kwargs) -> TilesetResult:
    """Create a tileset using the default MapForge instance."""
    return get_forge().create_tileset(lower, upper, **kwargs)


def generate_map(tileset, width: int = 10, height: int = 10, **kwargs) -> Image.Image:
    """Generate a map using the default MapForge instance."""
    return get_forge().generate_map_from_tileset(tileset, width, height, **kwargs)
