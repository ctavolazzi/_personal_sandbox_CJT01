"""
AlbumArt - Music Album Cover Generator
======================================
Generate album artwork in various musical genre styles.

Usage:
  albumart "Midnight Dreams" --artist "The Echoes" --genre synthwave
  albumart "Raw Power" --artist "Steel Thunder" --genre metal
  albumart "Summer Vibes" --genre lofi
"""

import os
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

@dataclass
class Config:
    output_dir: Path = Path.home() / "Desktop" / "AlbumArt"

CONFIG = Config()

GENRES = {
    "synthwave": {
        "name": "Synthwave/Retrowave",
        "emoji": "🌆",
        "style": """
            Style: 80s synthwave album cover
            Colors: Neon pink, cyan, purple gradients on dark background
            Elements: Grid landscapes, palm trees, sports cars, sunset
            Typography: Chrome 3D text, neon glow effects
            Mood: Nostalgic, futuristic, nighttime cruising
        """,
    },
    "metal": {
        "name": "Heavy Metal",
        "emoji": "🤘",
        "style": """
            Style: Classic heavy metal album cover
            Colors: Dark, fire oranges, blood reds, steel grays
            Elements: Skulls, demons, fire, chains, gothic imagery
            Typography: Angular metal font, chrome or blood drip effects
            Mood: Aggressive, dark, powerful, epic fantasy
        """,
    },
    "hiphop": {
        "name": "Hip Hop/Rap",
        "emoji": "🎤",
        "style": """
            Style: Modern hip hop album aesthetic
            Colors: Bold contrasts, gold/platinum accents, brand colors
            Elements: Urban imagery, luxury items, portrait style, symbolic objects
            Typography: Bold modern sans-serif, street art influence
            Mood: Confident, luxurious, street credibility
        """,
    },
    "lofi": {
        "name": "Lo-Fi/Chill",
        "emoji": "🎧",
        "style": """
            Style: Lo-fi hip hop / chillhop cover
            Colors: Warm muted tones, sunset palettes, soft purples
            Elements: Anime-style girl studying, cozy rooms, rain on windows
            Typography: Soft rounded fonts, handwritten elements
            Mood: Calm, nostalgic, study vibes, rainy day
        """,
    },
    "jazz": {
        "name": "Jazz",
        "emoji": "🎷",
        "style": """
            Style: Classic Blue Note style jazz cover
            Colors: Limited palette - blue, orange, black, white
            Elements: Abstract shapes, musician silhouettes, instruments
            Typography: Bold sans-serif, Reid Miles inspired
            Mood: Cool, sophisticated, improvisational
        """,
    },
    "indie": {
        "name": "Indie/Alternative",
        "emoji": "🎸",
        "style": """
            Style: Indie rock album aesthetic
            Colors: Desaturated, film photography feel
            Elements: Candid photography, nature, abstract art, collage
            Typography: Understated, vintage typewriter, hand-lettered
            Mood: Authentic, artistic, introspective, DIY
        """,
    },
    "electronic": {
        "name": "Electronic/EDM",
        "emoji": "🎹",
        "style": """
            Style: Modern electronic music cover
            Colors: Vibrant neons, UV reactive, digital gradients
            Elements: Abstract geometry, glitch art, visualizer graphics
            Typography: Futuristic sans-serif, minimal
            Mood: Energetic, futuristic, club-ready
        """,
    },
    "classical": {
        "name": "Classical/Orchestral",
        "emoji": "🎻",
        "style": """
            Style: Classical music album elegance
            Colors: Rich golds, deep burgundy, cream, black
            Elements: Ornate frames, concert halls, instruments, composers
            Typography: Elegant serif, gold foil effect
            Mood: Sophisticated, timeless, prestigious
        """,
    },
    "punk": {
        "name": "Punk Rock",
        "emoji": "💀",
        "style": """
            Style: DIY punk rock aesthetic
            Colors: High contrast black/white, safety orange, hot pink
            Elements: Ransom note letters, xerox texture, hand-drawn
            Typography: Cut out letters, stencil, graffiti
            Mood: Rebellious, raw, anti-establishment, DIY
        """,
    },
    "rnb": {
        "name": "R&B/Soul",
        "emoji": "💜",
        "style": """
            Style: Contemporary R&B album cover
            Colors: Rich purples, golds, sensual lighting
            Elements: Intimate portraits, luxury settings, soft focus
            Typography: Elegant script or modern sans-serif
            Mood: Sensual, smooth, emotional, intimate
        """,
    },
    "country": {
        "name": "Country/Americana",
        "emoji": "🤠",
        "style": """
            Style: Country/Americana album aesthetic
            Colors: Warm earth tones, sunset oranges, denim blues
            Elements: Landscapes, trucks, rural scenes, authentic portraits
            Typography: Western fonts, vintage Americana
            Mood: Authentic, storytelling, heartland pride
        """,
    },
    "psychedelic": {
        "name": "Psychedelic",
        "emoji": "🌀",
        "style": """
            Style: 60s/70s psychedelic rock aesthetic
            Colors: Acid colors, rainbow gradients, tie-dye
            Elements: Melting shapes, fractals, cosmic imagery, mushrooms
            Typography: Wavy art nouveau, liquid letters
            Mood: Trippy, expansive, mind-bending, cosmic
        """,
    },
}


