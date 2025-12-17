"""
Generate Consistent Cyber-Wizard Quote Backgrounds for Porchroot
Uses a strict style guide for visual consistency across all generations.

Usage:
    python generate_wizard_memes.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from google import genai
from google.genai import types

# Configure client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

OUTPUT_DIR = Path(__file__).parent / "assets" / "wizard_memes"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# STYLE GUIDE - This ensures consistency across all generations
# ============================================================
STYLE_GUIDE = """
STRICT STYLE REQUIREMENTS (follow exactly):
- Art style: 16-bit retro pixel art, like classic SNES/Genesis RPG games
- Color palette: Deep purples (#2a1a4a), matrix greens (#00ff41), black voids, magical blues (#4a90d9)
- Matrix elements: Falling green code characters (like The Matrix movie), digital glitches, scan lines
- Fantasy elements: Wizard robes, pointed hats, magical staves, glowing runes, mystical energy
- Corruption theme: Parts of the fantasy world "glitching" into digital wireframes
- Mood: Dark, mysterious, whimsical yet ominous
- Composition: Leave space at top and bottom for quote text overlay
- Background: Dark void or gradient, never pure white
- NO photorealism - strictly pixel art aesthetic
- NO text in the image - leave clean for text overlay later
"""

# Quote-friendly backgrounds (space for text overlay)
PROMPTS = [
    f"""Create a 16-bit pixel art background image:
    A wise old wizard with a long white beard stands contemplating, his robes flowing.
    Half of his body is normal fantasy style, half is glitching into green Matrix code.
    His staff crackles with both magical fire and digital static electricity.
    Matrix code rain falls gently in the background.
    Dark purple void behind him with subtle stars.
    {STYLE_GUIDE}""",

    f"""Create a 16-bit pixel art background:
    A mystical wizard's study room being consumed by digital corruption.
    Bookshelves with ancient tomes, some books transforming into streams of green code.
    A crystal ball shows The Matrix code instead of visions.
    Candles flicker between flame and pixelated glitches.
    Dark atmospheric mood with purple and green lighting.
    {STYLE_GUIDE}""",

    f"""Create a pixel art scene:
    A wizard's tower at night, silhouetted against a sky of falling Matrix code.
    The moon is replaced by a glowing green terminal cursor.
    Magical runes on the tower walls flicker between ancient symbols and binary.
    Purple mist at the base, green digital corruption spreading up the stones.
    {STYLE_GUIDE}""",

    f"""Create a 16-bit pixel art image:
    A wizard casting a spell, but the magic emerging is Matrix code instead of fire.
    Green digital energy swirls from his hands into the dark void.
    His eyes glow bright matrix green.
    Pixel art stars and code characters scattered in the background.
    Dark purple to black gradient behind.
    {STYLE_GUIDE}""",

    f"""Create a pixel art background:
    An enchanted forest path at twilight, trees partially corrupted by The Matrix.
    Some trees are normal fantasy style, others are wireframe digital versions.
    Floating magical orbs mix with floating green code characters.
    A wizard silhouette walks the path in the distance.
    Purple and green atmospheric lighting.
    {STYLE_GUIDE}""",

    f"""Create a 16-bit pixel art scene:
    A wizard's potion laboratory with bubbling cauldrons.
    The potions glow with matrix green instead of traditional colors.
    Steam rising forms patterns of falling code.
    Spell ingredients on shelves - some real, some glitching into digital artifacts.
    Dark moody lighting with green and purple accents.
    {STYLE_GUIDE}""",

    f"""Create a pixel art background image:
    A wizard meditating, floating in a void between two worlds.
    On one side: classic fantasy - stars, magical energy, warm colors.
    On the other side: The Matrix - green code, wireframes, digital cold.
    The wizard is at the center, being pulled in both directions.
    Symmetrical composition with dark center.
    {STYLE_GUIDE}""",

    f"""Create a 16-bit pixel art scene:
    Ancient wizard ruins with crumbling stone pillars.
    Magical glyphs carved in stone now display as glitching green terminals.
    A mystical portal shows The Matrix code dimension beyond.
    Pixel art fireflies mix with floating code particles.
    Dark atmospheric with purple shadows and green highlights.
    {STYLE_GUIDE}""",
]


def generate_wizard_background(prompt: str, output_path: Path, index: int):
    """Generate a single wizard background using Gemini."""

    print(f"\n🧙 Generating wizard background {index}/{len(PROMPTS)}...")

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_modalities=['IMAGE'],
                image_config=types.ImageConfig(
                    aspect_ratio="1:1",  # Square for social media posts
                )
            )
        )

        # Process response
        for part in response.parts:
            if part.text is not None:
                print(f"   📝 Note: {part.text[:80]}...")
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
            print(f"   ⚠️  Rate limited - waiting 5s...")
            import time
            time.sleep(5)
            return generate_wizard_background(prompt, output_path, index)
        else:
            print(f"   ❌ Error: {e}")
        return False


def main():
    print("=" * 60)
    print("🧙 PORCHROOT WIZARD MEME BACKGROUNDS")
    print("   Cyber-Corrupted Fantasy • 16-bit Pixel Art")
    print("   Consistent Style Guide Applied")
    print("=" * 60)
    print(f"📁 Output: {OUTPUT_DIR}")
    print(f"🎨 Backgrounds to generate: {len(PROMPTS)}")
    print()
    print("Style: 16-bit pixel art, purple/green palette,")
    print("       Matrix corruption, fantasy wizards")
    print("=" * 60)

    success = 0
    for i, prompt in enumerate(PROMPTS, 1):
        output_path = OUTPUT_DIR / f"wizard_bg_{i:02d}.png"
        if generate_wizard_background(prompt, output_path, i):
            success += 1

    print()
    print("=" * 60)
    print(f"🎉 Generated {success}/{len(PROMPTS)} wizard backgrounds")
    if success > 0:
        print(f"📁 Location: {OUTPUT_DIR}")
        print()
        print("Next: Use factory.py to overlay quotes on these backgrounds!")
    print("=" * 60)


if __name__ == "__main__":
    main()
