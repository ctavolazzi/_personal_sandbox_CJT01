"""
CrappyDesign - Intentionally Bad Graphic Design Generator
=========================================================
Generate gloriously terrible designs in various classic bad design styles.

Usage:
  crappydesign "GRAND OPENING SALE!!!" --style 90s_web
  crappydesign "Birthday Party" --style wordart
  crappydesign "Local Business" --style clipart_hell
"""

import os
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

@dataclass
class Config:
    output_dir: Path = Path.home() / "Desktop" / "CrappyDesign"

CONFIG = Config()

STYLES = {
    "90s_web": {
        "name": "90s Website",
        "emoji": "🌐",
        "style": """
            Style: Geocities/Angelfire 90s website aesthetic
            Background: Tiled starfield or garish pattern, maybe animated GIF feeling
            Text: Comic Sans, multiple fonts, rainbow colors, blinking text feeling
            Elements: Under construction GIFs, visitor counters, "WELCOME TO MY PAGE"
                     spinning email icons, horizontal rule lines everywhere
            Colors: Clashing neons, lime green, hot pink, electric blue
            Layout: Chaotic, no alignment, text overlapping images
            Quality: Pixelated, low-res, compression artifacts
        """,
    },
    "wordart": {
        "name": "WordArt Madness",
        "emoji": "🔤",
        "style": """
            Style: Microsoft WordArt from the 90s/2000s
            Text: Rainbow gradient WordArt, wavy/curved text, 3D shadow effects
            Elements: Multiple WordArt styles combined, stretched text, outline effects
            Colors: Rainbow gradients, metallic effects, clashing color schemes
            Background: Solid color that doesn't match, or gradient clash
            Effects: Bevels, emboss, shadows, all at once
            Quality: That distinctive low-res WordArt rendering
        """,
    },
    "clipart_hell": {
        "name": "Clipart Nightmare",
        "emoji": "📎",
        "style": """
            Style: Microsoft Office clipart overload
            Images: Generic clipart people, handshakes, lightbulbs, targets
                   All clipart with different styles mixed together
            Text: Times New Roman or Arial, stretched to fit
            Layout: Clipart scattered randomly, no visual hierarchy
            Colors: Default Office color palette, primary colors
            Background: White with random decorative borders
            Elements: Cheesy business metaphors (puzzle pieces, ladders, stars)
        """,
    },
    "mall_kiosk": {
        "name": "Mall Kiosk Flyer",
        "emoji": "🛒",
        "style": """
            Style: Low-budget local business flyer/mall kiosk sign
            Text: Multiple fonts (at least 5), ALL CAPS EVERYWHERE
            Colors: Red and yellow "SALE" colors, black outlines
            Elements: Starburst "SPECIAL!", percentage signs, arrows pointing everywhere
            Images: Low-res stock photos, badly cut out products
            Layout: Every inch filled, no white space, overwhelming
            Effects: Drop shadows on everything, fake 3D text
        """,
    },
    "myspace": {
        "name": "MySpace Profile",
        "emoji": "💀",
        "style": """
            Style: Mid-2000s MySpace profile customization
            Background: Tiled emo/scene pattern or band photo
            Text: Unreadable white on light background, or neon on neon
            Elements: Glitter GIFs, music player graphic, "Thanks for the add!"
            Colors: Black, hot pink, lime green, scene kid palette
            Images: Mirror selfies, band logos, sparkle overlays
            Aesthetic: Scene/emo, XxX formatting, broken HTML feeling
        """,
    },
    "ransom": {
        "name": "Ransom Note",
        "emoji": "✂️",
        "style": """
            Style: Cut-out ransom note letters
            Text: Each letter from different magazine/newspaper cutouts
            Colors: Mixed - each letter different color and font
            Background: Plain paper, maybe lined or graph paper
            Layout: Slightly crooked letters, paste marks visible
            Elements: Visible paper edges, uneven spacing
            Texture: Paper grain, slight shadows under letters
        """,
    },
    "powerpoint": {
        "name": "Bad PowerPoint",
        "emoji": "📊",
        "style": """
            Style: Terrible corporate PowerPoint presentation slide
            Background: Gradient blue or default template
            Text: Way too much text, bullet points everywhere
            Fonts: Mix of Comic Sans and Times New Roman
            Elements: Cheesy transitions, clip art, "Any Questions?" slide energy
            Graphics: 3D pie charts, SmartArt abuse, stock handshakes
            Effects: Every animation effect at once, sound effect icons
        """,
    },
    "vaporwave_ironic": {
        "name": "Ironic Vaporwave",
        "emoji": "🗿",
        "style": """
            Style: Deliberately bad vaporwave aesthetic
            Elements: Roman statues, Windows 95, Japanese text (wrong)
            Colors: Pink and cyan but wrong shades, oversaturated
            Images: Low-res renders, palm trees, old computers
            Text: Badly translated Japanese, AESTHETIC in Futura
            Effects: Chromatic aberration, scanlines, too much grain
            Vibe: Trying too hard, missing the point aesthetically
        """,
    },
}


