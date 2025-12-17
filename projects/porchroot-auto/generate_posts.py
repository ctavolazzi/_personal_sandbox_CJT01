"""
🎨 PORCHROOT POST GENERATOR - QOL Edition
==========================================
- Organized by date and theme
- Descriptive filenames with quote snippets
- Desktop shortcut support
- Manifest file for easy browsing
- Ready-to-post structure

Usage:
    python generate_posts.py --theme vaporwave
    python generate_posts.py --theme cyberpunk --count 3
    python generate_posts.py --list
    python generate_posts.py --open  # Open output folder
"""

import os
import json
import random
import argparse
import re
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from google import genai
from google.genai import types

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SCRIPT_DIR = Path(__file__).parent
DB_FILE = SCRIPT_DIR / "quotes_db.json"
BRAND = os.getenv("BRAND_HANDLE", "@Porchroot")

# Main output on Desktop for easy access
DESKTOP = Path.home() / "Desktop"
OUTPUT_ROOT = DESKTOP / "Porchroot_Posts"

# ============================================================
# 🎨 THEMES
# ============================================================
THEMES = {
    "wizard_matrix": {
        "name": "Wizard Matrix",
        "emoji": "🧙",
        "style": """
            Art style: 16-bit retro pixel art, SNES RPG aesthetic
            Colors: Deep purples, matrix greens (#00ff41), black voids, magical blues
            Elements: Falling green code, digital glitches, wizard robes, magical staves
            Mood: Dark, mysterious, cyber-fantasy fusion
            Text style: Pixel art retro game font, glowing green or gold
        """,
        "scenes": [
            "A wise wizard silhouette against falling Matrix code",
            "An ancient spellbook floating with digital corruption",
            "A wizard's tower with green code spreading up its walls",
            "A mystical portal between fantasy and digital realms",
            "A wizard casting spells that transform into code streams",
        ]
    },
    "vaporwave": {
        "name": "Vaporwave",
        "emoji": "🌴",
        "style": """
            Art style: Vaporwave/synthwave aesthetic, retro 80s/90s
            Colors: Pink (#ff71ce), cyan (#01cdfe), purple (#b967ff), yellow (#fffb96)
            Elements: Greek statues, palm trees, sunsets, geometric grids
            Mood: Nostalgic, dreamy, retro-futuristic
            Text style: Chrome 3D text, serif fonts
        """,
        "scenes": [
            "A Greek bust statue against a pink/purple sunset grid",
            "Palm trees silhouetted against a neon gradient sky",
            "An endless checkered floor leading to a sunset horizon",
        ]
    },
    "cyberpunk": {
        "name": "Cyberpunk",
        "emoji": "🌃",
        "style": """
            Art style: Cyberpunk, neon-noir, Blade Runner aesthetic
            Colors: Electric blue, hot pink, orange neon, dark blacks
            Elements: Rain, neon signs, skyscrapers, holograms
            Mood: Gritty, futuristic, urban dystopia
            Text style: Glowing neon signs, holographic display font
        """,
        "scenes": [
            "Rain-soaked neon streets with towering skyscrapers",
            "A holographic billboard flickering in the night",
            "Neon signs reflecting in puddles on dark streets",
        ]
    },
    "cottagecore": {
        "name": "Cottagecore",
        "emoji": "🍄",
        "style": """
            Art style: Soft, pastoral, watercolor-inspired
            Colors: Soft greens, warm browns, cream, dusty pink
            Elements: Mushrooms, wildflowers, cozy cottages, forests
            Mood: Peaceful, whimsical, nostalgic
            Text style: Handwritten script, soft serif
        """,
        "scenes": [
            "A cozy cottage in a sunlit forest clearing",
            "Mushrooms and wildflowers in a meadow",
            "A fairy garden with tiny doors in tree trunks",
        ]
    },
    "dark_academia": {
        "name": "Dark Academia",
        "emoji": "📚",
        "style": """
            Art style: Moody, classical, vintage library aesthetic
            Colors: Deep browns, burgundy, gold, forest green
            Elements: Old books, candles, Gothic architecture
            Mood: Scholarly, mysterious, romantic
            Text style: Elegant serif fonts, gold embossed
        """,
        "scenes": [
            "An ancient library with towering bookshelves and candlelight",
            "A desk with old books, a candle, and a quill pen",
            "Rain on a window overlooking ivy-covered walls",
        ]
    },
    "lofi": {
        "name": "Lo-Fi Vibes",
        "emoji": "🎧",
        "style": """
            Art style: Lo-fi hip hop aesthetic, cozy anime-inspired
            Colors: Warm purples, soft oranges, night blues
            Elements: Desk setups, rain on windows, plants, coffee
            Mood: Calm, focused, late-night study sessions
            Text style: Soft rounded fonts, handwritten notes
        """,
        "scenes": [
            "A cozy desk by a rainy window at night",
            "A coffee shop corner with soft lamp light",
            "A bedroom study nook with fairy lights",
        ]
    },
    "studio_ghibli": {
        "name": "Studio Ghibli",
        "emoji": "✨",
        "style": """
            Art style: Studio Ghibli anime, hand-painted watercolor
            Colors: Soft pastels, sky blues, lush greens
            Elements: Floating clouds, magical creatures, cozy villages
            Mood: Whimsical, heartwarming, magical realism
            Text style: Soft handwritten, gentle and warm
        """,
        "scenes": [
            "A floating castle among fluffy clouds at sunset",
            "A forest spirit watching from ancient trees",
            "A magical creature flying over flower fields",
        ]
    },
}


