"""
Map Assembler - Compose tiles into complete maps

Combines generated tiles/regions into complete maps:
- Stitch tiles based on Wang tileset rules
- Composite map regions with proper overlap handling
- Export final PNG at various scales
"""

import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Union

from PIL import Image

ASSETS_DIR = Path(__file__).parent / "assets"


@dataclass
class TileInfo:
    """Information about a tile in a tileset."""
    index: int
    image: Image.Image
    corners: tuple[int, int, int, int]  # TL, TR, BL, BR (0=lower, 1=upper)


class WangTileset:
    """
    Wang tileset for autotiling.

    Wang tiles use corner-based indexing where each corner can be
    either lower (0) or upper (1) terrain. This gives 2^4 = 16 tiles.

    Corner layout:
        TL -- TR
        |      |
        BL -- BR
    """

    def __init__(self, tileset_dir: Path):
        self.tileset_dir = tileset_dir
        self.tiles: list[TileInfo] = []
        self.tile_size = 16
        self._load_tileset()

    def _load_tileset(self):
        """Load tileset images and metadata."""
        metadata_path = self.tileset_dir / "metadata.json"

        if metadata_path.exists():
            metadata = json.loads(metadata_path.read_text())
            self.tileset_id = metadata.get("tileset_id")
        else:
            self.tileset_id = self.tileset_dir.name

        # Load individual tile images
        tile_files = sorted(self.tileset_dir.glob("tile_*.png"))

        for i, tile_path in enumerate(tile_files):
            img = Image.open(tile_path)
            self.tile_size = img.width

            # Calculate corner values from index (Wang tile indexing)
            # Index = TL*8 + TR*4 + BL*2 + BR*1
            corners = (
                (i >> 3) & 1,  # TL
                (i >> 2) & 1,  # TR
                (i >> 1) & 1,  # BL
                i & 1,         # BR
            )

            self.tiles.append(TileInfo(index=i, image=img, corners=corners))

    def get_tile_by_corners(
        self,
        tl: int, tr: int, bl: int, br: int
    ) -> Optional[TileInfo]:
        """Get tile by corner values (0=lower, 1=upper)."""
        index = tl * 8 + tr * 4 + bl * 2 + br
        if 0 <= index < len(self.tiles):
            return self.tiles[index]
        return None

    def get_tile_by_index(self, index: int) -> Optional[TileInfo]:
        """Get tile by index."""
        if 0 <= index < len(self.tiles):
            return self.tiles[index]
        return None


