"""
ProductShot - AI Product Visualization Generator
================================================
Generate professional product mockups and lifestyle shots.

Usage:
  productshot "Wireless earbuds, white case" --style minimal
  productshot "Craft beer bottle, amber lager" --style lifestyle
  productshot "Mobile app on phone" --style tech
"""

import os
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

@dataclass
class Config:
    output_dir: Path = Path.home() / "Desktop" / "ProductShot"

CONFIG = Config()

STYLES = {
    "minimal": {
        "name": "Minimal Studio",
        "emoji": "⬜",
        "style": """
            Setting: Clean white/light gray studio background
            Lighting: Soft diffused studio lighting, gentle shadows
            Composition: Product centered, lots of negative space
            Mood: Apple-style minimal, premium, sophisticated
            Props: None or minimal - just the product
            Focus: Sharp product focus, slight background blur
        """,
    },
    "lifestyle": {
        "name": "Lifestyle Scene",
        "emoji": "🏡",
        "style": """
            Setting: Natural lifestyle environment relevant to product
            Lighting: Natural warm lighting, golden hour feel
            Composition: Product in use context, environmental storytelling
            Mood: Aspirational, relatable, Instagram-worthy
            Props: Contextual items, plants, textures, human elements
            Focus: Product highlighted but part of a scene
        """,
    },
    "tech": {
        "name": "Tech Product",
        "emoji": "💻",
        "style": """
            Setting: Dark sleek surface, gradient background
            Lighting: Dramatic product lighting, subtle rim light
            Composition: Dynamic angle, floating effect optional
            Mood: Futuristic, premium tech, launch event style
            Props: Minimal - reflection surface, subtle particles
            Effects: Lens flare, glow effects, depth of field
        """,
    },
    "flat_lay": {
        "name": "Flat Lay",
        "emoji": "📸",
        "style": """
            Setting: Top-down view on styled background
            Lighting: Even soft overhead lighting
            Composition: Carefully arranged items, Instagram flat lay style
            Mood: Curated, social media ready, aesthetic
            Props: Complementary items, textures, branded elements
            Background: Marble, wood, fabric, or solid color
        """,
    },
    "outdoor": {
        "name": "Outdoor Adventure",
        "emoji": "🏔️",
        "style": """
            Setting: Natural outdoor environment
            Lighting: Natural sunlight, dramatic landscapes
            Composition: Product in adventure/nature context
            Mood: Rugged, adventurous, outdoor lifestyle
            Props: Nature elements, outdoor gear, action context
            Focus: Environmental product photography
        """,
    },
    "food": {
        "name": "Food/Beverage",
        "emoji": "🍽️",
        "style": """
            Setting: Appetizing food photography setup
            Lighting: Soft natural or studio food lighting
            Composition: Hero shot with garnish and props
            Mood: Delicious, appetizing, craveable
            Props: Ingredients, utensils, napkins, surfaces
            Details: Steam, condensation, texture highlights
        """,
    },
    "cosmetics": {
        "name": "Beauty/Cosmetics",
        "emoji": "💄",
        "style": """
            Setting: Luxurious beauty photography setup
            Lighting: Soft glamorous lighting, highlights product texture
            Composition: Elegant arrangement, often with swatches
            Mood: Luxurious, feminine/neutral, aspirational
            Props: Flowers, silk, marble, water drops
            Details: Product texture, color accuracy, premium feel
        """,
    },
    "packaging": {
        "name": "Packaging Mockup",
        "emoji": "📦",
        "style": """
            Setting: Clean studio or contextual background
            Lighting: Professional product photography lighting
            Composition: Multiple angles, show full packaging
            Mood: Professional, e-commerce ready
            Props: Minimal, focus on package design
            Focus: Sharp product details, label readability
        """,
    },
}


def generate_product_shot(
    product: str,
    style: str = "minimal",
    angle: str = None,
    color_scheme: str = None,
    output_dir: Path = None,
) -> dict:
    """Generate a product visualization."""
    from google import genai
    from google.genai import types
    from dotenv import load_dotenv
    load_dotenv()

    if style not in STYLES:
        raise ValueError(f"Unknown style: {style}. Options: {list(STYLES.keys())}")

    style_data = STYLES[style]
    output_dir = Path(output_dir) if output_dir else CONFIG.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    prompt = f"""Create a professional product photography image:

PRODUCT: {product}

PHOTOGRAPHY STYLE: {style_data['name']}
{style_data['style']}

{f'CAMERA ANGLE: {angle}' if angle else 'CAMERA ANGLE: Flattering hero angle for this product type'}
{f'COLOR SCHEME: {color_scheme}' if color_scheme else ''}

REQUIREMENTS:
- Make the product look premium and desirable
- Professional commercial photography quality
- Suitable for e-commerce, advertising, or social media
- Sharp product focus with appropriate depth of field
- The product should be the clear hero of the image
"""

    slug = product[:20].replace(' ', '_').replace(',', '')
    slug = ''.join(c for c in slug if c.isalnum() or c == '_')
    timestamp = datetime.now().strftime("%H%M%S")
    filename = f"product_{style}_{slug}_{timestamp}.png"
    output_path = output_dir / filename

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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
                with open(output_path, "wb") as f:
                    f.write(part.inline_data.data)
                return {
                    "path": str(output_path),
                    "product": product,
                    "style": style,
                }
        raise Exception("No image generated")

    except Exception as e:
        if "429" in str(e):
            import time
            time.sleep(10)
            return generate_product_shot(product, style, angle, color_scheme, output_dir)
        raise


def list_styles() -> dict:
    return {k: {"name": v["name"], "emoji": v["emoji"]} for k, v in STYLES.items()}


def cli():
    import argparse
    from dotenv import load_dotenv
    load_dotenv()

    parser = argparse.ArgumentParser(description="ProductShot - Product Visualization Generator")
    parser.add_argument("product", nargs="?", help="Product description")
    parser.add_argument("--style", "-s", default="minimal")
    parser.add_argument("--angle", "-a", help="Camera angle hint")
    parser.add_argument("--colors", "-c", help="Color scheme")
    parser.add_argument("--output", "-o")
    parser.add_argument("--list-styles", action="store_true")
    parser.add_argument("--open", action="store_true")

    args = parser.parse_args()

    if args.list_styles:
        print("\n📸 PRODUCT SHOT STYLES:\n")
        for key, info in list_styles().items():
            print(f"  {info['emoji']} {key:15} - {info['name']}")
        print()
        return

    if not args.product:
        parser.print_help()
        return

    if args.output:
        CONFIG.output_dir = Path(args.output)

    print(f"📸 Generating {args.style} product shot...")
    result = generate_product_shot(args.product, args.style, args.angle, args.colors)
    print(f"✅ {result['path']}")

    if args.open:
        import subprocess
        subprocess.run(["open", str(CONFIG.output_dir)])


if __name__ == "__main__":
    cli()
