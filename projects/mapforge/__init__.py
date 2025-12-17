"""
MapForge - Pixel Art Map Generation Toolkit

Generate pixel art maps using PixelLab's Wang tileset and inpainting APIs.

Usage:
    from mapforge import MapForge

    mf = MapForge()

    # Workflow 1: Tileset-based
    tileset = mf.create_tileset_chain(["ocean water", "sandy beach", "grass"])
    map_img = mf.generate_map_from_tileset(tileset, width=10, height=10)
    mf.save_map(map_img, "beach_map.png")

    # Workflow 2: Direct generation
    region = mf.generate_region("stairs in a cave", init_image="cave_sketch.png")
    mf.save_map(region.image, "cave_map.png")
"""

from .mapforge import MapForge
from .tileset_manager import TilesetManager
from .map_assembler import MapAssembler
from .map_generator import MapGenerator, MapRegion

__version__ = "0.1.0"
__all__ = ["MapForge", "TilesetManager", "MapAssembler", "MapGenerator", "MapRegion"]