def generate_album_art(
    album_title: str,
    artist: str = None,
    genre: str = "synthwave",
    mood: str = None,
    output_dir: Path = None,
) -> dict:
    """Generate album cover artwork."""
    from google import genai
    from google.genai import types
    from dotenv import load_dotenv
    load_dotenv()

    if genre not in GENRES:
        raise ValueError(f"Unknown genre: {genre}. Options: {list(GENRES.keys())}")

    genre_data = GENRES[genre]
    output_dir = Path(output_dir) if output_dir else CONFIG.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    prompt = f"""Create a music album cover:

ALBUM TITLE: {album_title}
{f'ARTIST NAME: {artist}' if artist else ''}

GENRE STYLE: {genre_data['name']}
{genre_data['style']}

{f'ADDITIONAL MOOD: {mood}' if mood else ''}

REQUIREMENTS:
- Create a professional album cover design
- Include the album title text prominently
{f'- Include artist name: {artist}' if artist else ''}
- Square format (standard album cover)
- Make it visually striking and genre-appropriate
- Should look like a real album you'd see on Spotify/Apple Music
- Text must be readable and well-designed
"""

    slug = album_title[:20].replace(' ', '_')
    slug = ''.join(c for c in slug if c.isalnum() or c == '_')
    timestamp = datetime.now().strftime("%H%M%S")
    filename = f"album_{genre}_{slug}_{timestamp}.png"
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
                    "title": album_title,
                    "artist": artist,
                    "genre": genre,
                }
        raise Exception("No image generated")

    except Exception as e:
        if "429" in str(e):
            import time
            time.sleep(10)
            return generate_album_art(album_title, artist, genre, mood, output_dir)
        raise


def list_genres() -> dict:
    return {k: {"name": v["name"], "emoji": v["emoji"]} for k, v in GENRES.items()}


def cli():
    import argparse
    from dotenv import load_dotenv
    load_dotenv()

    parser = argparse.ArgumentParser(description="AlbumArt - Music Album Cover Generator")
    parser.add_argument("title", nargs="?", help="Album title")
    parser.add_argument("--artist", "-a", help="Artist name")
    parser.add_argument("--genre", "-g", default="synthwave")
    parser.add_argument("--mood", "-m", help="Additional mood/vibe")
    parser.add_argument("--output", "-o")
    parser.add_argument("--list-genres", action="store_true")
    parser.add_argument("--open", action="store_true")

    args = parser.parse_args()

    if args.list_genres:
        print("\n🎵 MUSIC GENRES:\n")
        for key, info in list_genres().items():
            print(f"  {info['emoji']} {key:15} - {info['name']}")
        print()
        return

    if not args.title:
        parser.print_help()
        return

    if args.output:
        CONFIG.output_dir = Path(args.output)

    print(f"🎵 Generating {args.genre} album cover...")
    result = generate_album_art(args.title, args.artist, args.genre, args.mood)
    print(f"✅ {result['path']}")

    if args.open:
        import subprocess
        subprocess.run(["open", str(CONFIG.output_dir)])


if __name__ == "__main__":
    cli()