def slugify(text: str, max_len: int = 40) -> str:
    """Convert text to a filename-safe slug."""
    # Remove quotes and special chars
    text = re.sub(r'["\'\.\,\!\?\:\;]', '', text)
    # Replace spaces with underscores
    text = re.sub(r'\s+', '_', text.strip())
    # Remove any remaining non-alphanumeric (except underscore)
    text = re.sub(r'[^a-zA-Z0-9_]', '', text)
    # Truncate
    return text[:max_len].rstrip('_')


def load_quotes() -> list:
    with open(DB_FILE, 'r') as f:
        return json.load(f)


def get_output_dir(theme_key: str) -> Path:
    """Get today's output directory for this theme."""
    today = datetime.now().strftime("%Y-%m-%d")
    output_dir = OUTPUT_ROOT / today / theme_key
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def save_manifest(output_dir: Path, posts: list):
    """Save a manifest of generated posts for easy reference."""
    manifest_path = output_dir / "_manifest.md"

    with open(manifest_path, 'w') as f:
        f.write(f"# Posts Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(f"**Theme:** {posts[0]['theme'] if posts else 'N/A'}\n")
        f.write(f"**Count:** {len(posts)}\n\n")
        f.write("---\n\n")

        for post in posts:
            f.write(f"## {post['filename']}\n\n")
            f.write(f"**Quote:** \"{post['quote']}\"\n\n")
            f.write(f"**Author:** {post['author']}\n\n")
            f.write(f"**Caption (copy-paste ready):**\n\n")
            f.write(f"```\n{post['caption']}\n```\n\n")
            f.write("---\n\n")

    print(f"   📋 Manifest: _manifest.md")


def generate_caption(quote: str, author: str, theme_name: str) -> str:
    """Generate a ready-to-post caption."""
    return f'''"{quote}"
— {author}

✨ {theme_name} vibes for your feed.

#Motivation #QuotesDaily #Inspiration #Mindset #Growth
{BRAND}'''


def generate_post(quote: dict, theme: dict, theme_key: str, output_dir: Path) -> dict | None:
    """Generate a single post with descriptive filename."""

    quote_text = quote['text']
    author = quote['author']
    scene = random.choice(theme['scenes'])

    # Create descriptive filename
    quote_slug = slugify(quote_text)
    filename = f"{theme_key}_{quote_slug}.png"

    prompt = f"""Create a quote image:

THEME: {theme['name']}
STYLE: {theme['style']}
SCENE: {scene}

QUOTE (render this text clearly and prominently):
"{quote_text}"
— {author}

Include "{BRAND}" as a subtle watermark at bottom.

The quote text MUST be clearly readable and styled to match the theme.
Make it look like a shareable motivational social media post.
"""

    print(f"\n{theme['emoji']} Generating: {quote_text[:40]}...")

    output_path = output_dir / filename

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_modalities=['IMAGE'],
                image_config=types.ImageConfig(aspect_ratio="1:1")
            )
        )

        for part in response.parts:
            if part.inline_data is not None:
                image_data = part.inline_data.data
                mime_type = part.inline_data.mime_type
                ext = ".png" if "png" in mime_type else ".jpg"
                final_path = output_path.with_suffix(ext)

                with open(final_path, "wb") as f:
                    f.write(image_data)

                # Also save caption as .txt
                caption = generate_caption(quote_text, author, theme['name'])
                caption_path = final_path.with_suffix('.txt')
                with open(caption_path, 'w') as f:
                    f.write(caption)

                from PIL import Image as PILImage
                with PILImage.open(final_path) as img:
                    print(f"   ✅ {final_path.name} ({img.size[0]}x{img.size[1]})")

                return {
                    "filename": final_path.name,
                    "path": str(final_path),
                    "quote": quote_text,
                    "author": author,
                    "theme": theme['name'],
                    "caption": caption,
                }

        print(f"   ❌ No image returned")
        return None

    except Exception as e:
        if "429" in str(e):
            print(f"   ⏳ Rate limited, waiting...")
            import time
            time.sleep(10)
            return generate_post(quote, theme, theme_key, output_dir)
        print(f"   ❌ Error: {e}")
        return None


