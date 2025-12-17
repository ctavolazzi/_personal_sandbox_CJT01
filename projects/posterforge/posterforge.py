"""
PosterForge - Motivational & Demotivational Poster Generator
=============================================================
Create classic motivational posters, demotivational parodies, and propaganda.

Usage:
  posterforge "TEAMWORK" "Because none of us is as dumb as all of us" --style demotivational
  posterforge "BELIEVE" "You can achieve anything" --style motivational
  posterforge "VICTORY" "For the motherland" --style propaganda
"""

import os
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

@dataclass
class Config:
    output_dir: Path = Path.home() / "Desktop" / "PosterForge"

CONFIG = Config()

STYLES = {
    "motivational": {
        "name": "Classic Motivational",
        "emoji": "🌟",
        "style": """
            Style: Classic corporate motivational poster
            Background: Dramatic nature photograph (mountains, sunset, eagle, ocean)
            Frame: Thin black border with generous black matting
            Title: Large white serif text, all caps, centered at bottom
            Subtitle: Smaller italic white text below title
            Mood: Inspiring, uplifting, corporate conference room appropriate
            Image: Majestic natural scene or person achieving something
        """,
    },
    "demotivational": {
        "name": "Demotivational Parody",
        "emoji": "😐",
        "style": """
            Style: Demotivational poster parody (Despair.com style)
            Background: Ironic or mundane photograph
            Frame: Thick black border with wide black matting
            Title: Large white serif text, all caps, centered at bottom
            Subtitle: Smaller italic white text with sarcastic/cynical message
            Mood: Dry humor, corporate satire, existential dread
            Image: Mundane office scene, failure moment, or ironic juxtaposition
        """,
    },
    "propaganda": {
        "name": "Propaganda Poster",
        "emoji": "📢",
        "style": """
            Style: Bold propaganda poster (WW2/Soviet/Art Deco era)
            Colors: Bold red, black, white, gold - high contrast
            Art: Strong graphic illustration, heroic figures
            Text: Bold sans-serif, dramatic angles, exclamation points
            Elements: Rays of light, pointing fingers, determined faces
            Mood: Urgent, patriotic, call to action
        """,
    },
    "vintage": {
        "name": "Vintage Advertisement",
        "emoji": "📻",
        "style": """
            Style: 1950s vintage advertisement poster
            Colors: Muted pastels, cream backgrounds, red accents
            Art: Retro illustration style, happy families, atomic age
            Text: Vintage hand-lettered fonts, friendly and enthusiastic
            Elements: Starbursts, pointing hands, happy housewives
            Mood: Nostalgic, optimistic, wholesome Americana
        """,
    },
    "movie": {
        "name": "Movie Poster",
        "emoji": "🎬",
        "style": """
            Style: Dramatic Hollywood movie poster
            Colors: Dark moody backgrounds with dramatic lighting
            Art: Photorealistic or painterly hero shots
            Text: Big bold title, tagline, credits at bottom
            Elements: Lens flares, dramatic poses, ensemble cast layout
            Mood: Epic, cinematic, blockbuster energy
        """,
    },
    "concert": {
        "name": "Concert/Gig Poster",
        "emoji": "🎸",
        "style": """
            Style: Rock concert poster / gig flyer
            Colors: High contrast, neon accents, black backgrounds
            Art: Psychedelic, hand-drawn, screen print aesthetic
            Text: Bold distorted fonts, DIY punk aesthetic
            Elements: Skulls, flames, guitars, abstract shapes
            Mood: Underground, edgy, indie rock energy
        """,
    },
    "minimalist": {
        "name": "Minimalist",
        "emoji": "⬜",
        "style": """
            Style: Modern minimalist poster
            Colors: Limited palette, lots of white space
            Art: Simple geometric shapes, clean lines
            Text: Clean sans-serif, precise placement
            Elements: Single focal point, breathing room
            Mood: Sophisticated, gallery-worthy, design-forward
        """,
    },
    "safety": {
        "name": "Workplace Safety",
        "emoji": "⚠️",
        "style": """
            Style: Industrial workplace safety poster
            Colors: Yellow warning, red danger, industrial blue
            Art: Simple icons, warning symbols, stick figures
            Text: Bold clear warnings, easy to read from distance
            Elements: Hazard symbols, PPE illustrations, accident prevention
            Mood: Serious, informative, OSHA-compliant
        """,
    },
}


def generate_poster(
    title: str,
    subtitle: str = "",
    style: str = "motivational",
    image_hint: str = None,
    output_dir: Path = None,
) -> dict:
    """Generate a poster with title and subtitle."""
    from google import genai
    from google.genai import types
    from dotenv import load_dotenv
    load_dotenv()

    if style not in STYLES:
        raise ValueError(f"Unknown style: {style}. Options: {list(STYLES.keys())}")

    style_data = STYLES[style]
    output_dir = Path(output_dir) if output_dir else CONFIG.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    prompt = f"""Create a {style_data['name']} poster:

TITLE (large text): {title}
SUBTITLE (smaller text below): {subtitle if subtitle else '[no subtitle]'}
{f'IMAGE SUBJECT HINT: {image_hint}' if image_hint else ''}

STYLE:
{style_data['style']}

REQUIREMENTS:
- Title text must be clearly readable and prominent
- Subtitle should be readable but secondary
- Follow the classic format for this poster type
- Make it look professional and authentic to the style
- Portrait orientation (taller than wide)
"""

    slug = title[:20].replace(' ', '_')
    slug = ''.join(c for c in slug if c.isalnum() or c == '_')
    timestamp = datetime.now().strftime("%H%M%S")
    filename = f"poster_{style}_{slug}_{timestamp}.png"
    output_path = output_dir / filename

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_modalities=['IMAGE'],
                image_config=types.ImageConfig(aspect_ratio="9:16")
            )
        )

        for part in response.parts:
            if part.inline_data is not None:
                with open(output_path, "wb") as f:
                    f.write(part.inline_data.data)
                return {
                    "path": str(output_path),
                    "title": title,
                    "subtitle": subtitle,
                    "style": style,
                }
        raise Exception("No image generated")

    except Exception as e:
        if "429" in str(e):
            import time
            time.sleep(10)
            return generate_poster(title, subtitle, style, image_hint, output_dir)
        raise


def list_styles() -> dict:
    return {k: {"name": v["name"], "emoji": v["emoji"]} for k, v in STYLES.items()}


def cli():
    import argparse
    from dotenv import load_dotenv
    load_dotenv()

    parser = argparse.ArgumentParser(description="PosterForge - Motivational Poster Generator")
    parser.add_argument("title", nargs="?", help="Main title (big text)")
    parser.add_argument("subtitle", nargs="?", default="", help="Subtitle (small text)")
    parser.add_argument("--style", "-s", default="motivational")
    parser.add_argument("--image", "-i", help="Hint for background image")
    parser.add_argument("--output", "-o")
    parser.add_argument("--list-styles", action="store_true")
    parser.add_argument("--open", action="store_true")

    args = parser.parse_args()

    if args.list_styles:
        print("\n🖼️ POSTER STYLES:\n")
        for key, info in list_styles().items():
            print(f"  {info['emoji']} {key:15} - {info['name']}")
        print()
        return

    if not args.title:
        parser.print_help()
        return

    if args.output:
        CONFIG.output_dir = Path(args.output)

    print(f"🖼️ Generating {args.style} poster...")
    result = generate_poster(args.title, args.subtitle, args.style, args.image)
    print(f"✅ {result['path']}")

    if args.open:
        import subprocess
        subprocess.run(["open", str(CONFIG.output_dir)])


if __name__ == "__main__":
    cli()
