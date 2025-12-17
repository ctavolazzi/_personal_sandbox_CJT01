"""
🚀 PORCHROOT PRO - Production-Hardened Post Generator
======================================================
Fixes the holes in our prototype:
✅ Hybrid approach: AI backgrounds + Pillow text (reliable!)
✅ QC workflow: Generated → Review → Approved → Posted
✅ Usage history: No duplicate quotes
✅ Cost tracking: Know your spend
✅ Batch review: Quick approve/reject

Usage:
    python porchroot_pro.py generate --theme lofi --count 5
    python porchroot_pro.py review      # Review pending images
    python porchroot_pro.py stats       # See usage stats
    python porchroot_pro.py --list      # List themes
"""

import os
import json
import random
import argparse
import textwrap
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from google import genai
from google.genai import types
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

# ============================================================
# CONFIG
# ============================================================
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SCRIPT_DIR = Path(__file__).parent
DB_FILE = SCRIPT_DIR / "quotes_db.json"
HISTORY_FILE = SCRIPT_DIR / "quote_history.json"
STATS_FILE = SCRIPT_DIR / "usage_stats.json"
FONT_DIR = SCRIPT_DIR / "assets" / "fonts"

BRAND = os.getenv("BRAND_HANDLE", "@Porchroot")

# Desktop output with QC workflow folders
DESKTOP = Path.home() / "Desktop"
OUTPUT_ROOT = DESKTOP / "Porchroot_Pro"
REVIEW_DIR = OUTPUT_ROOT / "1_Review"
APPROVED_DIR = OUTPUT_ROOT / "2_Approved"
POSTED_DIR = OUTPUT_ROOT / "3_Posted"

# Cost tracking (approximate)
COST_PER_IMAGE = 0.03  # $0.03 per Gemini image generation

# ============================================================
# THEMES (Background generation only - no text!)
# ============================================================
THEMES = {
    "wizard_matrix": {
        "name": "Wizard Matrix",
        "emoji": "🧙",
        "text_color": "#00ff41",
        "text_shadow": "#000000",
        "author_color": "#b967ff",
        "bg_prompt": """16-bit pixel art background scene:
            Dark void with falling green Matrix code characters.
            Purple magical mist and pixel stars scattered throughout.
            A wizard silhouette or magical elements in the distance.
            Style: SNES RPG aesthetic, deep purples and matrix greens.
            NO TEXT - leave space for text overlay.""",
    },
    "vaporwave": {
        "name": "Vaporwave",
        "emoji": "🌴",
        "text_color": "#ff71ce",
        "text_shadow": "#01cdfe",
        "author_color": "#fffb96",
        "bg_prompt": """Vaporwave aesthetic background:
            Pink and cyan gradient sunset sky with geometric grid.
            Palm tree silhouettes or Greek statue elements.
            Retro 80s synthwave mood.
            NO TEXT - leave clean for text overlay.""",
    },
    "cyberpunk": {
        "name": "Cyberpunk",
        "emoji": "🌃",
        "text_color": "#00f0ff",
        "text_shadow": "#ff00aa",
        "author_color": "#ffaa00",
        "bg_prompt": """Cyberpunk cityscape background:
            Rain-soaked neon streets, towering dark skyscrapers.
            Neon signs glowing pink, blue, and orange in the distance.
            Moody Blade Runner atmosphere.
            NO TEXT - leave space for quote overlay.""",
    },
    "cottagecore": {
        "name": "Cottagecore",
        "emoji": "🍄",
        "text_color": "#5c4033",
        "text_shadow": "#ffffff",
        "author_color": "#8b7355",
        "bg_prompt": """Soft cottagecore illustration background:
            Peaceful forest clearing with dappled sunlight.
            Wildflowers, mushrooms, soft greens and warm browns.
            Dreamy watercolor style, gentle and pastoral.
            NO TEXT - clean background for overlay.""",
    },
    "dark_academia": {
        "name": "Dark Academia",
        "emoji": "📚",
        "text_color": "#d4af37",
        "text_shadow": "#1a1a1a",
        "author_color": "#8b0000",
        "bg_prompt": """Dark academia aesthetic background:
            Moody library with candlelight, old bookshelves.
            Deep browns, burgundy, and gold tones.
            Gothic scholarly atmosphere, vintage and mysterious.
            NO TEXT - leave clean for quote overlay.""",
    },
    "lofi": {
        "name": "Lo-Fi Vibes",
        "emoji": "🎧",
        "text_color": "#ffeaa7",
        "text_shadow": "#2d3436",
        "author_color": "#fd79a8",
        "bg_prompt": """Lo-fi study aesthetic background:
            Cozy room with warm lamp light, rain on window.
            Plants, coffee cup, soft purple and orange tones.
            Calm anime-inspired illustration style.
            NO TEXT - background only for overlay.""",
    },
    "studio_ghibli": {
        "name": "Studio Ghibli",
        "emoji": "✨",
        "text_color": "#ffffff",
        "text_shadow": "#2c5530",
        "author_color": "#ffefd5",
        "bg_prompt": """Studio Ghibli style background:
            Soft watercolor sky with fluffy clouds at sunset.
            Lush green hills, magical atmosphere.
            Hand-painted anime aesthetic, warm and whimsical.
            NO TEXT - clean for quote overlay.""",
    },
}


