"""
Generate Dino Details Branded Images - Holiday Edition
Matches the green/white stencil style with T-Rex in Santa hat driving vintage car.

Usage:
    python generate_dino_details_v2.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from google import genai
from google.genai import types

# Configure client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

OUTPUT_DIR = Path(__file__).parent / "assets" / "dino_details_v2"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Brand info
PHONE = "530-591-5297"
EMAIL = "dinodetailsmobile@gmail.com"

# Style guide for all prompts
STYLE_GUIDE = """
Style requirements:
- Dark forest green background (#2d5a3d or similar)
- White/cream colored artwork in stencil/silhouette style
- T-Rex dinosaur driving a classic vintage car (1950s style)
- Christmas/holiday theme: Santa hat on dinosaur, snowflakes in background
- Sparkling headlight effect on the car
- Bold white sans-serif text
- Professional mobile detailing service aesthetic
- Monochromatic green and white only - no other colors
"""

PROMPTS = [
    f"""Create a promotional image for a mobile car detailing service:
    A T-Rex dinosaur wearing a red Santa hat, driving a vintage 1950s car, in white stencil art style.
    Dark green background with subtle snowflakes.
    The car's headlight has a sparkling shine effect.

    Text layout:
    - "DINO DETAILS" in large bold white letters
    - "INTERIOR DETAILING" below in medium white text
    - "CALL OR TEXT {PHONE}" in white
    - "{EMAIL}" at bottom

    {STYLE_GUIDE}""",

    f"""Create a holiday promotional graphic for auto detailing:
    White silhouette of a happy T-Rex dinosaur in a Santa hat behind the wheel of a classic car.
    Dark green background with decorative snowflakes scattered around.
    Glowing headlight with sparkle/shine lines.

    Text:
    - "DINO DETAILS" prominently displayed
    - "FULL EXTERIOR WASH & WAX" as the service
    - "CALL OR TEXT {PHONE}"
    - "{EMAIL}"

    {STYLE_GUIDE}""",

    f"""Create a Christmas-themed car service advertisement:
    Stencil-style white artwork of a T-Rex dinosaur wearing Santa hat, sitting in a vintage convertible car.
    Rich dark green background with elegant snowflake decorations.
    Bright sparkling headlight effect.

    Text in white:
    - "DINO DETAILS" as main header
    - "CERAMIC COATING" as featured service
    - "CALL OR TEXT {PHONE}"
    - "{EMAIL}"

    {STYLE_GUIDE}""",

    f"""Create a festive promotional image for mobile detailing:
    White vector-style T-Rex dinosaur with Santa hat driving a classic American car.
    Deep green background with Christmas snowflakes.
    One headlight glowing with star sparkle effect.

    Bold text:
    - "DINO DETAILS"
    - "PAINT CORRECTION"
    - "CALL OR TEXT {PHONE}"
    - "{EMAIL}"

    {STYLE_GUIDE}""",

    f"""Create a holiday season car care advertisement:
    Cheerful T-Rex in Santa hat at the wheel of a vintage hot rod, white stencil on green.
    Snowflake pattern in background, Christmas vibes.
    Gleaming headlight with light rays.

    Text layout:
    - "DINO DETAILS" big and bold
    - "ENGINE BAY CLEANING"
    - "CALL OR TEXT {PHONE}"
    - "{EMAIL}"

    {STYLE_GUIDE}""",

    f"""Create a winter promotional graphic:
    T-Rex dinosaur wearing red and white Santa hat, driving vintage car, white artwork style.
    Dark green festive background with falling snowflakes.
    Sparkling headlight detail.

    Include text:
    - "DINO DETAILS"
    - "GIFT CERTIFICATES AVAILABLE"
    - "CALL OR TEXT {PHONE}"
    - "{EMAIL}"

    {STYLE_GUIDE}""",
]


def generate_dino_image(prompt: str, output_path: Path, index: int):
    """Generate a single Dino Details branded image using Gemini."""

    print(f"\n🦖🎄 Generating holiday image {index}...")
    print(f"   Service: {prompt.split('service')[0][-30:] if 'service' in prompt else 'Dino Details'}...")

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_modalities=['IMAGE'],
                image_config=types.ImageConfig(
                    aspect_ratio="9:16",  # Portrait for mobile/social
                )
            )
        )

        # Process response
        for part in response.parts:
            if part.text is not None:
                print(f"   📝 Text: {part.text[:100]}...")
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
            print(f"   ⚠️  Rate limited - waiting...")
            import time
            time.sleep(5)
            return generate_dino_image(prompt, output_path, index)  # Retry
        else:
            print(f"   ❌ Error: {e}")
        return False


def main():
    print("=" * 60)
    print("🦖🎄 DINO DETAILS - HOLIDAY EDITION")
    print("   Green & White Stencil Style • Santa Hat T-Rex")
    print("=" * 60)
    print(f"📁 Output: {OUTPUT_DIR}")
    print(f"📞 Phone: {PHONE}")
    print(f"📧 Email: {EMAIL}")
    print(f"🎨 Images to generate: {len(PROMPTS)}")

    success = 0
    for i, prompt in enumerate(PROMPTS, 1):
        output_path = OUTPUT_DIR / f"dino_holiday_{i}.png"
        if generate_dino_image(prompt, output_path, i):
            success += 1

    print()
    print("=" * 60)
    print(f"🎉 Generated {success}/{len(PROMPTS)} holiday images")
    if success > 0:
        print(f"📁 Location: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
