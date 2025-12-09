"""
Generate whimsical procedural backgrounds using Pillow.
No API needed - pure algorithmic art.

Usage:
    python generate_procedural_backgrounds.py
"""

import random
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

OUTPUT_DIR = Path(__file__).parent / "assets" / "backgrounds"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def lerp_color(c1, c2, t):
    """Linear interpolate between two RGB colors."""
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def generate_gradient(size, colors, angle=0):
    """Generate a smooth gradient background."""
    img = Image.new('RGB', size)
    draw = ImageDraw.Draw(img)

    for y in range(size[1]):
        t = y / size[1]
        # Multi-stop gradient
        if len(colors) == 2:
            color = lerp_color(colors[0], colors[1], t)
        else:
            segment = t * (len(colors) - 1)
            idx = int(segment)
            local_t = segment - idx
            if idx >= len(colors) - 1:
                color = colors[-1]
            else:
                color = lerp_color(colors[idx], colors[idx + 1], local_t)

        draw.line([(0, y), (size[0], y)], fill=color)

    return img


def add_bokeh(img, count=30):
    """Add soft bokeh circles."""
    draw = ImageDraw.Draw(img, 'RGBA')

    for _ in range(count):
        x = random.randint(0, img.width)
        y = random.randint(0, img.height)
        r = random.randint(20, 80)
        alpha = random.randint(15, 50)

        # Soft pastel colors
        colors = [
            (255, 200, 150, alpha),  # Warm peach
            (200, 180, 255, alpha),  # Soft lavender
            (255, 220, 200, alpha),  # Cream
            (180, 220, 255, alpha),  # Sky blue
        ]
        color = random.choice(colors)

        draw.ellipse([x-r, y-r, x+r, y+r], fill=color)

    return img


def add_stars(img, count=100):
    """Add twinkling stars."""
    draw = ImageDraw.Draw(img, 'RGBA')

    for _ in range(count):
        x = random.randint(0, img.width)
        y = random.randint(0, img.height)
        r = random.randint(1, 3)
        alpha = random.randint(100, 255)

        draw.ellipse([x-r, y-r, x+r, y+r], fill=(255, 255, 255, alpha))

    return img


def generate_dreamy_watercolor():
    """Purple and gold dreamy gradient with bokeh."""
    colors = [
        (45, 25, 70),    # Deep purple
        (80, 50, 100),   # Mid purple
        (150, 100, 60),  # Gold-ish
        (60, 40, 80),    # Back to purple
    ]
    img = generate_gradient((1080, 1080), colors)
    img = add_bokeh(img, count=40)
    img = img.filter(ImageFilter.GaussianBlur(radius=3))
    return img


def generate_cosmic_night():
    """Deep blue cosmic sky with stars."""
    colors = [
        (10, 15, 40),    # Deep navy
        (30, 50, 90),    # Dark blue
        (80, 60, 100),   # Purple hint
        (20, 30, 60),    # Back to navy
    ]
    img = generate_gradient((1080, 1080), colors)
    img = add_stars(img, count=150)
    img = add_bokeh(img, count=15)
    img = img.filter(ImageFilter.GaussianBlur(radius=1))
    return img


def generate_sunset_calm():
    """Soft pastel sunset."""
    colors = [
        (255, 180, 150),  # Warm peach
        (255, 150, 180),  # Pink
        (200, 150, 200),  # Lavender
        (100, 120, 180),  # Dusk blue
    ]
    img = generate_gradient((1080, 1080), colors)
    img = add_bokeh(img, count=20)
    img = img.filter(ImageFilter.GaussianBlur(radius=4))
    return img


def generate_forest_magic():
    """Enchanted forest greens."""
    colors = [
        (20, 40, 30),    # Deep forest
        (40, 80, 50),    # Emerald
        (60, 50, 40),    # Amber hint
        (30, 50, 40),    # Back to green
    ]
    img = generate_gradient((1080, 1080), colors)

    # Add magical floating lights
    draw = ImageDraw.Draw(img, 'RGBA')
    for _ in range(25):
        x = random.randint(0, img.width)
        y = random.randint(0, img.height)
        r = random.randint(5, 15)
        alpha = random.randint(80, 180)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=(200, 255, 180, alpha))

    img = img.filter(ImageFilter.GaussianBlur(radius=2))
    return img


def main():
    print("=" * 60)
    print("🎨 PROCEDURAL BACKGROUND GENERATOR")
    print("=" * 60)

    generators = [
        ("whimsical_dreamy", generate_dreamy_watercolor),
        ("whimsical_cosmic", generate_cosmic_night),
        ("whimsical_sunset", generate_sunset_calm),
        ("whimsical_forest", generate_forest_magic),
    ]

    for name, gen_func in generators:
        print(f"🎨 Generating: {name}...")
        img = gen_func()
        path = OUTPUT_DIR / f"{name}.png"
        img.save(path, quality=95)
        print(f"✅ Saved: {path.name}")

    print()
    print("=" * 60)
    print(f"🎉 Generated {len(generators)} backgrounds")
    print(f"📁 Location: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
