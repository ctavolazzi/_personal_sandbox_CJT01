"""
QuoteCard - AI-Powered Quote Graphics Generator
===============================================
Generate beautiful, themed quote cards for social media.

Hybrid approach:
- AI generates backgrounds (Gemini)
- Pillow renders text (reliable)

Can be used as:
- CLI tool: quotecard "Your quote" --author "Author" --theme lofi
- MCP server: Expose to AI assistants
- Python module: from quotecard import generate_card
"""

import os
import json
import random
import textwrap
from pathlib import Path
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, asdict

# ============================================================
# CONFIGURATION
# ============================================================
@dataclass
class QuoteCardConfig:
    """Configuration for QuoteCard generator."""
    output_dir: Path = Path.home() / "Desktop" / "QuoteCards"
    brand: str = "@YourBrand"
    default_theme: str = "minimal"
    image_size: tuple = (1080, 1080)
    quality: int = 95


# Global config - can be overridden
CONFIG = QuoteCardConfig()


# ============================================================
# THEMES - The secret sauce
# ============================================================
THEMES = {
    "minimal": {
        "name": "Minimal",
        "emoji": "⬜",
        "text_color": "#ffffff",
        "text_shadow": "#000000",
        "author_color": "#cccccc",
        "bg_prompt": """Clean minimal background:
            Soft gradient from dark gray to black.
            Subtle texture or grain.
            Professional and elegant.
            NO TEXT.""",
    },
    "wizard_matrix": {
        "name": "Wizard Matrix",
        "emoji": "🧙",
        "text_color": "#00ff41",
        "text_shadow": "#000000",
        "author_color": "#b967ff",
        "bg_prompt": """16-bit pixel art background:
            Dark void with falling green Matrix code.
            Purple magical mist, wizard silhouette in distance.
            SNES RPG aesthetic. NO TEXT.""",
    },
    "vaporwave": {
        "name": "Vaporwave",
        "emoji": "🌴",
        "text_color": "#ff71ce",
        "text_shadow": "#01cdfe",
        "author_color": "#fffb96",
        "bg_prompt": """Vaporwave aesthetic background:
            Pink/cyan gradient sunset with geometric grid.
            Palm trees or Greek statue silhouettes.
            80s synthwave mood. NO TEXT.""",
    },
    "cyberpunk": {
        "name": "Cyberpunk",
        "emoji": "🌃",
        "text_color": "#00f0ff",
        "text_shadow": "#ff00aa",
        "author_color": "#ffaa00",
        "bg_prompt": """Cyberpunk cityscape background:
            Rain-soaked neon streets, dark skyscrapers.
            Pink/blue/orange neon glow.
            Blade Runner mood. NO TEXT.""",
    },
    "cottagecore": {
        "name": "Cottagecore",
        "emoji": "🍄",
        "text_color": "#5c4033",
        "text_shadow": "#ffffff",
        "author_color": "#8b7355",
        "bg_prompt": """Soft cottagecore background:
            Forest clearing with dappled sunlight.
            Wildflowers, mushrooms, watercolor style.
            Peaceful and dreamy. NO TEXT.""",
    },
    "dark_academia": {
        "name": "Dark Academia",
        "emoji": "📚",
        "text_color": "#d4af37",
        "text_shadow": "#1a1a1a",
        "author_color": "#8b0000",
        "bg_prompt": """Dark academia background:
            Moody library with candlelight.
            Old books, deep browns and gold.
            Gothic scholarly atmosphere. NO TEXT.""",
    },
    "lofi": {
        "name": "Lo-Fi Vibes",
        "emoji": "🎧",
        "text_color": "#ffeaa7",
        "text_shadow": "#2d3436",
        "author_color": "#fd79a8",
        "bg_prompt": """Lo-fi study aesthetic background:
            Cozy room, warm lamp, rain on window.
            Plants, soft purple/orange tones.
            Calm anime-inspired style. NO TEXT.""",
    },
    "studio_ghibli": {
        "name": "Studio Ghibli",
        "emoji": "✨",
        "text_color": "#ffffff",
        "text_shadow": "#2c5530",
        "author_color": "#ffefd5",
        "bg_prompt": """Studio Ghibli style background:
            Soft watercolor sky, fluffy clouds.
            Green hills, magical atmosphere.
            Warm and whimsical. NO TEXT.""",
    },
    "ocean": {
        "name": "Ocean Calm",
        "emoji": "🌊",
        "text_color": "#ffffff",
        "text_shadow": "#1a3a4a",
        "author_color": "#87ceeb",
        "bg_prompt": """Peaceful ocean background:
            Calm sea at sunset or sunrise.
            Soft blues, pinks, and golds.
            Serene and meditative. NO TEXT.""",
    },
    "space": {
        "name": "Deep Space",
        "emoji": "🚀",
        "text_color": "#ffffff",
        "text_shadow": "#000033",
        "author_color": "#9999ff",
        "bg_prompt": """Deep space background:
            Stars, nebulae, cosmic dust.
            Deep purples, blues, and hints of pink.
            Vast and inspiring. NO TEXT.""",
    },
    "nature": {
        "name": "Nature",
        "emoji": "🌿",
        "text_color": "#ffffff",
        "text_shadow": "#1a3320",
        "author_color": "#90ee90",
        "bg_prompt": """Lush nature background:
            Forest or mountain landscape.
            Rich greens, earth tones.
            Fresh and alive. NO TEXT.""",
    },
    "retro": {
        "name": "Retro Pop",
        "emoji": "📺",
        "text_color": "#ffff00",
        "text_shadow": "#ff0000",
        "author_color": "#00ffff",
        "bg_prompt": """Retro pop art background:
            Bold colors, halftone dots.
            60s/70s poster aesthetic.
            Energetic and fun. NO TEXT.""",
    },
}


