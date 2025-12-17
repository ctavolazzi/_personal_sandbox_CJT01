"""
Map Generator - Direct map generation with inpainting

Uses the official PixelLab Python client (v1 API) for:
- Image generation (pixflux/bitforge)
- Inpainting
- Animation
- Rotation

Implements the workflow from the PixelLab documentation:
- Start with init image (sketch/template)
- Generate initial 4x4 tile area with description
- Expand map by selecting overlapping regions
- Use inpainting to add details and fix areas
"""

import os
import io
import base64
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Union

from PIL import Image
from dotenv import load_dotenv

load_dotenv()

ASSETS_DIR = Path(__file__).parent / "assets"

# Try to import official pixellab client
try:
    import pixellab
    HAS_PIXELLAB_CLIENT = True
except ImportError:
    HAS_PIXELLAB_CLIENT = False
    pixellab = None


@dataclass
class MapRegion:
    """Represents a generated map region."""
    image: Image.Image
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
    description: str = ""
    generation_id: Optional[str] = None
    created_at: Optional[str] = None

    def __post_init__(self):
        if self.width == 0:
            self.width = self.image.width
        if self.height == 0:
            self.height = self.image.height
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def to_base64(self) -> str:
        """Convert image to base64 string."""
        buffer = io.BytesIO()
        self.image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()

    def save(self, path: Union[str, Path]) -> Path:
        """Save region image to file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.image.save(path)
        return path


def _image_to_base64_dict(image: Union[str, Path, Image.Image]) -> dict:
    """Convert image to PixelLab base64 format."""
    if isinstance(image, (str, Path)):
        image = Image.open(image)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    b64 = base64.b64encode(buffer.getvalue()).decode()

    return {"type": "base64", "base64": b64}


class MapGenerator:
    """
    Generates map regions using PixelLab's v1 API.

    Uses the official pixellab Python client for:
    - generate_image_pixflux: Text to pixel art
    - generate_image_bitforge: Style-based with inpainting
    - inpaint: Modify existing images
    - rotate: Rotate characters/objects

    Usage:
        generator = MapGenerator()

        # Create initial region
        region = generator.create_initial_region(
            description="stone dungeon floor with moss",
            width=64,
            height=64
        )

        # Expand the region
        expanded = generator.expand_region(
            region,
            direction="right",
            description="treasure chest on stone floor"
        )

        # Inpaint specific area
        modified = generator.inpaint_area(
            region,
            mask_rect=(16, 16, 32, 32),
            description="glowing magic rune on floor"
        )
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        assets_dir: Optional[Path] = None
    ):
        self.api_key = api_key or os.getenv("PIXELLAB_API_KEY")
        self.assets_dir = assets_dir or ASSETS_DIR
        self.init_images_dir = self.assets_dir / "init_images"
        self.init_images_dir.mkdir(parents=True, exist_ok=True)

        # Initialize official client if available
        self._client = None
        if HAS_PIXELLAB_CLIENT and self.api_key:
            self._client = pixellab.Client(secret=self.api_key)

    @property
    def client(self):
        """Get the PixelLab client, initializing if needed."""
        if self._client is None:
            if not HAS_PIXELLAB_CLIENT:
                raise ImportError(
                    "pixellab package not installed. Run: pip install pixellab"
                )
            if not self.api_key:
                raise ValueError(
                    "PIXELLAB_API_KEY not found. Set it in .env or pass to constructor."
                )
            self._client = pixellab.Client(secret=self.api_key)
        return self._client

    def create_initial_region(
        self,
        description: str,
        width: int = 64,
        height: int = 64,
        init_image: Optional[Union[str, Path, Image.Image]] = None,
        seed: Optional[int] = None,
        use_bitforge: bool = False,
        style_image: Optional[Union[str, Path, Image.Image]] = None,
        **kwargs
    ) -> MapRegion:
        """
        Create an initial map region from a description.

        Args:
            description: Text description of the region
            width: Region width in pixels (max 400x400 area for pixflux, 200x200 for bitforge)
            height: Region height in pixels
            init_image: Optional starting image/sketch
            seed: Random seed for reproducibility
            use_bitforge: Use bitforge model (supports style images)
            style_image: Style reference image (bitforge only)
            **kwargs: Additional API parameters (detail, outline, direction, etc.)

        Returns:
            MapRegion with generated image
        """
        print(f"[GEN] Creating region: {description[:50]}...")

        image_size = {"width": width, "height": height}

        if use_bitforge or style_image:
            # Use bitforge for style-based generation (max 200x200)
            params = {
                "description": description,
                "image_size": image_size,
            }

            if init_image:
                params["init_image"] = _image_to_base64_dict(init_image)

            if style_image:
                params["style_image"] = _image_to_base64_dict(style_image)

            if seed is not None:
                params["seed"] = seed

            # Add optional parameters
            for key in ["detail", "direction", "outline", "shading", "no_background"]:
                if key in kwargs:
                    params[key] = kwargs[key]

            response = self.client.generate_image_bitforge(**params)
        else:
            # Use pixflux for text-to-image (max 400x400)
            params = {
                "description": description,
                "image_size": image_size,
            }

            if init_image:
                params["init_image"] = _image_to_base64_dict(init_image)

            if seed is not None:
                params["seed"] = seed

            # Add optional parameters
            for key in ["detail", "direction", "outline", "shading", "no_background", "isometric"]:
                if key in kwargs:
                    params[key] = kwargs[key]

            response = self.client.generate_image_pixflux(**params)

        # Get image from response
        result_image = response.image.pil_image()

        return MapRegion(
            image=result_image,
            description=description,
        )

    def expand_region(
        self,
        existing_region: MapRegion,
        direction: str,
        description: str,
        overlap: int = 16,
        expansion_size: int = 64,
        **kwargs
    ) -> MapRegion:
        """
        Expand an existing region in a direction.

        Creates a new region that overlaps with the existing one,
        using the overlapping area for context via init_image.

        Args:
            existing_region: The region to expand from
            direction: "up", "down", "left", or "right"
            description: Description for the new area
            overlap: Pixels of overlap for context
            expansion_size: Size of new region
            **kwargs: Additional API parameters

        Returns:
            New MapRegion that overlaps with existing
        """
        print(f"[EXPAND] Expanding {direction}: {description[:50]}...")

        img = existing_region.image
        x, y = existing_region.x, existing_region.y

        if direction == "right":
            context_region = img.crop((img.width - overlap, 0, img.width, img.height))
            new_x = x + img.width - overlap
            new_y = y
            new_width = expansion_size
            new_height = img.height

        elif direction == "left":
            context_region = img.crop((0, 0, overlap, img.height))
            new_x = x - expansion_size + overlap
            new_y = y
            new_width = expansion_size
            new_height = img.height

        elif direction == "down":
            context_region = img.crop((0, img.height - overlap, img.width, img.height))
            new_x = x
            new_y = y + img.height - overlap
            new_width = img.width
            new_height = expansion_size

        elif direction == "up":
            context_region = img.crop((0, 0, img.width, overlap))
            new_x = x
            new_y = y - expansion_size + overlap
            new_width = img.width
            new_height = expansion_size

        else:
            raise ValueError(f"Invalid direction: {direction}")

        # Use context as init_image for continuity
        new_region = self.create_initial_region(
            description=description,
            width=new_width,
            height=new_height,
            init_image=context_region,
            **kwargs
        )

        new_region.x = new_x
        new_region.y = new_y

        return new_region

    def inpaint_area(
        self,
        region: MapRegion,
        mask_rect: tuple[int, int, int, int],
        description: str,
        **kwargs
    ) -> MapRegion:
        """
        Inpaint a rectangular area of a region using v1 API.

        Args:
            region: The region to modify
            mask_rect: (x, y, width, height) of area to inpaint
            description: Description for the inpainted area
            **kwargs: Additional API parameters

        Returns:
            New MapRegion with inpainted area
        """
        print(f"[INPAINT] Modifying area: {description[:50]}...")

        x, y, w, h = mask_rect

        # Create mask image (white = area to generate, black = keep)
        mask = Image.new("L", region.image.size, 0)

        from PIL import ImageDraw
        draw = ImageDraw.Draw(mask)
        draw.rectangle([x, y, x + w, y + h], fill=255)

        # Convert to RGB for API (some APIs expect RGB masks)
        mask_rgb = mask.convert("RGB")

        try:
            response = self.client.inpaint(
                description=description,
                image_size={
                    "width": region.image.width,
                    "height": region.image.height
                },
                inpainting_image=_image_to_base64_dict(region.image),
                mask_image=_image_to_base64_dict(mask_rgb),
                **{k: v for k, v in kwargs.items()
                   if k in ["detail", "direction", "outline", "shading", "no_background"]}
            )

            new_image = response.image.pil_image()

        except Exception as e:
            print(f"[WARN] Inpaint failed ({e}), returning original")
            new_image = region.image.copy()

        return MapRegion(
            image=new_image,
            x=region.x,
            y=region.y,
            description=description,
        )

    def create_map_object(
        self,
        description: str,
        width: int = 64,
        height: int = 64,
        view: str = "high top-down",
        style_image: Optional[Union[str, Path, Image.Image]] = None,
        **kwargs
    ) -> MapRegion:
        """
        Create a map object with transparent background.

        Args:
            description: Object description (e.g., "wooden barrel")
            width: Object width in pixels
            height: Object height in pixels
            view: Camera angle (mapped to direction/isometric)
            style_image: Optional style reference image
            **kwargs: Additional API parameters

        Returns:
            MapRegion with transparent object
        """
        print(f"[OBJECT] Creating: {description[:50]}...")

        # Map view to API parameters
        params = {
            "no_background": True,
        }

        if view == "high top-down":
            params["isometric"] = False
        elif view == "low top-down":
            params["isometric"] = False
        elif view == "side":
            params["direction"] = "south"

        params.update(kwargs)

        return self.create_initial_region(
            description=description,
            width=width,
            height=height,
            style_image=style_image,
            use_bitforge=style_image is not None,
            **params
        )

    def rotate_object(
        self,
        image: Union[str, Path, Image.Image, MapRegion],
        from_direction: str = "south",
        to_direction: str = "east",
        from_view: str = "side",
        to_view: str = "side",
        **kwargs
    ) -> MapRegion:
        """
        Rotate a character or object to a new direction.

        Args:
            image: Source image or MapRegion
            from_direction: Current direction (north, south, east, west, etc.)
            to_direction: Target direction
            from_view: Current view (side, low top-down, high top-down)
            to_view: Target view
            **kwargs: Additional API parameters

        Returns:
            MapRegion with rotated object
        """
        if isinstance(image, MapRegion):
            source_image = image.image
        elif isinstance(image, (str, Path)):
            source_image = Image.open(image)
        else:
            source_image = image

        print(f"[ROTATE] {from_direction} → {to_direction}")

        response = self.client.rotate(
            from_image=_image_to_base64_dict(source_image),
            image_size={
                "width": source_image.width,
                "height": source_image.height
            },
            from_direction=from_direction,
            to_direction=to_direction,
            from_view=from_view,
            to_view=to_view,
            **kwargs
        )

        result_image = response.image.pil_image()

        return MapRegion(
            image=result_image,
            description=f"Rotated from {from_direction} to {to_direction}",
        )

    def animate_object(
        self,
        reference_image: Union[str, Path, Image.Image, MapRegion],
        action: str = "walk",
        description: str = "",
        direction: str = "south",
        n_frames: int = 4,
        **kwargs
    ) -> list[MapRegion]:
        """
        Generate animation frames for a character.

        Args:
            reference_image: Reference character image
            action: Animation action (walk, run, idle, etc.)
            description: Character description
            direction: Direction facing
            n_frames: Number of frames (2-20, generates 4 at a time)
            **kwargs: Additional API parameters

        Returns:
            List of MapRegion frames
        """
        if isinstance(reference_image, MapRegion):
            source_image = reference_image.image
        elif isinstance(reference_image, (str, Path)):
            source_image = Image.open(reference_image)
        else:
            source_image = reference_image

        print(f"[ANIMATE] {action} animation ({n_frames} frames)")

        response = self.client.animate_with_text(
            description=description or "pixel art character",
            action=action,
            view="side",
            direction=direction,
            image_size={
                "width": source_image.width,
                "height": source_image.height
            },
            reference_image=_image_to_base64_dict(source_image),
            n_frames=n_frames,
            **kwargs
        )

        frames = []
        for i, img_response in enumerate(response.images):
            frame_image = img_response.pil_image()
            frames.append(MapRegion(
                image=frame_image,
                description=f"{action} frame {i + 1}",
            ))

        return frames