def generate_bad_design(
    text: str,
    style: str = "90s_web",
    purpose: str = None,
    output_dir: Path = None,
) -> dict:
    """Generate gloriously bad design."""
    from google import genai
    from google.genai import types
    from dotenv import load_dotenv
    load_dotenv()

    if style not in STYLES:
        raise ValueError(f"Unknown style: {style}. Options: {list(STYLES.keys())}")

    style_data = STYLES[style]
    output_dir = Path(output_dir) if output_dir else CONFIG.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    prompt = f"""Create an INTENTIONALLY BAD graphic design in the {style_data['name']} style:

MAIN TEXT/MESSAGE: {text}
{f'PURPOSE: {purpose}' if purpose else ''}

STYLE: {style_data['name']}
{style_data['style']}

IMPORTANT: This should look GENUINELY like bad amateur design from this era.
- Break design rules on purpose
- Mix things that don't go together
- Make it authentically terrible, not polished-terrible
- It should make designers cringe
- Commit fully to the aesthetic - don't hold back
"""

    slug = text[:20].replace(' ', '_')
    slug = ''.join(c for c in slug if c.isalnum() or c == '_')
    timestamp = datetime.now().strftime("%H%M%S")
    filename = f"crappy_{style}_{slug}_{timestamp}.png"
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
                    "text": text,
                    "style": style,
                }
        raise Exception("No image generated")

    except Exception as e:
        if "429" in str(e):
            import time
            time.sleep(10)
            return generate_bad_design(text, style, purpose, output_dir)
        raise


def list_styles() -> dict:
    return {k: {"name": v["name"], "emoji": v["emoji"]} for k, v in STYLES.items()}


def cli():
    import argparse
    from dotenv import load_dotenv
    load_dotenv()

    parser = argparse.ArgumentParser(description="CrappyDesign - Bad Graphic Design Generator")
    parser.add_argument("text", nargs="?", help="Main text for the design")
    parser.add_argument("--style", "-s", default="90s_web")
    parser.add_argument("--purpose", "-p", help="What this terrible design is for")
    parser.add_argument("--output", "-o")
    parser.add_argument("--list-styles", action="store_true")
    parser.add_argument("--open", action="store_true")

    args = parser.parse_args()

    if args.list_styles:
        print("\n💀 BAD DESIGN STYLES:\n")
        for key, info in list_styles().items():
            print(f"  {info['emoji']} {key:20} - {info['name']}")
        print()
        return

    if not args.text:
        parser.print_help()
        return

    if args.output:
        CONFIG.output_dir = Path(args.output)

    print(f"💀 Generating terrible {args.style} design...")
    result = generate_bad_design(args.text, args.style, args.purpose)
    print(f"✅ {result['path']}")
    print("(It's supposed to look bad!)")

    if args.open:
        import subprocess
        subprocess.run(["open", str(CONFIG.output_dir)])


if __name__ == "__main__":
    cli()
