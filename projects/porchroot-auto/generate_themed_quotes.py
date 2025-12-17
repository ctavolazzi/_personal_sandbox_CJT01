"""
Generate Themed Quote Images - Mad Lib Style Theme Swapping
Easily swap between different visual themes.

Usage:
    python generate_themed_quotes.py                    # Uses default theme
    python generate_themed_quotes.py --theme vaporwave  # Use specific theme
    python generate_themed_quotes.py --list             # List available themes
"""

import os
import json
import random
import argparse
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from google import genai
from google.genai import types

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "output" / "themed_quotes"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DB_FILE = SCRIPT_DIR / "quotes_db.json"

BRAND = "@Porchroot"

# ============================================================
# 🎨 THEMES - Mad Lib Style! Add new themes here easily
# ============================================================
THEMES = {
    "wizard_matrix": {
        "name": "Wizard Matrix",
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
        "name": "Vaporwave Aesthetic",
        "style": """
            Art style: Vaporwave/synthwave aesthetic, retro 80s/90s
            Colors: Pink (#ff71ce), cyan (#01cdfe), purple (#b967ff), yellow (#fffb96)
            Elements: Greek statues, palm trees, sunsets, geometric grids, retro computers
            Mood: Nostalgic, dreamy, retro-futuristic
            Text style: Chrome 3D text, Japanese characters optional, serif fonts
        """,
        "scenes": [
            "A Greek bust statue against a pink/purple sunset grid",
            "Palm trees silhouetted against a neon gradient sky",
            "A retro computer floating in a geometric void",
            "An endless checkered floor leading to a sunset horizon",
            "A Roman column surrounded by floating geometric shapes",
        ]
    },

    "cyberpunk": {
        "name": "Cyberpunk City",
        "style": """
            Art style: Cyberpunk, neon-noir, Blade Runner aesthetic
            Colors: Electric blue, hot pink, orange neon, dark blacks
            Elements: Rain, neon signs, skyscrapers, holograms, flying cars
            Mood: Gritty, futuristic, urban dystopia
            Text style: Glowing neon signs, holographic display font
        """,
        "scenes": [
            "Rain-soaked neon streets with towering skyscrapers",
            "A holographic billboard flickering in the night",
            "A cyborg silhouette against a city skyline",
            "Neon signs reflecting in puddles on dark streets",
            "A rooftop view of a sprawling mega-city at night",
        ]
    },

    "cottagecore": {
        "name": "Cottagecore Dreams",
        "style": """
            Art style: Soft, pastoral, watercolor-inspired illustration
            Colors: Soft greens, warm browns, cream, dusty pink, lavender
            Elements: Mushrooms, wildflowers, cozy cottages, forests, tea cups
            Mood: Peaceful, whimsical, nostalgic, nature-loving
            Text style: Handwritten script, soft serif, botanical illustration labels
        """,
        "scenes": [
            "A cozy cottage in a sunlit forest clearing",
            "Mushrooms and wildflowers in a meadow",
            "A window seat with books and a cup of tea",
            "A fairy garden with tiny doors in tree trunks",
            "A picnic blanket in a field of wildflowers",
        ]
    },

    "dark_academia": {
        "name": "Dark Academia",
        "style": """
            Art style: Moody, classical, vintage library aesthetic
            Colors: Deep browns, burgundy, gold, forest green, cream
            Elements: Old books, candles, Gothic architecture, autumn leaves, quills
            Mood: Scholarly, mysterious, romantic, melancholic
            Text style: Elegant serif fonts, gold embossed, vintage typography
        """,
        "scenes": [
            "An ancient library with towering bookshelves and candlelight",
            "A Gothic university building shrouded in autumn mist",
            "A desk with old books, a candle, and a quill pen",
            "Rain on a window overlooking ivy-covered walls",
            "A secret study with maps and mysterious artifacts",
        ]
    },

    "studio_ghibli": {
        "name": "Studio Ghibli Style",
        "style": """
            Art style: Studio Ghibli anime, hand-painted watercolor
            Colors: Soft pastels, sky blues, lush greens, warm sunset oranges
            Elements: Floating clouds, magical creatures, cozy villages, nature spirits
            Mood: Whimsical, heartwarming, magical realism
            Text style: Soft handwritten Japanese-inspired, gentle and warm
        """,
        "scenes": [
            "A floating castle among fluffy clouds at sunset",
            "A forest spirit watching from ancient trees",
            "A cozy hillside village with a gentle breeze",
            "A magical creature flying over flower fields",
            "A peaceful lakeside scene with mountains in distance",
        ]
    },

    "retro_scifi": {
        "name": "Retro Sci-Fi Pulp",
        "style": """
            Art style: 1950s pulp sci-fi magazine covers
            Colors: Bold reds, atomic orange, space black, silver chrome
            Elements: Rockets, ray guns, aliens, planets, astronauts, robots
            Mood: Adventurous, optimistic, atomic age wonder
            Text style: Bold pulp magazine fonts, chrome effects, dramatic
        """,
        "scenes": [
            "A sleek rocket ship landing on a colorful alien planet",
            "An astronaut gazing at a ringed planet on the horizon",
            "A retro robot extending a helpful mechanical hand",
            "A space station orbiting a red alien world",
            "A ray gun duel on a futuristic moonbase",
        ]
    },

    "lofi": {
        "name": "Lo-Fi Study Vibes",
        "style": """
            Art style: Lo-fi hip hop aesthetic, cozy anime-inspired
            Colors: Warm purples, soft oranges, night blues, warm lamp yellows
            Elements: Desk setups, rain on windows, plants, headphones, coffee
            Mood: Calm, focused, late-night study sessions
            Text style: Soft rounded fonts, handwritten notes style
        """,
        "scenes": [
            "A cozy desk by a rainy window at night",
            "A person with headphones studying among plants",
            "A coffee shop corner with soft lamp light",
            "A bedroom study nook with fairy lights",
            "A rooftop view of city lights at dusk",
        ]
    },
}


