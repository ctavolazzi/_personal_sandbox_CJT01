"""
Generate whimsical AI backgrounds using Gemini's image generation.

Usage:
    python generate_backgrounds.py              # Generate 2 backgrounds
    python generate_backgrounds.py --count 5   # Generate 5 backgrounds
"""

import os
import sys
import time
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Add parent for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "api-testing-framework"))
load_dotenv()

import google.generativeai as genai
from PIL import Image
import io

# Configure
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

OUTPUT_DIR = Path(__file__).parent / "assets" / "backgrounds"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Whimsical prompt templates
PROMPTS = [
    "Abstract dreamy watercolor background with soft purple and gold gradients, ethereal clouds, mystical atmosphere, no text, no people, artistic, painterly",
    "Whimsical cosmic night sky with swirling galaxies, warm orange and deep blue tones, magical stardust, no text, no people, dreamy",
    "Soft pastel sunset over calm water, pink and lavender reflections, serene mood, no text, no people, impressionist style",
    "Deep forest with magical floating lights, emerald green and amber tones, enchanted atmosphere, no text, no people",
    "Abstract geometric pattern with warm earth tones, terracotta and sage green, modern boho aesthetic, no text",
]


def generate_background(prompt: str, output_path: Path, model_name: str = "gemini-2.0-flash-exp-image-generation"):
    """Generate a single background image."""
    model = genai.GenerativeModel(model_name)

    full_prompt = f"Create an image: {prompt}"

    print(f"🎨 Generating: {prompt[:50]}...")

    response = model.generate_content(full_prompt)

    if response.candidates:
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                image_data = part.inline_data.data
                img = Image.open(io.BytesIO(image_data))

                # Resize to 1080x1080 if needed
                if img.size != (1080, 1080):
                    img = img.resize((1080, 1080), Image.Resampling.LANCZOS)

                img.save(output_path)
                print(f"✅ Saved: {output_path.name} ({img.size})")
                return True
            elif hasattr(part, 'text') and part.text:
                print(f"⚠️  Got text instead of image: {part.text[:100]}...")

    print(f"❌ No image generated")
    return False


def main():
    parser = argparse.ArgumentParser(description="Generate AI backgrounds")
    parser.add_argument("--count", type=int, default=2, help="Number of backgrounds to generate")
    parser.add_argument("--delay", type=int, default=5, help="Delay between requests (seconds)")
    args = parser.parse_args()

    print("=" * 60)
    print("🎨 WHIMSICAL BACKGROUND GENERATOR")
    print("=" * 60)
    print(f"Output: {OUTPUT_DIR}")
    print(f"Count: {args.count}")
    print()

    success = 0
    for i in range(min(args.count, len(PROMPTS))):
        prompt = PROMPTS[i]
        output_path = OUTPUT_DIR / f"whimsical_bg_{i+1}.png"

        try:
            if generate_background(prompt, output_path):
                success += 1
        except Exception as e:
            print(f"❌ Error: {e}")

        if i < args.count - 1:
            print(f"⏳ Waiting {args.delay}s...")
            time.sleep(args.delay)

    print()
    print("=" * 60)
    print(f"🎉 Generated {success}/{args.count} backgrounds")
    print("=" * 60)


if __name__ == "__main__":
    main()
