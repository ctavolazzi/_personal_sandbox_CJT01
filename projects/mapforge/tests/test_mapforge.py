"""
Tests for MapForge

Run with: pytest tests/test_mapforge.py -v

Note: Tests are designed to work offline using mock data.
To test with live API, set PIXELLAB_API_KEY and use -m live marker.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PIL import Image

# Import components
from mapforge import MapForge, TilesetManager, MapAssembler, MapGenerator, MapRegion


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_api_key():
    """Provide a mock API key."""
    return "test-api-key-12345"


@pytest.fixture
def temp_assets_dir(tmp_path):
    """Create temporary assets directory."""
    assets = tmp_path / "assets"
    assets.mkdir()
    (assets / "tilesets").mkdir()
    (assets / "maps").mkdir()
    return assets


@pytest.fixture
def sample_tileset_dir(temp_assets_dir):
    """Create a sample tileset directory with mock tiles."""
    tileset_dir = temp_assets_dir / "tilesets" / "test_ts"
    tileset_dir.mkdir(parents=True)

    # Create 16 mock tile images (16x16 pixels each)
    for i in range(16):
        tile = Image.new("RGBA", (16, 16), color=(i * 16, 100, 150, 255))
        tile.save(tileset_dir / f"tile_{i:02d}.png")

    # Create metadata
    metadata = {
        "tileset_id": "test_ts_12345678",
        "lower_base_tile_id": "base_lower_123",
        "upper_base_tile_id": "base_upper_456",
        "tile_count": 16
    }
    (tileset_dir / "metadata.json").write_text(json.dumps(metadata))

    return tileset_dir


@pytest.fixture
def sample_region():
    """Create a sample MapRegion."""
    img = Image.new("RGBA", (64, 64), color=(100, 150, 200, 255))
    return MapRegion(image=img, description="test region")


# =============================================================================
# MapAssembler Tests (Offline)
# =============================================================================

class TestMapAssembler:
    """Tests for MapAssembler - works offline with mock tilesets."""

    def test_create_map_from_layout(self, temp_assets_dir, sample_tileset_dir):
        """Test creating a map from explicit tile layout."""
        assembler = MapAssembler(assets_dir=temp_assets_dir)

        # Simple 2x2 layout
        layout = [[0, 1], [2, 3]]

        map_img = assembler.create_map_from_tileset(sample_tileset_dir, layout)

        assert map_img.size == (32, 32)  # 2x2 tiles at 16px each
        assert map_img.mode == "RGBA"

    def test_create_map_from_terrain(self, temp_assets_dir, sample_tileset_dir):
        """Test autotile map generation from terrain map."""
        assembler = MapAssembler(assets_dir=temp_assets_dir)

        # 3x3 vertex grid = 2x2 tile output
        terrain = [
            [0, 0, 1],
            [0, 1, 1],
            [1, 1, 1]
        ]

        map_img = assembler.create_map_from_terrain(sample_tileset_dir, terrain)

        assert map_img.size == (32, 32)  # 2x2 tiles

    def test_create_simple_map_random(self, temp_assets_dir, sample_tileset_dir):
        """Test simple map with random pattern."""
        assembler = MapAssembler(assets_dir=temp_assets_dir)

        map_img = assembler.create_simple_map(
            sample_tileset_dir,
            width=5,
            height=5,
            pattern="random"
        )

        assert map_img.size == (80, 80)  # 5x5 tiles at 16px

    def test_create_simple_map_checkerboard(self, temp_assets_dir, sample_tileset_dir):
        """Test simple map with checkerboard pattern."""
        assembler = MapAssembler(assets_dir=temp_assets_dir)

        map_img = assembler.create_simple_map(
            sample_tileset_dir,
            width=4,
            height=4,
            pattern="checkerboard"
        )

        assert map_img.size == (64, 64)

    def test_export_png(self, temp_assets_dir, sample_tileset_dir):
        """Test exporting map to PNG file."""
        assembler = MapAssembler(assets_dir=temp_assets_dir)

        map_img = Image.new("RGBA", (32, 32), color=(255, 0, 0, 255))
        output_path = assembler.export_png(map_img, "test_map.png")

        assert output_path.exists()
        assert output_path.suffix == ".png"

    def test_export_png_scaled(self, temp_assets_dir, sample_tileset_dir):
        """Test exporting scaled map."""
        assembler = MapAssembler(assets_dir=temp_assets_dir)

        map_img = Image.new("RGBA", (32, 32), color=(0, 255, 0, 255))
        output_path = assembler.export_png(map_img, "test_scaled.png", scale=4)

        assert output_path.exists()

        # Verify scaled size
        loaded = Image.open(output_path)
        assert loaded.size == (128, 128)

    def test_stitch_regions(self, temp_assets_dir):
        """Test stitching multiple regions together."""
        assembler = MapAssembler(assets_dir=temp_assets_dir)

        # Create two regions
        region1 = Image.new("RGBA", (32, 32), color=(255, 0, 0, 255))
        region2 = Image.new("RGBA", (32, 32), color=(0, 255, 0, 255))

        regions = [
            (region1, 0, 0),
            (region2, 32, 0)
        ]

        combined = assembler.stitch_regions(regions)

        assert combined.size == (64, 32)


# =============================================================================
# MapRegion Tests (Offline)
# =============================================================================

class TestMapRegion:
    """Tests for MapRegion dataclass."""

    def test_map_region_creation(self):
        """Test creating a MapRegion."""
        img = Image.new("RGBA", (64, 64))
        region = MapRegion(image=img, description="test")

        assert region.width == 64
        assert region.height == 64
        assert region.x == 0
        assert region.y == 0

    def test_map_region_to_base64(self, sample_region):
        """Test converting region to base64."""
        b64 = sample_region.to_base64()

        assert isinstance(b64, str)
        assert len(b64) > 0

    def test_map_region_save(self, sample_region, tmp_path):
        """Test saving region to file."""
        output_path = tmp_path / "region.png"
        saved = sample_region.save(output_path)

        assert saved.exists()
        assert saved == output_path


# =============================================================================
# WangTileset Tests (Offline)
# =============================================================================

class TestWangTileset:
    """Tests for WangTileset class."""

    def test_load_tileset(self, sample_tileset_dir):
        """Test loading a tileset from directory."""
        from mapforge.map_assembler import WangTileset

        tileset = WangTileset(sample_tileset_dir)

        assert len(tileset.tiles) == 16
        assert tileset.tile_size == 16

    def test_get_tile_by_index(self, sample_tileset_dir):
        """Test getting tile by index."""
        from mapforge.map_assembler import WangTileset

        tileset = WangTileset(sample_tileset_dir)

        tile = tileset.get_tile_by_index(0)
        assert tile is not None
        assert tile.index == 0

        tile = tileset.get_tile_by_index(15)
        assert tile is not None
        assert tile.index == 15

    def test_get_tile_by_corners(self, sample_tileset_dir):
        """Test getting tile by corner values."""
        from mapforge.map_assembler import WangTileset

        tileset = WangTileset(sample_tileset_dir)

        # All lower (0,0,0,0) = index 0
        tile = tileset.get_tile_by_corners(0, 0, 0, 0)
        assert tile is not None
        assert tile.index == 0

        # All upper (1,1,1,1) = index 15
        tile = tileset.get_tile_by_corners(1, 1, 1, 1)
        assert tile is not None
        assert tile.index == 15


# =============================================================================
# TilesetManager Tests (Mock API)
# =============================================================================

class TestTilesetManagerMock:
    """Tests for TilesetManager with mocked API calls."""

    @patch("mapforge.tileset_manager.requests")
    def test_create_tileset(self, mock_requests, mock_api_key, temp_assets_dir):
        """Test creating a tileset (mocked API)."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {"tileset_id": "test-id-12345"}
        }
        mock_response.raise_for_status = Mock()
        mock_requests.post.return_value = mock_response

        manager = TilesetManager(
            api_key=mock_api_key,
            assets_dir=temp_assets_dir / "tilesets"
        )

        result = manager.create_tileset("ocean", "beach")

        assert result.tileset_id == "test-id-12345"
        assert result.status == "pending"

    @patch("mapforge.tileset_manager.requests")
    def test_get_tileset(self, mock_requests, mock_api_key, temp_assets_dir):
        """Test getting tileset status (mocked API)."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "status": "completed",
                "lower_base_tile_id": "lower_123",
                "upper_base_tile_id": "upper_456",
                "tiles": []
            }
        }
        mock_response.raise_for_status = Mock()
        mock_requests.get.return_value = mock_response

        manager = TilesetManager(
            api_key=mock_api_key,
            assets_dir=temp_assets_dir / "tilesets"
        )

        result = manager.get_tileset("test-id")

        assert result.status == "completed"
        assert result.lower_base_tile_id == "lower_123"


# =============================================================================
# MapGenerator Tests (Mock API)
# =============================================================================

class TestMapGeneratorMock:
    """Tests for MapGenerator with mocked pixellab client."""

    @patch("mapforge.map_generator.pixellab")
    @patch("mapforge.map_generator.HAS_PIXELLAB_CLIENT", True)
    def test_create_initial_region(self, mock_pixellab, mock_api_key, temp_assets_dir):
        """Test creating initial region (mocked client)."""
        # Create a mock image response
        test_img = Image.new("RGBA", (64, 64), color=(100, 150, 200, 255))

        # Mock the pixellab client response
        mock_image_response = Mock()
        mock_image_response.pil_image.return_value = test_img

        mock_response = Mock()
        mock_response.image = mock_image_response

        mock_client = Mock()
        mock_client.generate_image_pixflux.return_value = mock_response
        mock_pixellab.Client.return_value = mock_client

        generator = MapGenerator(
            api_key=mock_api_key,
            assets_dir=temp_assets_dir
        )
        # Force client initialization
        generator._client = mock_client

        region = generator.create_initial_region("test dungeon", width=64, height=64)

        assert region.image.size == (64, 64)
        assert region.description == "test dungeon"

    @patch("mapforge.map_generator.pixellab")
    @patch("mapforge.map_generator.HAS_PIXELLAB_CLIENT", True)
    def test_inpaint_area(self, mock_pixellab, mock_api_key, temp_assets_dir, sample_region):
        """Test inpainting an area (mocked client)."""
        # Create a mock inpaint response
        test_img = Image.new("RGBA", (64, 64), color=(200, 100, 150, 255))

        mock_image_response = Mock()
        mock_image_response.pil_image.return_value = test_img

        mock_response = Mock()
        mock_response.image = mock_image_response

        mock_client = Mock()
        mock_client.inpaint.return_value = mock_response
        mock_pixellab.Client.return_value = mock_client

        generator = MapGenerator(
            api_key=mock_api_key,
            assets_dir=temp_assets_dir
        )
        generator._client = mock_client

        result = generator.inpaint_area(
            sample_region,
            mask_rect=(10, 10, 20, 20),
            description="magic rune"
        )

        assert result.image.size == (64, 64)
        assert result.description == "magic rune"


# =============================================================================
# MapForge Integration Tests (Mock)
# =============================================================================

class TestMapForgeIntegration:
    """Integration tests for MapForge with mocked components."""

    def test_list_tilesets(self, mock_api_key, tmp_path):
        """Test listing local tilesets."""
        # Create assets directory structure
        assets_dir = tmp_path / "assets"
        assets_dir.mkdir()
        tilesets_dir = assets_dir / "tilesets"
        tilesets_dir.mkdir()

        # Create a sample tileset directly in the temp directory
        tileset_dir = tilesets_dir / "test_ts"
        tileset_dir.mkdir()

        # Create mock tiles
        from PIL import Image
        for i in range(16):
            tile = Image.new("RGBA", (16, 16), color=(i * 16, 100, 150, 255))
            tile.save(tileset_dir / f"tile_{i:02d}.png")

        # Create metadata
        metadata = {
            "tileset_id": "test_ts_12345678",
            "lower_base_tile_id": "base_lower_123",
            "upper_base_tile_id": "base_upper_456",
            "tile_count": 16
        }
        (tileset_dir / "metadata.json").write_text(json.dumps(metadata))

        mf = MapForge(api_key=mock_api_key, assets_dir=assets_dir)

        tilesets = mf.list_tilesets()

        assert len(tilesets) >= 1

    def test_save_map(self, mock_api_key, temp_assets_dir):
        """Test saving a map."""
        mf = MapForge(api_key=mock_api_key, assets_dir=temp_assets_dir)

        img = Image.new("RGBA", (64, 64), color=(255, 0, 0, 255))
        path = mf.save_map(img, "test_output.png")

        assert path.exists()

    def test_save_map_from_region(self, mock_api_key, temp_assets_dir, sample_region):
        """Test saving a map from MapRegion."""
        mf = MapForge(api_key=mock_api_key, assets_dir=temp_assets_dir)

        path = mf.save_map(sample_region, "region_output.png", scale=2)

        assert path.exists()

        loaded = Image.open(path)
        assert loaded.size == (128, 128)


# =============================================================================
# CLI Tests
# =============================================================================

class TestCLI:
    """Tests for CLI commands."""

    def test_cli_import(self):
        """Test CLI module imports correctly."""
        from mapforge.cli import main
        assert callable(main)

    def test_cli_tileset_list(self):
        """Test tileset list command function exists."""
        # This would require more complex mocking of sys.argv
        # For now just verify the function exists and is callable
        from mapforge.cli import cmd_tileset_list
        assert callable(cmd_tileset_list)


# =============================================================================
# Markers for live tests
# =============================================================================

@pytest.mark.live
class TestLiveAPI:
    """
    Live API tests - only run with explicit -m live flag.

    These tests make real API calls and consume credits.
    """

    @pytest.mark.skip(reason="Requires live API key and consumes credits")
    def test_live_create_tileset(self):
        """Test creating a real tileset."""
        pass

    @pytest.mark.skip(reason="Requires live API key and consumes credits")
    def test_live_generate_region(self):
        """Test generating a real region."""
        pass