class MapAssembler:
    """
    Assembles tiles into complete map images.

    Usage:
        assembler = MapAssembler()

        # From a tileset with explicit layout
        map_img = assembler.create_map_from_tileset(
            tileset_dir,
            layout=[[0, 1, 2], [3, 4, 5]],
            tile_size=16
        )

        # From a terrain map (autotiling)
        terrain_map = [[0, 0, 1], [0, 1, 1], [1, 1, 1]]
        map_img = assembler.create_map_from_terrain(tileset_dir, terrain_map)

        # Export with scaling
        assembler.export_png(map_img, "map.png", scale=4)
    """

    def __init__(self, assets_dir: Optional[Path] = None):
        self.assets_dir = assets_dir or ASSETS_DIR
        self.maps_dir = self.assets_dir / "maps"
        self.maps_dir.mkdir(parents=True, exist_ok=True)

    def create_map_from_tileset(
        self,
        tileset_dir: Union[str, Path],
        layout: list[list[int]],
        tile_size: Optional[int] = None
    ) -> Image.Image:
        """
        Create a map by placing tiles according to a layout.

        Args:
            tileset_dir: Path to tileset directory
            layout: 2D list of tile indices
            tile_size: Override tile size (None = use tileset default)

        Returns:
            Assembled map as PIL Image
        """
        tileset_dir = Path(tileset_dir)
        tileset = WangTileset(tileset_dir)

        if tile_size is None:
            tile_size = tileset.tile_size

        height = len(layout)
        width = len(layout[0]) if layout else 0

        map_img = Image.new(
            "RGBA",
            (width * tile_size, height * tile_size),
            (0, 0, 0, 0)
        )

        for y, row in enumerate(layout):
            for x, tile_index in enumerate(row):
                tile = tileset.get_tile_by_index(tile_index)
                if tile:
                    # Resize if needed
                    tile_img = tile.image
                    if tile_img.size != (tile_size, tile_size):
                        tile_img = tile_img.resize(
                            (tile_size, tile_size),
                            Image.Resampling.NEAREST
                        )
                    map_img.paste(tile_img, (x * tile_size, y * tile_size))

        return map_img

    def create_map_from_terrain(
        self,
        tileset_dir: Union[str, Path],
        terrain_map: list[list[int]],
        tile_size: Optional[int] = None
    ) -> Image.Image:
        """
        Create a map using Wang autotiling from a terrain map.

        The terrain map defines terrain type at each VERTEX (corner).
        Tiles are placed between vertices, so map dimensions are:
        - terrain_map size: (H+1) x (W+1) vertices
        - output tiles: H x W tiles

        Args:
            tileset_dir: Path to tileset directory
            terrain_map: 2D list of terrain values at vertices (0 or 1)
            tile_size: Override tile size

        Returns:
            Assembled map as PIL Image
        """
        tileset_dir = Path(tileset_dir)
        tileset = WangTileset(tileset_dir)

        if tile_size is None:
            tile_size = tileset.tile_size

        # Map dimensions in tiles
        height = len(terrain_map) - 1
        width = len(terrain_map[0]) - 1 if terrain_map else 0

        if height <= 0 or width <= 0:
            raise ValueError("Terrain map must be at least 2x2 vertices")

        map_img = Image.new(
            "RGBA",
            (width * tile_size, height * tile_size),
            (0, 0, 0, 0)
        )

        for y in range(height):
            for x in range(width):
                # Get corner values from terrain map
                tl = terrain_map[y][x]
                tr = terrain_map[y][x + 1]
                bl = terrain_map[y + 1][x]
                br = terrain_map[y + 1][x + 1]

                tile = tileset.get_tile_by_corners(tl, tr, bl, br)
                if tile:
                    tile_img = tile.image
                    if tile_img.size != (tile_size, tile_size):
                        tile_img = tile_img.resize(
                            (tile_size, tile_size),
                            Image.Resampling.NEAREST
                        )
                    map_img.paste(tile_img, (x * tile_size, y * tile_size))

        return map_img

    def stitch_regions(
        self,
        regions: list[tuple[Image.Image, int, int]],
        background_color: tuple[int, int, int, int] = (0, 0, 0, 0)
    ) -> Image.Image:
        """
        Stitch multiple map regions together.

        Args:
            regions: List of (image, x_offset, y_offset) tuples
            background_color: RGBA background color

        Returns:
            Composite map as PIL Image
        """
        if not regions:
            return Image.new("RGBA", (1, 1), background_color)

        # Calculate total dimensions
        max_x = 0
        max_y = 0

        for img, x, y in regions:
            max_x = max(max_x, x + img.width)
            max_y = max(max_y, y + img.height)

        # Create canvas and composite
        canvas = Image.new("RGBA", (max_x, max_y), background_color)

        for img, x, y in regions:
            canvas.paste(img, (x, y), img if img.mode == "RGBA" else None)

        return canvas

    def export_png(
        self,
        map_image: Image.Image,
        output_path: Union[str, Path],
        scale: int = 1
    ) -> Path:
        """
        Export map image to PNG file.

        Args:
            map_image: Map image to export
            output_path: Output file path
            scale: Integer scale factor (1 = original, 2 = 2x, etc.)

        Returns:
            Path to exported file
        """
        output_path = Path(output_path)

        if not output_path.is_absolute():
            output_path = self.maps_dir / output_path

        output_path.parent.mkdir(parents=True, exist_ok=True)

        if scale > 1:
            new_size = (map_image.width * scale, map_image.height * scale)
            map_image = map_image.resize(new_size, Image.Resampling.NEAREST)

        map_image.save(output_path, "PNG")
        print(f"[EXPORT] Map saved: {output_path}")

        return output_path

    def create_simple_map(
        self,
        tileset_dir: Union[str, Path],
        width: int,
        height: int,
        pattern: str = "random"
    ) -> Image.Image:
        """
        Create a simple map with a basic pattern.

        Args:
            tileset_dir: Path to tileset directory
            width: Map width in tiles
            height: Map height in tiles
            pattern: Pattern type ("random", "gradient", "checkerboard", "solid_lower", "solid_upper")

        Returns:
            Map as PIL Image
        """
        import random

        # Create terrain map (vertices, so +1 in each dimension)
        terrain = [[0] * (width + 1) for _ in range(height + 1)]

        if pattern == "random":
            for y in range(height + 1):
                for x in range(width + 1):
                    terrain[y][x] = random.randint(0, 1)

        elif pattern == "gradient":
            for y in range(height + 1):
                threshold = y / height
                for x in range(width + 1):
                    terrain[y][x] = 1 if y / height > 0.5 else 0

        elif pattern == "checkerboard":
            for y in range(height + 1):
                for x in range(width + 1):
                    terrain[y][x] = (x + y) % 2

        elif pattern == "solid_lower":
            pass  # All zeros (default)

        elif pattern == "solid_upper":
            terrain = [[1] * (width + 1) for _ in range(height + 1)]

        else:
            raise ValueError(f"Unknown pattern: {pattern}")

        return self.create_map_from_terrain(tileset_dir, terrain)
