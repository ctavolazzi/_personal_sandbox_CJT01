"""
Generate Dino Details Branded Backgrounds using Gemini Image Generation
Car detailing business with a T-Rex mascot driving a vintage car.

Usage:
    python generate_dino_details.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from google import genai
from google.genai import types

# Configure client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

OUTPUT_DIR = Path(__file__).parent / "assets" / "dino_details"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Dino Details prompts - T-Rex car detailing business with text
PROMPTS = [
    """Create a bold promotional image for a car detailing business:
    A cartoon T-Rex dinosaur wearing sunglasses, happily washing/detailing a shiny vintage car.
    The dinosaur is using a polishing cloth with its tiny arms.
    Sparkling clean effects around the car.
    Bold text at the top says "DINO DETAILS"
    Tagline at bottom: "Prehistoric Shine, Modern Clean"
    Style: Fun, professional, vibrant green and chrome colors. Marketing poster style.""",

    """Create a promotional graphic for Dino Details car wash:
    A friendly green T-Rex dinosaur driving a classic hot rod car that's gleaming and spotless.
    The car has water droplets and shine effects showing it was just detailed.
    Large bold text: "DINO DETAILS"
    Smaller text: "We Go Extinct on Dirt"
    Style: Retro Americana, 1950s diner poster aesthetic, bold colors.""",

    """Create a business advertisement image:
    A muscular cartoon T-Rex dinosaur flexing while standing next to a perfectly detailed luxury car.
    The car's paint is mirror-like with reflections.
    Professional detailing equipment nearby.
    Text: "DINO DETAILS" in big bold chrome letters
    Subtext: "Jurassic Quality Service"
    Style: Bold, confident, professional auto detailing advertisement.""",

    """Create a fun promotional image for a car detailing service:
    A cute but cool T-Rex dinosaur in a green uniform, holding detailing spray bottles.
    Behind him: before/after of a dirty car transformed to sparkling clean.
    Big bold text: "DINO DETAILS"
    Bottom text: "Making Cars Roar Since Day 1"
    Style: Friendly, approachable, professional service advertisement with green brand colors.""",

    """Create a social media promotional image:
    A T-Rex dinosaur giving a thumbs up (with tiny arms) next to a gleaming sports car.
    Stars and sparkle effects showing the car is immaculately clean.
    Bold header: "DINO DETAILS"
    Call to action: "Book Your Detail Today!"
    Style: Eye-catching social media ad, vibrant green theme, professional yet fun.""",

    """Create a logo-style promotional image:
    A T-Rex dinosaur head emerging from behind a perfectly polished vintage car hood.
    The car's chrome reflects everything perfectly.
    Circular badge design with text "DINO DETAILS" arched at top
    "Premium Auto Detailing" at bottom of circle
    Style: Logo badge, vintage auto shop aesthetic, green and silver colors.""",
]


def generate_dino_background(prompt: str, output_path: Path, index: int):
    """Generate a single Dino Details branded image using Gemini."""

    print(f"\n🦖 Generating Dino Details image {index}...")
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
        else:
            print(f"   ❌ Error: {e}")
        return False


def main():
    print("=" * 60)
    print("🦖 DINO DETAILS - BRANDED IMAGE GENERATOR")
    print("   T-Rex Car Detailing • With Text On Images")
    print("=" * 60)
    print(f"📁 Output: {OUTPUT_DIR}")
    print(f"🎨 Images to generate: {len(PROMPTS)}")

    success = 0
    for i, prompt in enumerate(PROMPTS, 1):
        output_path = OUTPUT_DIR / f"dino_details_{i}.png"
        if generate_dino_background(prompt, output_path, i):
            success += 1

    print()
    print("=" * 60)
    print(f"🎉 Generated {success}/{len(PROMPTS)} Dino Details images")
    if success > 0:
        print(f"📁 Location: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
