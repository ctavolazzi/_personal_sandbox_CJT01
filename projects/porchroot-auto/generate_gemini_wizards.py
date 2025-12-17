"""
Generate Cyber-Corrupted Wizard Backgrounds using Gemini Image Generation
Uses the new google-genai SDK for native image generation.

Usage:
    python generate_gemini_wizards.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from google import genai
from google.genai import types

# Configure client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

OUTPUT_DIR = Path(__file__).parent / "assets" / "backgrounds"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Cyber-corrupted wizard prompts - fantasy being taken over by the Matrix
PROMPTS = [
    """Create a pixel art image in 16-bit retro style:
    A fantasy wizard with a long flowing beard and tall pointed hat, being corrupted by The Matrix.
    Green digital code cascades down his robes like spreading corruption.
    His eyes glow bright matrix green. Parts of his body are glitching with pixelated distortions.
    Horizontal scan lines cut through him. His wooden staff crackles with both magical fire and digital static.
    Background: deep void with falling matrix code characters.
    Style: Dark, moody, cyberpunk meets high fantasy. No text.""",

    """Create a pixel art image in retro 16-bit game style:
    An ancient wizard's tower being consumed by digital corruption from The Matrix.
    The stone tower has glowing green circuit patterns spreading up its walls like vines.
    Matrix code rains down from the sky. Magical runes on the tower flicker between ancient symbols and binary.
    A wizard silhouette in a window, half flesh half digital wireframe.
    Style: Pixel art, dark fantasy, cyberpunk corruption. No text.""",

    """Create a pixel art image:
    A wizard's spellbook floating open, pages transforming from magical runes to streaming green Matrix code.
    Magical sparkles mix with digital glitches around the book.
    The background is a dark void with falling code characters.
    A wizard's hand reaches for the book - half normal, half wireframe digital corruption.
    Style: 16-bit pixel art, whimsical yet dark, fantasy meets cyber. No text.""",

    """Create a pixel art image in retro game style:
    A magical forest scene being invaded by The Matrix.
    Ancient trees with glowing runes are being overtaken by green digital corruption.
    Pixel art wizards and magical creatures partially glitched - some body parts replaced with wireframes.
    Matrix code falls like rain through the canopy.
    Floating magical orbs flicker between mystical energy and digital data streams.
    Style: Dark whimsical pixel art, fantasy cyberpunk fusion. No text.""",
]


def generate_wizard_background(prompt: str, output_path: Path, index: int):
    """Generate a single cyber-wizard background using Gemini."""

    print(f"\n🧙 Generating wizard background {index}...")
    print(f"   Prompt: {prompt[:60]}...")

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
                print(f"   📝 Text: {part.text[:100]}...")
            elif part.inline_data is not None:
                # Get the raw image data and save it
                image_data = part.inline_data.data
                mime_type = part.inline_data.mime_type

                # Determine extension from mime type
                ext = ".png" if "png" in mime_type else ".jpg"
                final_path = output_path.with_suffix(ext)

                # Save raw bytes
                with open(final_path, "wb") as f:
                    f.write(image_data)

                # Get size for display
                from PIL import Image as PILImage
                with PILImage.open(final_path) as img:
                    print(f"   ✅ Saved: {final_path.name} ({img.size[0]}x{img.size[1]})")
                return True

        print(f"   ❌ No image in response")
        return False

    except Exception as e:
        error_str = str(e)
        if "429" in error_str:
            print(f"   ⚠️  Rate limited - try again later")
            if "limit: 0" in error_str:
                print(f"   💳 Image generation requires billing enabled")
                print(f"      Go to: https://console.cloud.google.com/billing")
        else:
            print(f"   ❌ Error: {e}")
        return False


def main():
    print("=" * 60)
    print("🧙 CYBER-CORRUPTED WIZARD BACKGROUND GENERATOR")
    print("   Fantasy Wizards × Matrix Corruption × Pixel Art")
    print("=" * 60)
    print(f"📁 Output: {OUTPUT_DIR}")
    print(f"🎨 Backgrounds to generate: {len(PROMPTS)}")

    success = 0
    for i, prompt in enumerate(PROMPTS, 1):
        output_path = OUTPUT_DIR / f"gemini_cyber_wizard_{i}.png"
        if generate_wizard_background(prompt, output_path, i):
            success += 1

    print()
    print("=" * 60)
    print(f"🎉 Generated {success}/{len(PROMPTS)} cyber-wizard backgrounds")
    if success > 0:
        print(f"📁 Location: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
