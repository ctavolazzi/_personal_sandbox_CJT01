"""
Generate Wizard Quote Images with Text Baked In
Gemini renders the quote text directly in pixel art style.

Usage:
    python generate_wizard_quote_images.py
"""

import os
import json
import random
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from google import genai
from google.genai import types

# Configure client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "output" / "wizard_quotes"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DB_FILE = SCRIPT_DIR / "quotes_db.json"

BRAND = "@Porchroot"

# Style guide for consistent wizard aesthetic
STYLE_GUIDE = """
STRICT STYLE REQUIREMENTS:
- Art style: 16-bit retro pixel art, like classic SNES RPG games
- Color palette: Deep purples, matrix greens (#00ff41), black voids, magical blues
- Matrix elements: Falling green code, digital glitches, scan lines
- Fantasy elements: Wizard imagery, magical energy, mystical atmosphere
- The quote text should be rendered in a stylized pixel art font
- Text should be clearly readable but feel part of the artwork
- Author attribution below the quote in smaller text
- Brand watermark "@Porchroot" subtle at bottom
- Dark moody background with magical/digital effects
"""

# Different scene templates for variety
SCENE_TEMPLATES = [
    "A wise wizard silhouette against falling Matrix code, contemplating the quote",
    "An ancient spellbook floating open with magical energy surrounding it",
    "A wizard's tower at night with green digital corruption spreading",
    "A mystical portal between fantasy and digital realms",
    "A wizard casting a spell that transforms into streams of code",
    "An enchanted forest path with glitching trees and floating runes",
]


def load_quotes() -> list:
    """Load quotes from JSON database."""
    with open(DB_FILE, 'r') as f:
        return json.load(f)


def generate_wizard_quote(quote: dict, scene: str, index: int) -> bool:
    """Generate a wizard meme with quote text baked in."""

    quote_text = quote['text']
    author = quote['author']

    prompt = f"""Create a 16-bit pixel art quote image:

SCENE: {scene}

QUOTE TEXT TO DISPLAY (render this text clearly in the image):
"{quote_text}"
— {author}

BRAND: Include "{BRAND}" as a small watermark at the bottom

{STYLE_GUIDE}

IMPORTANT:
- The quote text MUST be readable and prominent in the image
- Style the text to look like pixel art / retro game font
- The quote should be the focal point, with the wizard scene as backdrop
- Make it look like a shareable motivational meme with fantasy/cyber aesthetic
"""

    print(f"\n🧙 Generating wizard quote {index}...")
    print(f"   Quote: \"{quote_text[:50]}...\"")
    print(f"   Scene: {scene[:40]}...")

    output_path = OUTPUT_DIR / f"wizard_quote_{quote['id']:03d}.png"

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

        # Process response
        for part in response.parts:
            if part.text is not None:
                print(f"   📝 Note: {part.text[:60]}...")
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
        error_str = str(e)
        if "429" in error_str:
            print(f"   ⚠️  Rate limited - waiting 10s...")
            import time
            time.sleep(10)
            return generate_wizard_quote(quote, scene, index)
        else:
            print(f"   ❌ Error: {e}")
        return False


def main():
    print("=" * 60)
    print("🧙 WIZARD QUOTE MEMES - TEXT BAKED IN BY GEMINI")
    print("   Pixel Art • Matrix Corruption • Quotes Rendered")
    print("=" * 60)

    quotes = load_quotes()

    # Select random quotes to generate
    num_to_generate = min(5, len(quotes))
    selected_quotes = random.sample(quotes, num_to_generate)

    print(f"📁 Output: {OUTPUT_DIR}")
    print(f"📝 Quotes to generate: {num_to_generate}")
    print("=" * 60)

    success = 0
    for i, quote in enumerate(selected_quotes, 1):
        scene = random.choice(SCENE_TEMPLATES)
        if generate_wizard_quote(quote, scene, i):
            success += 1

    print()
    print("=" * 60)
    print(f"🎉 Generated {success}/{num_to_generate} wizard quote memes")
    if success > 0:
        print(f"📁 Location: {OUTPUT_DIR}")
        print()
        print("These images have the QUOTE TEXT rendered directly by Gemini!")
    print("=" * 60)


if __name__ == "__main__":
    main()