def create_desktop_shortcut():
    """Create/update alias on Desktop pointing to output folder."""
    # The folder itself is on Desktop, so just ensure it exists
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    print(f"📂 Output folder: {OUTPUT_ROOT}")


def main():
    parser = argparse.ArgumentParser(description="Generate themed quote posts")
    parser.add_argument("--theme", type=str, default="wizard_matrix")
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--list", action="store_true", help="List themes")
    parser.add_argument("--open", action="store_true", help="Open output folder")
    args = parser.parse_args()

    if args.list:
        print("\n🎨 AVAILABLE THEMES:\n")
        for key, t in THEMES.items():
            print(f"  {t['emoji']} {key:20} - {t['name']}")
        print(f"\n📂 Output saves to: {OUTPUT_ROOT}")
        return

    if args.open:
        import subprocess
        subprocess.run(["open", str(OUTPUT_ROOT)])
        print(f"📂 Opened: {OUTPUT_ROOT}")
        return

    if args.theme not in THEMES:
        print(f"❌ Unknown theme: {args.theme}")
        print(f"   Use --list to see available themes")
        return

    theme = THEMES[args.theme]
    create_desktop_shortcut()
    output_dir = get_output_dir(args.theme)

    print("=" * 60)
    print(f"{theme['emoji']} PORCHROOT POST GENERATOR")
    print(f"   Theme: {theme['name']}")
    print(f"   Output: {output_dir}")
    print("=" * 60)

    quotes = load_quotes()
    selected = random.sample(quotes, min(args.count, len(quotes)))

    posts = []
    for quote in selected:
        result = generate_post(quote, theme, args.theme, output_dir)
        if result:
            posts.append(result)

    if posts:
        save_manifest(output_dir, posts)

    print()
    print("=" * 60)
    print(f"🎉 Generated {len(posts)}/{args.count} posts")
    print(f"📂 Location: {output_dir}")
    print()
    print("📋 Each post has:")
    print("   • Image file (descriptive name)")
    print("   • Caption file (.txt) ready to copy-paste")
    print("   • Manifest (_manifest.md) with all details")
    print("=" * 60)

    # Auto-open folder
    import subprocess
    subprocess.run(["open", str(output_dir)])


if __name__ == "__main__":
    main()