# ============================================================
# UTILITIES
# ============================================================
def load_json(path: Path, default=None):
    if path.exists():
        with open(path, 'r') as f:
            return json.load(f)
    return default if default is not None else {}


def save_json(path: Path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def load_quotes() -> list:
    return load_json(DB_FILE, [])


def get_used_quotes() -> set:
    history = load_json(HISTORY_FILE, {"used": []})
    return set(history.get("used", []))


def mark_quote_used(quote_id: int):
    history = load_json(HISTORY_FILE, {"used": []})
    if quote_id not in history["used"]:
        history["used"].append(quote_id)
    save_json(HISTORY_FILE, history)


def track_generation(theme: str, cost: float):
    stats = load_json(STATS_FILE, {
        "total_generated": 0,
        "total_cost": 0.0,
        "by_theme": {},
        "history": []
    })
    stats["total_generated"] += 1
    stats["total_cost"] += cost
    stats["by_theme"][theme] = stats["by_theme"].get(theme, 0) + 1
    stats["history"].append({
        "date": datetime.now().isoformat(),
        "theme": theme,
        "cost": cost
    })
    save_json(STATS_FILE, stats)


def setup_folders():
    """Create QC workflow folders."""
    for folder in [REVIEW_DIR, APPROVED_DIR, POSTED_DIR]:
        folder.mkdir(parents=True, exist_ok=True)


def get_font(size: int) -> ImageFont.FreeTypeFont:
    """Load Inter font or fallback."""
    try:
        font_files = list(FONT_DIR.glob("*.ttf"))
        if font_files:
            # Prefer Bold for quotes
            bold = [f for f in font_files if "Bold" in f.name]
            font_path = bold[0] if bold else font_files[0]
            return ImageFont.truetype(str(font_path), size)
    except:
        pass
    return ImageFont.load_default()


# ============================================================
# CORE GENERATION (Hybrid: AI background + Pillow text)
# ============================================================
def generate_background(theme: dict, output_path: Path) -> bool:
    """Generate JUST the background with Gemini (no text)."""

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
            print("   ⏳ Rate limited, waiting 10s...")
            time.sleep(10)
            return generate_background(theme, output_path)
        print(f"   ❌ Error: {e}")
        return False


def overlay_text(bg_path: Path, quote: str, author: str, theme: dict, output_path: Path):
    """Overlay quote text using Pillow (reliable text rendering!)."""

    # Load and prepare background
    img = Image.open(bg_path).convert("RGBA")
    img = img.resize((1080, 1080), Image.Resampling.LANCZOS)

    # Add slight darken overlay for text readability
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 100))
    img = Image.alpha_composite(img, overlay)

    draw = ImageDraw.Draw(img)

    # Fonts
    font_quote = get_font(48)
    font_author = get_font(32)
    font_brand = get_font(24)

    # Wrap quote text
    wrapped = textwrap.fill(f'"{quote}"', width=35)

    # Calculate positions
    bbox = draw.multiline_textbbox((0, 0), wrapped, font=font_quote)
    text_height = bbox[3] - bbox[1]
    center_x = 540
    quote_y = (1080 - text_height) // 2 - 40

    # Draw shadow
    shadow_color = theme.get("text_shadow", "#000000")
    for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
        draw.multiline_text(
            (center_x + offset[0], quote_y + offset[1]),
            wrapped, font=font_quote, fill=shadow_color,
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
    draw.text(
        (center_x, 1020), BRAND,
        font=font_brand, fill=(255, 255, 255, 150),
        anchor="mm"
    )

    # Save
    img.convert("RGB").save(output_path, quality=95)


def generate_post(quote: dict, theme_key: str, theme: dict) -> dict | None:
    """Generate a complete post (background + text overlay)."""

    setup_folders()

    # Create temp background
    temp_bg = REVIEW_DIR / f"_temp_bg_{quote['id']}.png"

    print(f"\n{theme['emoji']} Generating background...")
    if not generate_background(theme, temp_bg):
        return None

    # Create final filename
    quote_snippet = quote['text'][:30].replace(' ', '_').replace('"', '')
    quote_snippet = ''.join(c for c in quote_snippet if c.isalnum() or c == '_')
    filename = f"{theme_key}_{quote['id']:03d}_{quote_snippet}.jpg"
    final_path = REVIEW_DIR / filename

    print(f"   📝 Adding text overlay...")
    overlay_text(temp_bg, quote['text'], quote['author'], theme, final_path)

    # Cleanup temp
    temp_bg.unlink(missing_ok=True)

    # Save caption
    caption = f'''"{quote['text']}"
— {quote['author']}

✨ {theme['name']} vibes

#Motivation #Quotes #Inspiration #Mindset #DailyWisdom
{BRAND}'''

    caption_path = final_path.with_suffix('.txt')
    with open(caption_path, 'w') as f:
        f.write(caption)

    # Track stats
    track_generation(theme_key, COST_PER_IMAGE)
    mark_quote_used(quote['id'])

    print(f"   ✅ {filename}")

    return {
        "path": str(final_path),
        "quote_id": quote['id'],
        "theme": theme_key
    }


# ============================================================
# COMMANDS
# ============================================================
def cmd_generate(args):
    """Generate new posts."""
    if args.theme not in THEMES:
        print(f"❌ Unknown theme: {args.theme}")
        return

    theme = THEMES[args.theme]
    quotes = load_quotes()
    used = get_used_quotes()

    # Filter available quotes
    available = [q for q in quotes if q['id'] not in used]

    if not available:
        print("❌ All quotes used! Reset with: python porchroot_pro.py reset")
        return

    count = min(args.count, len(available))
    selected = random.sample(available, count)

    print("=" * 60)
    print(f"{theme['emoji']} PORCHROOT PRO - Generating {count} posts")
    print(f"   Theme: {theme['name']}")
    print(f"   Available quotes: {len(available)}")
    print("=" * 60)

    success = 0
    for quote in selected:
        if generate_post(quote, args.theme, theme):
            success += 1

    print()
    print("=" * 60)
    print(f"🎉 Generated {success}/{count} posts")
    print(f"📂 Review folder: {REVIEW_DIR}")
    print()
    print("Next: python porchroot_pro.py review")
    print("=" * 60)

    # Open review folder
    import subprocess
    subprocess.run(["open", str(REVIEW_DIR)])


def cmd_review(args):
    """Open review folder and show pending count."""
    setup_folders()

    review_files = list(REVIEW_DIR.glob("*.jpg"))
    approved_files = list(APPROVED_DIR.glob("*.jpg"))
    posted_files = list(POSTED_DIR.glob("*.jpg"))

    print("=" * 60)
    print("📋 PORCHROOT PRO - Content Pipeline")
    print("=" * 60)
    print(f"   🔍 Review:   {len(review_files)} posts pending")
    print(f"   ✅ Approved: {len(approved_files)} ready to post")
    print(f"   📤 Posted:   {len(posted_files)} completed")
    print("=" * 60)
    print()
    print("Workflow:")
    print("  1. Review images in '1_Review' folder")
    print("  2. Move good ones to '2_Approved'")
    print("  3. After posting, move to '3_Posted'")
    print()
    print(f"📂 Opening: {OUTPUT_ROOT}")

    import subprocess
    subprocess.run(["open", str(OUTPUT_ROOT)])


def cmd_stats(args):
    """Show usage statistics."""
    stats = load_json(STATS_FILE, {
        "total_generated": 0,
        "total_cost": 0.0,
        "by_theme": {}
    })

    quotes = load_quotes()
    used = get_used_quotes()

    print("=" * 60)
    print("📊 PORCHROOT PRO - Usage Statistics")
    print("=" * 60)
    print(f"   Total generated: {stats['total_generated']} images")
    print(f"   Estimated cost:  ${stats['total_cost']:.2f}")
    print(f"   Quotes used:     {len(used)}/{len(quotes)}")
    print()
    print("By theme:")
    for theme, count in stats.get("by_theme", {}).items():
        emoji = THEMES.get(theme, {}).get("emoji", "🎨")
        print(f"   {emoji} {theme}: {count}")
    print("=" * 60)


def cmd_reset(args):
    """Reset quote history."""
    if HISTORY_FILE.exists():
        HISTORY_FILE.unlink()
    print("✅ Quote history reset - all quotes available again")


def cmd_list(args):
    """List available themes."""
    print("\n🎨 AVAILABLE THEMES:\n")
    for key, t in THEMES.items():
        print(f"  {t['emoji']} {key:20} - {t['name']}")
    print()
    print("Usage: python porchroot_pro.py generate --theme lofi --count 5")


# ============================================================
# MAIN
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="Porchroot Pro - Production Post Generator")
    subparsers = parser.add_subparsers(dest="command")

    # generate
    gen_parser = subparsers.add_parser("generate", help="Generate new posts")
    gen_parser.add_argument("--theme", type=str, default="wizard_matrix")
    gen_parser.add_argument("--count", type=int, default=5)

    # review
    subparsers.add_parser("review", help="Open review workflow")

    # stats
    subparsers.add_parser("stats", help="Show usage statistics")

    # reset
    subparsers.add_parser("reset", help="Reset quote history")

    # list
    parser.add_argument("--list", action="store_true", help="List themes")

    args = parser.parse_args()

    if args.list:
        cmd_list(args)
    elif args.command == "generate":
        cmd_generate(args)
    elif args.command == "review":
        cmd_review(args)
    elif args.command == "stats":
        cmd_stats(args)
    elif args.command == "reset":
        cmd_reset(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