def load_quotes() -> list:
    with open(DB_FILE, 'r') as f:
        return json.load(f)


def generate_themed_quote(quote: dict, theme: dict, scene: str, index: int, theme_key: str) -> bool:
    """Generate a quote image with the selected theme."""

    quote_text = quote['text']
    author = quote['author']

    prompt = f"""Create a quote image in this specific style:

THEME: {theme['name']}

STYLE REQUIREMENTS:
{theme['style']}

SCENE: {scene}

QUOTE TEXT TO DISPLAY (render clearly and prominently):
"{quote_text}"
— {author}

BRAND: Include "{BRAND}" as a subtle watermark at the bottom

CRITICAL:
- The quote text MUST be clearly readable
- Style the text to match the theme aesthetic
- The quote is the focal point, scene is the backdrop
- Make it look like a shareable motivational image
"""

    print(f"\n🎨 Generating {theme['name']} quote {index}...")
    print(f"   Quote: \"{quote_text[:45]}...\"")

    output_path = OUTPUT_DIR / f"{theme_key}_{quote['id']:03d}.png"

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_modalities=['IMAGE'],
                image_config=types.ImageConfig(
                    aspect_ratio="1:1",
                )
            )
        )

        for part in response.parts:
            if part.text is not None:
                print(f"   📝 Note: {part.text[:50]}...")
            elif part.inline_data is not None:
                image_data = part.inline_data.data
                mime_type = part.inline_data.mime_type
                ext = ".png" if "png" in mime_type else ".jpg"
                final_path = output_path.with_suffix(ext)

                with open(final_path, "wb") as f:
                    f.write(image_data)

                from PIL import Image as PILImage
                with PILImage.open(final_path) as img:
                    print(f"   ✅ Saved: {final_path.name} ({img.size[0]}x{img.size[1]})")
                return True

        print(f"   ❌ No image in response")
        return False

    except Exception as e:
        if "429" in str(e):
            print(f"   ⚠️  Rate limited - waiting...")
            import time
            time.sleep(10)
            return generate_themed_quote(quote, theme, scene, index, theme_key)
        print(f"   ❌ Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Generate themed quote images")
    parser.add_argument("--theme", type=str, default="wizard_matrix",
                        help=f"Theme to use: {', '.join(THEMES.keys())}")
    parser.add_argument("--list", action="store_true", help="List available themes")
    parser.add_argument("--count", type=int, default=5, help="Number of quotes to generate")
    args = parser.parse_args()

    if args.list:
        print("\n🎨 AVAILABLE THEMES:\n")
        for key, theme in THEMES.items():
            print(f"  {key:20} - {theme['name']}")
        print(f"\nUsage: python generate_themed_quotes.py --theme {list(THEMES.keys())[1]}")
        return

    if args.theme not in THEMES:
        print(f"❌ Unknown theme: {args.theme}")
        print(f"   Available: {', '.join(THEMES.keys())}")
        return

    theme = THEMES[args.theme]

    print("=" * 60)
    print(f"🎨 THEMED QUOTE GENERATOR")
    print(f"   Theme: {theme['name']}")
    print("=" * 60)

    quotes = load_quotes()
    num_to_generate = min(args.count, len(quotes))
    selected_quotes = random.sample(quotes, num_to_generate)

    print(f"📁 Output: {OUTPUT_DIR}")
    print(f"📝 Quotes: {num_to_generate}")
    print("=" * 60)

    success = 0
    for i, quote in enumerate(selected_quotes, 1):
        scene = random.choice(theme['scenes'])
        if generate_themed_quote(quote, theme, scene, i, args.theme):
            success += 1

    print()
    print("=" * 60)
    print(f"🎉 Generated {success}/{num_to_generate} {theme['name']} quotes")
    print(f"📁 Location: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
