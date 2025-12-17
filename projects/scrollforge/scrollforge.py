"""
ScrollForge - Ancient Document Generator
========================================
Transform text into ancient scrolls, manuscripts, and historical documents.

Usage:
  scrollforge "Your prophecy text here" --style medieval
  scrollforge "Recipe for eternal youth" --style alchemist
  scrollforge "The sacred laws" --style egyptian
"""

import os
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

@dataclass
class Config:
    output_dir: Path = Path.home() / "Desktop" / "ScrollForge"

CONFIG = Config()

# Ancient document styles
STYLES = {
    "medieval": {
        "name": "Medieval Manuscript",
        "emoji": "📜",
        "style": """
            Style: Illuminated medieval manuscript
            Paper: Aged parchment with worn edges, tea-stained
            Text: Gothic blackletter calligraphy in dark brown/black ink
            Decorations: Ornate illuminated capital letters, gold leaf accents,
                        floral borders, Celtic knots, miniature illustrations in margins
            Wear: Some fading, foxing spots, wax drips, slight tears at edges
        """,
    },
    "egyptian": {
        "name": "Egyptian Papyrus",
        "emoji": "🏛️",
        "style": """
            Style: Ancient Egyptian papyrus scroll
            Paper: Tan/brown papyrus with fibrous texture, torn edges
            Text: Hieroglyphic-inspired decorative elements mixed with text
            Decorations: Egyptian gods in margins, cartouches, Eye of Horus,
                        scarab beetles, lotus flowers, golden accents
            Wear: Faded sections, ancient stains, cracked surface
        """,
    },
    "alchemist": {
        "name": "Alchemist's Notes",
        "emoji": "⚗️",
        "style": """
            Style: Medieval alchemist's laboratory notes
            Paper: Dark aged parchment, burn marks, chemical stains
            Text: Cramped handwriting, mix of Latin and symbols
            Decorations: Alchemical symbols, planetary signs, ouroboros,
                        diagrams of equipment, mystical circles, coded margins
            Wear: Singed edges, mysterious stains, wax seals
        """,
    },
    "pirate": {
        "name": "Pirate Map/Letter",
        "emoji": "🏴‍☠️",
        "style": """
            Style: Weathered pirate document or treasure map
            Paper: Sea-worn parchment, water stained, salt crusted
            Text: Bold captain's handwriting, X marks, coordinates
            Decorations: Skull and crossbones, compass rose, sea monsters,
                        dotted paths, anchor symbols, rope borders
            Wear: Torn corners, fold creases, rum stains, burned edges
        """,
    },
    "wizard": {
        "name": "Wizard's Spellbook",
        "emoji": "🧙",
        "style": """
            Style: Page from an ancient spellbook
            Paper: Dark mysterious parchment with magical shimmer
            Text: Arcane script with glowing runes interspersed
            Decorations: Mystical symbols, constellation maps, potion ingredients,
                        magical creatures in margins, glowing sigils
            Wear: Scorch marks from spells, ethereal glow, floating particles
        """,
    },
    "asian": {
        "name": "Asian Scroll",
        "emoji": "🎋",
        "style": """
            Style: Traditional East Asian hanging scroll
            Paper: Rice paper or silk, cream/tan colored
            Text: Elegant brush calligraphy, vertical orientation
            Decorations: Ink wash landscape elements, bamboo, cherry blossoms,
                        red seal stamps (chops), subtle watercolor washes
            Wear: Slight foxing, aged silk edges, gentle creases
        """,
    },
    "roman": {
        "name": "Roman Decree",
        "emoji": "🏛️",
        "style": """
            Style: Official Roman empire document
            Paper: Light parchment with formal presentation
            Text: Latin-style capitals, formal Roman typeface
            Decorations: Laurel wreaths, SPQR eagles, columns at borders,
                        wax imperial seals, red ribbon ties
            Wear: Official folds, seal impressions, dignified aging
        """,
    },
    "lovecraft": {
        "name": "Lovecraftian Tome",
        "emoji": "🐙",
        "style": """
            Style: Page from forbidden eldritch tome
            Paper: Unsettling leather-like material, wrong colors
            Text: Disturbing script that seems to move, non-Euclidean layouts
            Decorations: Tentacles in margins, alien geometries, elder signs,
                        eyes that seem to watch, sanity-bending patterns
            Wear: Impossible stains, reality distortions at edges
        """,
    },
}


def generate_scroll(
    text: str,
    style: str = "medieval",
    title: str = None,
    output_dir: Path = None,
) -> dict:
    """Generate an ancient document with the given text."""
    from google import genai
    from google.genai import types
    from dotenv import load_dotenv
    load_dotenv()

    if style not in STYLES:
        raise ValueError(f"Unknown style: {style}. Options: {list(STYLES.keys())}")

    style_data = STYLES[style]
    output_dir = Path(output_dir) if output_dir else CONFIG.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    prompt = f"""Create an image of an ancient document containing this text:

TEXT TO INCLUDE:
"{text}"

{f'TITLE/HEADER: {title}' if title else ''}

DOCUMENT STYLE: {style_data['name']}
{style_data['style']}

REQUIREMENTS:
- The text should be readable but styled appropriately for the document type
- Include appropriate decorative elements for authenticity
- Make it look genuinely ancient and weathered
- The document should look like a real historical artifact
- Aspect ratio should be portrait (taller than wide) like a real document page
"""

    # Generate filename
    slug = text[:25].replace(' ', '_')
    slug = ''.join(c for c in slug if c.isalnum() or c == '_')
    timestamp = datetime.now().strftime("%H%M%S")
    filename = f"scroll_{style}_{slug}_{timestamp}.png"
    output_path = output_dir / filename

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_modalities=['IMAGE'],
                image_config=types.ImageConfig(aspect_ratio="9:16")  # Portrait
            )
        )

        for part in response.parts:
            if part.inline_data is not None:
                with open(output_path, "wb") as f:
                    f.write(part.inline_data.data)
                return {
                    "path": str(output_path),
                    "text": text,
                    "style": style,
                    "title": title,
                }
        raise Exception("No image generated")

    except Exception as e:
        if "429" in str(e):
            import time
            time.sleep(10)
            return generate_scroll(text, style, title, output_dir)
        raise


def list_styles() -> dict:
    return {k: {"name": v["name"], "emoji": v["emoji"]} for k, v in STYLES.items()}


def cli():
    import argparse
    from dotenv import load_dotenv
    load_dotenv()

    parser = argparse.ArgumentParser(description="ScrollForge - Ancient Document Generator")
    parser.add_argument("text", nargs="?", help="Text to inscribe")
    parser.add_argument("--style", "-s", default="medieval", help=f"Style: {', '.join(STYLES.keys())}")
    parser.add_argument("--title", "-t", help="Document title/header")
    parser.add_argument("--output", "-o", help="Output directory")
    parser.add_argument("--list-styles", action="store_true")
    parser.add_argument("--open", action="store_true")

    args = parser.parse_args()

    if args.list_styles:
        print("\n📜 ANCIENT DOCUMENT STYLES:\n")
        for key, info in list_styles().items():
            print(f"  {info['emoji']} {key:15} - {info['name']}")
        print()
        return

    if not args.text:
        parser.print_help()
        return

    if args.output:
        CONFIG.output_dir = Path(args.output)

    print(f"📜 Generating {args.style} scroll...")
    result = generate_scroll(args.text, args.style, args.title)
    print(f"✅ {result['path']}")

    if args.open:
        import subprocess
        subprocess.run(["open", str(CONFIG.output_dir)])


if __name__ == "__main__":
    cli()
