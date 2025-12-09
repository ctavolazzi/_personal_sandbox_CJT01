"""
Porchroot Auto - Social Media Content Factory
----------------------------------------------
Generates branded quote images with AI-powered captions.

Uses:
- Pillow for reliable text rendering (no AI text-in-image issues)
- GeminiClient from api-testing-framework for caption generation
- .env for secure API key storage

Usage:
    python factory.py              # Generate one post
    python factory.py --batch 5    # Generate 5 posts
"""

import os
import sys
import json
import random
import textwrap
import argparse
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

# Add parent directory to path so we can import from api-testing-framework
sys.path.insert(0, str(Path(__file__).parent.parent / "api-testing-framework"))

from gemini_client import GeminiClient
from config import api_config

# --- SETUP ---
load_dotenv()

BRAND_HANDLE = os.getenv("BRAND_HANDLE", "@YourBrand")
BRAND_WEBSITE = os.getenv("BRAND_WEBSITE", "")

# Paths relative to this script
SCRIPT_DIR = Path(__file__).parent
ASSET_DIR = SCRIPT_DIR / "assets"
OUT_DIR = SCRIPT_DIR / "output"
DB_FILE = SCRIPT_DIR / "quotes_db.json"
HISTORY_FILE = SCRIPT_DIR / "used_quotes.txt"

# Ensure output directory exists
OUT_DIR.mkdir(exist_ok=True)


def generate_caption(quote_text: str, author: str) -> str:
    """Use GeminiClient to write a social media caption."""
    # Force LIVE mode for caption generation
    api_config.set_override("gemini", "LIVE")

    client = GeminiClient()

    prompt = (
        f"Write a short, engaging Instagram caption for this quote:\n"
        f'"{quote_text}" - {author}\n\n'
        f"Include:\n"
        f"- A hook (first line that grabs attention)\n"
        f"- A brief 1-2 sentence reflection\n"
        f"- 5 relevant hashtags\n"
        f"- End with {BRAND_HANDLE}\n\n"
        f"Keep it under 50 words total. No emojis in the first line."
    )

    try:
        response = client.generate_text(prompt)
        return response
    except Exception as e:
        return f"Caption generation failed: {e}\n\n{BRAND_HANDLE}"


