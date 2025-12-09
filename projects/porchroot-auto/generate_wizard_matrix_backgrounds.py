"""
Pixel Art Wizard Matrix Backgrounds
Fantasy wizards hacking into the Matrix - whimsical cyberpunk meets magic.

Usage:
    python generate_wizard_matrix_backgrounds.py
"""

import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

OUTPUT_DIR = Path(__file__).parent / "assets" / "backgrounds"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Pixel art palette - Matrix green + magical purple/gold
MATRIX_GREEN = (0, 255, 65)
MATRIX_DARK = (0, 40, 10)
MAGIC_PURPLE = (180, 100, 255)
MAGIC_GOLD = (255, 215, 0)
WIZARD_BLUE = (100, 150, 255)
DEEP_VOID = (5, 5, 15)


def pixelate(img, pixel_size=4):
    """Pixelate an image for retro effect."""
    small = img.resize(
        (img.width // pixel_size, img.height // pixel_size),
        Image.Resampling.NEAREST
    )
    return small.resize(img.size, Image.Resampling.NEAREST)


def draw_matrix_rain(draw, width, height, density=40):
    """Draw falling Matrix code columns."""
    chars = "01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"

    for _ in range(density):
        x = random.randint(0, width)
        col_height = random.randint(100, 400)
        y_start = random.randint(-200, height)

        for i in range(0, col_height, 20):
            y = y_start + i
            if 0 <= y <= height:
                # Fade from bright to dim
                brightness = max(0, 255 - (i * 2))
                if i < 40:  # Head of the rain is brightest
                    color = (0, 255, 65)
                else:
                    color = (0, brightness // 2, brightness // 8)

                char = random.choice(chars)
                draw.text((x, y), char, fill=color)


def draw_pixel_stars(draw, width, height, count=50):
    """Draw pixel art magical stars."""
    for _ in range(count):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.choice([2, 4, 6])

        # Magic colors
        color = random.choice([
            MAGIC_PURPLE,
            MAGIC_GOLD,
            WIZARD_BLUE,
            (255, 255, 255),
        ])

        # Pixel star pattern
        draw.rectangle([x, y, x+size, y+size], fill=color)
        if size > 2:
            # Add cross pattern for bigger stars
            draw.rectangle([x-size, y+size//2, x, y+size//2+size//2], fill=color)
            draw.rectangle([x+size, y+size//2, x+size*2, y+size//2+size//2], fill=color)
            draw.rectangle([x+size//2, y-size, x+size//2+size//2, y], fill=color)
            draw.rectangle([x+size//2, y+size, x+size//2+size//2, y+size*2], fill=color)


def draw_magic_runes(draw, width, height):
    """Draw floating magical runes/symbols."""
    runes = "⚡✧☆★◇◆▲△●○⬡⬢⎔⏣⏢"

    for _ in range(15):
        x = random.randint(50, width - 50)
        y = random.randint(50, height - 50)

        rune = random.choice(runes)
        color = random.choice([MAGIC_PURPLE, MAGIC_GOLD, WIZARD_BLUE])
        alpha = random.randint(100, 200)

        # Draw with glow effect (multiple layers)
        for offset in range(3, 0, -1):
            glow_color = tuple(list(color) + [alpha // offset])
            draw.text((x-offset, y-offset), rune, fill=color)
            draw.text((x+offset, y+offset), rune, fill=color)
        draw.text((x, y), rune, fill=color)


def draw_pixel_wizard_hat(draw, x, y, size=60):
    """Draw a simple pixel art wizard hat."""
    # Hat cone
    color = random.choice([MAGIC_PURPLE, WIZARD_BLUE, (100, 50, 150)])

    # Pixelated triangle for hat
    for row in range(size):
        width_at_row = row * 2
        left = x - width_at_row // 2
        draw.rectangle(
            [left, y + row, left + width_at_row, y + row + 4],
            fill=color
        )

    # Hat brim
    brim_y = y + size
    draw.rectangle([x - size, brim_y, x + size, brim_y + 8], fill=color)

    # Star on hat
    draw.rectangle([x - 4, y + size // 3, x + 4, y + size // 3 + 8], fill=MAGIC_GOLD)


def generate_matrix_void():
    """Deep void with Matrix rain."""
    img = Image.new('RGB', (1080, 1080), DEEP_VOID)
    draw = ImageDraw.Draw(img)

    # Matrix rain
    draw_matrix_rain(draw, 1080, 1080, density=60)

    # Pixel stars
    draw_pixel_stars(draw, 1080, 1080, count=30)

    # Pixelate for retro feel
    img = pixelate(img, pixel_size=3)

    return img


def generate_wizard_matrix():
    """Wizard-themed Matrix background."""
    # Gradient from purple to green
    img = Image.new('RGB', (1080, 1080))
    draw = ImageDraw.Draw(img)

    for y in range(1080):
        t = y / 1080
        r = int(20 + t * 10)
        g = int(10 + t * 40)
        b = int(40 - t * 30)
        draw.line([(0, y), (1080, y)], fill=(r, g, b))

    # Matrix rain (lighter)
    draw_matrix_rain(draw, 1080, 1080, density=30)

    # Magic runes
    draw_magic_runes(draw, 1080, 1080)

    # Floating wizard hats
    for _ in range(3):
        x = random.randint(100, 980)
        y = random.randint(100, 400)
        draw_pixel_wizard_hat(draw, x, y, size=random.randint(30, 50))

    # Pixelate
    img = pixelate(img, pixel_size=4)

    return img


def generate_cyber_sanctum():
    """Magical cyber sanctum - glowing portal in digital void."""
    img = Image.new('RGB', (1080, 1080), (5, 0, 20))
    draw = ImageDraw.Draw(img)

    # Draw concentric magic circles (portal effect)
    center = (540, 540)
    for radius in range(400, 50, -30):
        color_intensity = (400 - radius) // 4
        color = (
            min(255, color_intensity + 50),
            min(255, color_intensity * 2),
            min(255, 100 + color_intensity)
        )
        # Draw pixelated circle
        for angle in range(0, 360, 3):
            import math
            x = center[0] + int(radius * math.cos(math.radians(angle)))
            y = center[1] + int(radius * math.sin(math.radians(angle)))
            draw.rectangle([x, y, x+4, y+4], fill=color)

    # Matrix rain around edges
    draw_matrix_rain(draw, 1080, 1080, density=25)

    # Magic particles
    draw_pixel_stars(draw, 1080, 1080, count=80)

    # Pixelate
    img = pixelate(img, pixel_size=3)

    return img


def generate_neon_spellbook():
    """Neon magical spellbook aesthetic."""
    img = Image.new('RGB', (1080, 1080), (10, 5, 25))
    draw = ImageDraw.Draw(img)

    # Horizontal scan lines (CRT effect)
    for y in range(0, 1080, 4):
        alpha = random.randint(5, 15)
        draw.line([(0, y), (1080, y)], fill=(alpha, alpha + 10, alpha))

    # Glowing grid lines (like Tron)
    grid_color = (0, 100, 50)
    for x in range(0, 1080, 60):
        draw.line([(x, 0), (x, 1080)], fill=grid_color, width=1)
    for y in range(0, 1080, 60):
        draw.line([(0, y), (1080, y)], fill=grid_color, width=1)

    # Matrix rain
    draw_matrix_rain(draw, 1080, 1080, density=20)

    # Magic runes floating
    draw_magic_runes(draw, 1080, 1080)

    # Bright pixel stars
    draw_pixel_stars(draw, 1080, 1080, count=60)

    # Wizard hats
    for _ in range(2):
        x = random.randint(200, 880)
        y = random.randint(150, 350)
        draw_pixel_wizard_hat(draw, x, y, size=random.randint(40, 60))

    # Pixelate
    img = pixelate(img, pixel_size=4)

    return img


def main():
    print("=" * 60)
    print("🧙 WIZARD MATRIX BACKGROUND GENERATOR")
    print("   Pixel Art • Fantasy • Cyberpunk")
    print("=" * 60)

    generators = [
        ("wizard_matrix_void", generate_matrix_void),
        ("wizard_matrix_realm", generate_wizard_matrix),
        ("wizard_cyber_sanctum", generate_cyber_sanctum),
        ("wizard_neon_spellbook", generate_neon_spellbook),
    ]

    for name, gen_func in generators:
        print(f"🧙 Generating: {name}...")
        img = gen_func()
        path = OUTPUT_DIR / f"{name}.png"
        img.save(path, quality=95)
        print(f"✅ Saved: {path.name}")

    print()
    print("=" * 60)
    print(f"🎉 Generated {len(generators)} wizard matrix backgrounds")
    print(f"📁 Location: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
