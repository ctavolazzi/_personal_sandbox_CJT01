# MapForge

**Pixel Art Map Generation Toolkit** - Generate pixel art maps using PixelLab's Wang tileset and AI generation APIs.

## Features

- 🎨 **Wang Tileset Generation** - Create seamless terrain transitions (ocean → beach → grass)
- 🗺️ **Autotile Map Assembly** - Compose tiles into maps using corner-based Wang tiling
- 🎮 **Direct Generation** - Generate map regions from text descriptions (pixflux/bitforge)
- 🧱 **Map Objects** - Create objects with transparent backgrounds
- 🔄 **Rotation** - Rotate characters/objects to different directions
- 🎬 **Animation** - Generate animation frames from text descriptions
- ✏️ **Inpainting** - Edit and modify existing pixel art
- 📦 **CLI Interface** - Command-line tools for all operations

## Installation

```bash
cd projects/mapforge
pip install -r requirements.txt
```

**Note:** Uses the official [PixelLab Python client](https://github.com/pixellab-ai/pixellab-python) for v1 API operations.

## Configuration

Set your PixelLab API key:

```bash
export PIXELLAB_API_KEY="your-api-key-here"
```

Or create a `.env` file:

```
PIXELLAB_API_KEY=your-api-key-here
```

## Quick Start

### Python API

```python
from mapforge import MapForge

mf = MapForge()

# Workflow 1: Tileset-based map generation
results = mf.create_tileset_chain(["ocean water", "sandy beach", "grass"])
map_img = mf.generate_map_from_tileset(results[0], width=10, height=10)
mf.save_map(map_img, "beach_map.png", scale=4)

# Workflow 2: Direct AI generation
region = mf.generate_region("stone dungeon floor with moss")
region = mf.expand_region(region, "right", "treasure room with chest")
mf.save_map(region.image, "dungeon.png")

# Create map objects
barrel = mf.create_map_object("wooden barrel", width=32, height=32)
mf.save_map(barrel.image, "barrel.png")
```

### CLI

```bash
# Create a tileset chain
python -m mapforge tileset create "ocean water" "sandy beach" "grass"

# Generate a map from tileset
python -m mapforge map from-tileset ocean_8f3a --width 10 --height 10 --output beach.png

# Direct map generation
python -m mapforge map generate "cave with stairs and torches" --output cave.png

# Create a map object
python -m mapforge object create "wooden barrel" --output barrel.png

# List local tilesets
python -m mapforge tileset list
```

## Workflows

### Workflow 1: Wang Tileset Maps

Best for: **Terrain-based maps** with seamless transitions.

1. **Create tileset chain** - Generate connected tilesets
2. **Define terrain map** - Set terrain type at each vertex
3. **Assemble map** - Auto-select tiles based on corners

```python
# Create terrain chain: ocean → beach → grass
results = mf.create_tileset_chain([
    "ocean water",
    "sandy beach",
    "grass field"
])

# Define custom terrain layout (0=lower, 1=upper)
terrain = [
    [0, 0, 0, 1, 1],
    [0, 0, 1, 1, 1],
    [0, 1, 1, 1, 1],
    [1, 1, 1, 1, 1],
]
map_img = mf.generate_map_from_terrain(results[0], terrain)

# Or use a pattern
map_img = mf.generate_map_from_tileset(results[0], width=10, height=10, pattern="random")
```

### Workflow 2: Direct Generation

Best for: **Custom regions** with specific content.

1. **Generate initial region** - Create from text description
2. **Expand regions** - Add connected areas
3. **Stitch together** - Combine into final map

```python
# Create initial region
dungeon = mf.generate_region("stone dungeon corridor with torches", width=64, height=64)

# Expand in multiple directions
right = mf.expand_region(dungeon, "right", "treasure room with gold chest")
down = mf.expand_region(dungeon, "down", "dark prison cells")

# Stitch regions together
final_map = mf.stitch_regions([dungeon, right, down])
mf.save_map(final_map, "dungeon_complete.png")
```

### Workflow 3: Character Animation

Best for: **Game characters** with movement animations.

```python
from mapforge import MapGenerator

gen = MapGenerator()

# Create a character
wizard = gen.create_initial_region("pixel art wizard with staff", width=64, height=64, no_background=True)

# Rotate to different directions
wizard_east = gen.rotate_object(wizard, from_direction="south", to_direction="east")
wizard_north = gen.rotate_object(wizard, from_direction="south", to_direction="north")

# Generate walk animation
walk_frames = gen.animate_object(wizard, action="walk", description="wizard", n_frames=4)
```

## Wang Tileset Explained

Wang tiles use **corner-based indexing** where each corner can be either:
- **0**: Lower terrain (e.g., water)
- **1**: Upper terrain (e.g., beach)

```
Tile Corner Layout:
    TL ── TR
    │     │
    BL ── BR

Index = TL×8 + TR×4 + BL×2 + BR×1
```

This gives 16 unique tiles (2^4 = 16) covering all possible corner combinations.

### Chaining Tilesets

To create seamless multi-terrain transitions:

```python
# Creates: ocean→beach tileset, then beach→grass tileset
# The beach tiles are visually consistent across both
results = mf.create_tileset_chain(["ocean", "beach", "grass"])
```

## API Reference

### MapForge

Main interface combining all components.

```python
class MapForge:
    # Tileset operations
    create_tileset(lower, upper, **kwargs) -> TilesetResult
    create_tileset_chain(terrains, **kwargs) -> list[TilesetResult]

    # Map generation
    generate_map_from_tileset(tileset, width, height, pattern) -> Image
    generate_map_from_terrain(tileset, terrain_map) -> Image

    # Direct generation
    generate_region(description, width, height, **kwargs) -> MapRegion
    expand_region(region, direction, description, **kwargs) -> MapRegion
    create_map_object(description, width, height, **kwargs) -> MapRegion

    # Utilities
    stitch_regions(regions) -> Image
    save_map(image, path, scale) -> Path
    list_tilesets() -> list[dict]
```

### TilesetManager

Low-level tileset operations.

```python
class TilesetManager:
    create_tileset(lower, upper, **kwargs) -> TilesetResult
    get_tileset(tileset_id) -> TilesetResult
    wait_for_completion(tileset_id, max_wait) -> TilesetResult
    save_tileset_images(tileset_id, output_dir) -> list[Path]
    create_terrain_chain(terrains, **kwargs) -> list[TilesetResult]
```

### MapAssembler

Map composition and export.

```python
class MapAssembler:
    create_map_from_tileset(tileset_dir, layout) -> Image
    create_map_from_terrain(tileset_dir, terrain_map) -> Image
    create_simple_map(tileset_dir, width, height, pattern) -> Image
    stitch_regions(regions) -> Image
    export_png(image, path, scale) -> Path
```

### MapGenerator

Direct AI generation using PixelLab v1 API.

```python
class MapGenerator:
    # Image generation (pixflux or bitforge)
    create_initial_region(description, width, height, **kwargs) -> MapRegion
    expand_region(region, direction, description, **kwargs) -> MapRegion

    # Inpainting
    inpaint_area(region, mask_rect, description, **kwargs) -> MapRegion

    # Objects
    create_map_object(description, width, height, **kwargs) -> MapRegion

    # Rotation
    rotate_object(image, from_direction, to_direction, **kwargs) -> MapRegion

    # Animation
    animate_object(reference_image, action, description, n_frames, **kwargs) -> list[MapRegion]
```

#### Generation Models

| Model | Max Size | Features |
|-------|----------|----------|
| **pixflux** | 400×400 | Text-to-image, transparent bg, init image |
| **bitforge** | 200×200 | Style images, inpainting, init image |

## File Structure

```
mapforge/
├── __init__.py           # Package exports
├── __main__.py           # CLI entry point
├── mapforge.py           # Main API
├── tileset_manager.py    # Tileset operations
├── map_generator.py      # Direct generation
├── map_assembler.py      # Map composition
├── cli.py                # CLI commands
├── requirements.txt
├── README.md
├── assets/
│   ├── tilesets/         # Generated Wang tilesets
│   ├── maps/             # Assembled map PNGs
│   └── init_images/      # Template images
└── tests/
    └── test_mapforge.py
```

## Tileset Options

| Option | Values | Description |
|--------|--------|-------------|
| `tile_size` | 16, 32 | Tile dimensions in pixels |
| `transition_size` | 0.0, 0.25, 0.5, 1.0 | Terrain transition size |
| `outline` | "single color outline", "selective outline", "lineless" | Outline style |
| `shading` | "flat shading" to "highly detailed shading" | Shading complexity |
| `detail` | "low detail", "medium detail", "highly detailed" | Detail level |
| `view` | "low top-down", "high top-down" | Camera angle |

## Examples

### Beach Scene

```python
mf = MapForge()

# Create terrain chain
results = mf.create_tileset_chain([
    "deep blue ocean water",
    "sandy beach with shells",
    "grass with small flowers"
])

# Generate random beach map
beach = mf.generate_map_from_tileset(results[0], width=15, height=10, pattern="gradient")
mf.save_map(beach, "beach.png", scale=4)
```

### Dungeon Crawler

```python
mf = MapForge()

# Create dungeon floor
floor = mf.generate_region("dark stone dungeon floor with cracks", width=128, height=128)

# Add rooms
treasure = mf.expand_region(floor, "right", "golden treasure room")
prison = mf.expand_region(floor, "down", "rusty prison cells")
boss = mf.expand_region(treasure, "down", "dark boss arena with pillars")

# Combine
dungeon = mf.stitch_regions([floor, treasure, prison, boss])
mf.save_map(dungeon, "dungeon.png", scale=2)
```

## License

MIT License - See project root for details.

## Credits

- [PixelLab](https://pixellab.ai) - AI pixel art generation API
- Inspired by Wang tiles research and autotiling techniques