# ============================================================
# CORE FUNCTIONS
# ============================================================
def get_gemini_client():
    """Lazy load Gemini client."""
    from google import genai
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set. Add it to .env or environment.")
    return genai.Client(api_key=api_key)


def generate_background(theme_key: str, output_path: Path) -> bool:
    """Generate AI background using Gemini."""
    from google.genai import types

    if theme_key not in THEMES:
        raise ValueError(f"Unknown theme: {theme_key}. Available: {list(THEMES.keys())}")

    theme = THEMES[theme_key]
    client = get_gemini_client()

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[theme["bg_prompt"]],
            config=types.GenerateContentConfig(
                response_modalities=['IMAGE'],
                image_config=types.ImageConfig(aspect_ratio="1:1")
            )
        )

        for part in response.parts:
            if part.inline_data is not None:
                with open(output_path, "wb") as f:
                    f.write(part.inline_data.data)
                return True
        return False

    except Exception as e:
        if "429" in str(e):
            import time
            time.sleep(10)
            return generate_background(theme_key, output_path)
        raise


def overlay_text(
    bg_path: Path,
    quote: str,
    author: str,
    theme_key: str,
    output_path: Path,
    brand: Optional[str] = None
) -> Path:
    """Overlay text on background using Pillow."""
    from PIL import Image, ImageDraw, ImageFont

    theme = THEMES[theme_key]
    brand = brand or CONFIG.brand

    # Load background
    img = Image.open(bg_path).convert("RGBA")
    img = img.resize(CONFIG.image_size, Image.Resampling.LANCZOS)

    # Darken overlay for readability
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 100))
    img = Image.alpha_composite(img, overlay)

    draw = ImageDraw.Draw(img)

    # Try to load a nice font, fallback to default
    def get_font(size):
        font_paths = [
            Path(__file__).parent / "fonts" / "Inter-Bold.ttf",
            Path.home() / "Library/Fonts/Inter-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ]
        for fp in font_paths:
            if fp.exists():
                try:
                    return ImageFont.truetype(str(fp), size)
                except:
                    pass
        return ImageFont.load_default()

    font_quote = get_font(48)
    font_author = get_font(32)
    font_brand = get_font(24)

    # Wrap quote
    wrapped = textwrap.fill(f'"{quote}"', width=35)

    # Calculate positions
    bbox = draw.multiline_textbbox((0, 0), wrapped, font=font_quote)
    text_height = bbox[3] - bbox[1]
    center_x = CONFIG.image_size[0] // 2
    quote_y = (CONFIG.image_size[1] - text_height) // 2 - 40

    # Draw shadow
    shadow = theme.get("text_shadow", "#000000")
    for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
        draw.multiline_text(
            (center_x + offset[0], quote_y + offset[1]),
            wrapped, font=font_quote, fill=shadow,
            anchor="mm", align="center"
        )

    # Draw quote
    draw.multiline_text(
        (center_x, quote_y), wrapped,
        font=font_quote, fill=theme.get("text_color", "#ffffff"),
        anchor="mm", align="center"
    )

    # Draw author
    author_y = quote_y + (text_height // 2) + 60
    draw.text(
        (center_x, author_y), f"— {author}",
        font=font_author, fill=theme.get("author_color", "#cccccc"),
        anchor="mm"
    )

    # Draw brand
    if brand:
        draw.text(
            (center_x, CONFIG.image_size[1] - 60), brand,
            font=font_brand, fill=(255, 255, 255, 150),
            anchor="mm"
        )

    # Save
    img.convert("RGB").save(output_path, quality=CONFIG.quality)
    return output_path


def generate_card(
    quote: str,
    author: str,
    theme: str = "minimal",
    brand: Optional[str] = None,
    output_dir: Optional[Path] = None,
    filename: Optional[str] = None
) -> dict:
    """
    Generate a complete quote card.

    Args:
        quote: The quote text
        author: Attribution
        theme: Theme key (use list_themes() to see options)
        brand: Brand handle (optional)
        output_dir: Where to save (defaults to Desktop/QuoteCards)
        filename: Custom filename (optional)

    Returns:
        dict with path, quote, author, theme, caption
    """
    from dotenv import load_dotenv
    load_dotenv()

    # Setup output
    output_dir = Path(output_dir) if output_dir else CONFIG.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    if not filename:
        slug = quote[:30].replace(' ', '_')
        slug = ''.join(c for c in slug if c.isalnum() or c == '_')
        timestamp = datetime.now().strftime("%H%M%S")
        filename = f"{theme}_{slug}_{timestamp}.jpg"

    # Paths
    temp_bg = output_dir / f"_temp_{timestamp}.png"
    final_path = output_dir / filename

    # Generate background
    generate_background(theme, temp_bg)

    # Overlay text
    overlay_text(temp_bg, quote, author, theme, final_path, brand)

    # Cleanup
    temp_bg.unlink(missing_ok=True)

    # Generate caption
    caption = f'''"{quote}"
— {author}

✨ Made with QuoteCard

#Motivation #Quotes #Inspiration #Mindset
{brand or CONFIG.brand}'''

    # Save caption
    caption_path = final_path.with_suffix('.txt')
    with open(caption_path, 'w') as f:
        f.write(caption)

    return {
        "path": str(final_path),
        "caption_path": str(caption_path),
        "quote": quote,
        "author": author,
        "theme": theme,
        "caption": caption,
    }


def list_themes() -> dict:
    """Return available themes."""
    return {k: {"name": v["name"], "emoji": v["emoji"]} for k, v in THEMES.items()}


def generate_random_card(
    quotes_file: Optional[Path] = None,
    theme: Optional[str] = None,
    **kwargs
) -> dict:
    """Generate a card with a random quote from a JSON file."""

    if quotes_file and Path(quotes_file).exists():
        with open(quotes_file) as f:
            quotes = json.load(f)
        quote_data = random.choice(quotes)
        quote = quote_data.get("text", quote_data.get("quote", ""))
        author = quote_data.get("author", "Unknown")
    else:
        # Fallback quotes
        fallback = [
            ("The best time to plant a tree was 20 years ago. The second best time is now.", "Chinese Proverb"),
            ("Done is better than perfect.", "Sheryl Sandberg"),
            ("Start where you are. Use what you have. Do what you can.", "Arthur Ashe"),
        ]
        quote, author = random.choice(fallback)

    theme = theme or random.choice(list(THEMES.keys()))

    return generate_card(quote, author, theme, **kwargs)


# ============================================================
# CLI
# ============================================================
def cli():
    """Command-line interface."""
    import argparse
    from dotenv import load_dotenv
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="QuoteCard - Generate beautiful quote graphics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  quotecard "Be the change" --author "Gandhi" --theme minimal
  quotecard --random --theme lofi
  quotecard --list-themes
  quotecard --batch 5 --theme vaporwave --quotes quotes.json
        """
    )

    parser.add_argument("quote", nargs="?", help="The quote text")
    parser.add_argument("--author", "-a", default="Unknown", help="Quote author")
    parser.add_argument("--theme", "-t", default="minimal", help="Visual theme")
    parser.add_argument("--brand", "-b", help="Brand handle")
    parser.add_argument("--output", "-o", help="Output directory")
    parser.add_argument("--list-themes", action="store_true", help="List available themes")
    parser.add_argument("--random", "-r", action="store_true", help="Generate with random quote")
    parser.add_argument("--quotes", "-q", help="JSON file with quotes for random selection")
    parser.add_argument("--batch", type=int, help="Generate multiple cards")
    parser.add_argument("--open", action="store_true", help="Open output folder after")

    args = parser.parse_args()

    # List themes
    if args.list_themes:
        print("\n🎨 AVAILABLE THEMES:\n")
        for key, info in list_themes().items():
            print(f"  {info['emoji']} {key:20} - {info['name']}")
        print()
        return

    # Set config
    if args.brand:
        CONFIG.brand = args.brand
    if args.output:
        CONFIG.output_dir = Path(args.output)

    # Generate
    results = []

    if args.batch:
        print(f"🎨 Generating {args.batch} quote cards...")
        for i in range(args.batch):
            print(f"\n[{i+1}/{args.batch}]", end=" ")
            result = generate_random_card(
                quotes_file=args.quotes,
                theme=args.theme if args.theme != "minimal" else None
            )
            results.append(result)
            print(f"✅ {Path(result['path']).name}")

    elif args.random:
        print("🎨 Generating random quote card...")
        result = generate_random_card(quotes_file=args.quotes, theme=args.theme)
        results.append(result)
        print(f"✅ {result['path']}")

    elif args.quote:
        print(f"🎨 Generating quote card...")
        result = generate_card(args.quote, args.author, args.theme)
        results.append(result)
        print(f"✅ {result['path']}")

    else:
        parser.print_help()
        return

    # Summary
    if results:
        print(f"\n📂 Output: {CONFIG.output_dir}")

        if args.open:
            import subprocess
            subprocess.run(["open", str(CONFIG.output_dir)])


if __name__ == "__main__":
    cli()