def create_post(quote_data: dict) -> Image.Image:
    """Generate a branded quote image using Pillow."""

    # A. Select random background (or create solid color)
    bg_dir = ASSET_DIR / "backgrounds"
    try:
        bg_files = [f for f in bg_dir.iterdir() if f.suffix.lower() in ('.jpg', '.png', '.jpeg')]
        if bg_files:
            chosen_bg = random.choice(bg_files)
            img = Image.open(chosen_bg).convert("RGBA")
            img = img.resize((1080, 1080))
        else:
            raise FileNotFoundError("No backgrounds")
    except (FileNotFoundError, StopIteration):
        # Create dark gradient background
        img = Image.new('RGBA', (1080, 1080), (25, 25, 35, 255))

    # B. Add darken overlay for text readability
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 140))
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    # C. Load fonts (or use default)
    font_dir = ASSET_DIR / "fonts"
    try:
        font_files = list(font_dir.glob("*.ttf")) + list(font_dir.glob("*.otf"))
        if font_files:
            font_path = str(font_files[0])
            font_quote = ImageFont.truetype(font_path, 52)
            font_author = ImageFont.truetype(font_path, 36)
            font_brand = ImageFont.truetype(font_path, 28)
        else:
            raise FileNotFoundError("No fonts")
    except (FileNotFoundError, OSError):
        # Use default font (basic but works)
        font_quote = ImageFont.load_default()
        font_author = ImageFont.load_default()
        font_brand = ImageFont.load_default()

    # D. Text wrapping
    quote_text = f'"{quote_data["text"]}"'

    # Calculate characters per line based on image width and font size
    margin = 100
    max_width = 1080 - (margin * 2)
    chars_per_line = 38  # Conservative estimate for readability

    wrapped_quote = textwrap.fill(quote_text, width=chars_per_line)

    # E. Calculate text positioning (centered)
    bbox = draw.multiline_textbbox((0, 0), wrapped_quote, font=font_quote)
    text_height = bbox[3] - bbox[1]

    center_x = 540
    quote_y = (1080 - text_height) // 2 - 60  # Shift up to make room for author

    # F. Draw quote text
    draw.multiline_text(
        (center_x, quote_y),
        wrapped_quote,
        font=font_quote,
        fill="white",
        anchor="mm",
        align="center"
    )

    # G. Draw author
    author_y = quote_y + (text_height // 2) + 80
    draw.text(
        (center_x, author_y),
        f"— {quote_data['author']}",
        font=font_author,
        fill=(255, 215, 0),  # Gold color
        anchor="mm"
    )

    # H. Draw brand watermark
    draw.text(
        (center_x, 1000),
        BRAND_HANDLE,
        font=font_brand,
        fill=(255, 255, 255, 180),
        anchor="mm"
    )

    return img


def load_quotes() -> list:
    """Load quotes from JSON database."""
    if not DB_FILE.exists():
        print(f"⚠️  No quotes database found at {DB_FILE}")
        print("   Creating sample database...")
        create_sample_db()

    with open(DB_FILE, 'r') as f:
        return json.load(f)


def load_history() -> set:
    """Load IDs of already-used quotes."""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r') as f:
            return set(int(line.strip()) for line in f if line.strip())
    return set()


def save_to_history(quote_id: int):
    """Mark a quote as used."""
    with open(HISTORY_FILE, 'a') as f:
        f.write(f"{quote_id}\n")


def create_sample_db():
    """Create a sample quotes database."""
    sample_quotes = [
        {"id": 1, "text": "The best time to plant a tree was 20 years ago. The second best time is now.", "author": "Chinese Proverb"},
        {"id": 2, "text": "Done is better than perfect.", "author": "Sheryl Sandberg"},
        {"id": 3, "text": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
        {"id": 4, "text": "Start where you are. Use what you have. Do what you can.", "author": "Arthur Ashe"},
        {"id": 5, "text": "Small daily improvements over time lead to stunning results.", "author": "Robin Sharma"},
    ]
    with open(DB_FILE, 'w') as f:
        json.dump(sample_quotes, f, indent=2)
    print(f"✅ Created sample database with {len(sample_quotes)} quotes")


def generate_post(quotes: list, used: set) -> dict | None:
    """Generate a single post (image + caption)."""

    # Filter available quotes
    available = [q for q in quotes if q['id'] not in used]

    if not available:
        print("❌ All quotes have been used!")
        print(f"   Delete {HISTORY_FILE} to reset, or add more quotes to {DB_FILE}")
        return None

    # Select random quote
    selected = random.choice(available)
    print(f"📝 Quote #{selected['id']}: \"{selected['text'][:50]}...\"")

    # Generate image
    print("🎨 Generating image...")
    img = create_post(selected)

    # Save image
    filename = f"post_{selected['id']:03d}.jpg"
    img_path = OUT_DIR / filename
    img.convert("RGB").save(img_path, quality=95)
    print(f"✅ Image saved: {filename}")

    # Generate caption
    print("✨ Generating caption with Gemini...")
    caption = generate_caption(selected['text'], selected['author'])

    # Save caption
    caption_path = OUT_DIR / f"post_{selected['id']:03d}_caption.txt"
    with open(caption_path, 'w') as f:
        f.write(caption)
    print(f"✅ Caption saved: {caption_path.name}")

    # Update history
    save_to_history(selected['id'])

    return {
        "quote_id": selected['id'],
        "image_path": str(img_path),
        "caption_path": str(caption_path),
        "caption": caption
    }


def main():
    parser = argparse.ArgumentParser(description="Generate branded quote posts")
    parser.add_argument("--batch", type=int, default=1, help="Number of posts to generate")
    parser.add_argument("--reset", action="store_true", help="Reset quote history")
    args = parser.parse_args()

    print("=" * 60)
    print("🏭 PORCHROOT AUTO - Social Media Content Factory")
    print("=" * 60)

    # Reset history if requested
    if args.reset:
        if HISTORY_FILE.exists():
            HISTORY_FILE.unlink()
            print("🔄 Quote history reset")

    # Load data
    quotes = load_quotes()
    used = load_history()

    print(f"📊 Database: {len(quotes)} quotes, {len(used)} used")
    print(f"📁 Output: {OUT_DIR}")
    print()

    # Generate posts
    results = []
    for i in range(args.batch):
        if args.batch > 1:
            print(f"\n--- Post {i+1}/{args.batch} ---")

        result = generate_post(quotes, used)
        if result:
            results.append(result)
            used.add(result['quote_id'])  # Update local set for batch runs
        else:
            break

    # Summary
    print("\n" + "=" * 60)
    print(f"🎉 COMPLETE: Generated {len(results)} post(s)")
    for r in results:
        print(f"   - {Path(r['image_path']).name}")
    print("=" * 60)


if __name__ == "__main__":
    main()
