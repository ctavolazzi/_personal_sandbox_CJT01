#!/usr/bin/env python3
"""
ImageForge - Unified AI Image Generation Toolkit
=================================================
A robust CLI tool for single or batch image generation across all tools.

Features:
- 🎯 Single or batch generation
- 📊 Progress tracking with ETA
- 📝 Detailed console logging
- ⚡ Rate limiting and retry logic
- 📁 Organized output with manifests
- 🔧 JSON config support for batch jobs

Usage:
  # Single generation
  imageforge quote "Your quote" --author "Author" --theme lofi
  imageforge diagram "A -> B -> C" --type flowchart --theme neon
  imageforge scroll "Ancient text" --style medieval
  imageforge poster "TITLE" "Subtitle" --style demotivational
  imageforge crappy "SALE!!!" --style 90s_web
  imageforge product "Earbuds" --style minimal
  imageforge album "Title" --artist "Artist" --genre synthwave

  # Batch generation
  imageforge batch --config batch.json
  imageforge batch --random 20
  imageforge showcase  # Generate curated showcase

  # List all options
  imageforge list
"""

import os
import sys
import json
import time
import random
import argparse
import logging
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
from enum import Enum

# ============================================================
# LOGGING SETUP
# ============================================================
class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors and emojis."""

    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m',
    }

    EMOJIS = {
        'DEBUG': '🔍',
        'INFO': '✅',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '💀',
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        emoji = self.EMOJIS.get(record.levelname, '')
        reset = self.COLORS['RESET']

        # Add timestamp for non-info messages
        if record.levelname != 'INFO':
            timestamp = datetime.now().strftime('%H:%M:%S')
            record.msg = f"{color}[{timestamp}] {emoji} {record.msg}{reset}"
        else:
            record.msg = f"{color}{emoji} {record.msg}{reset}"

        return super().format(record)


def setup_logging(verbose: bool = False):
    """Configure logging with pretty output."""
    level = logging.DEBUG if verbose else logging.INFO

    logger = logging.getLogger('imageforge')

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    handler = logging.StreamHandler()
    handler.setFormatter(ColoredFormatter('%(message)s'))

    logger.setLevel(level)
    logger.addHandler(handler)
    logger.propagate = False

    return logger


log = setup_logging()


# ============================================================
# CONFIGURATION
# ============================================================
@dataclass
class Config:
    output_dir: Path = Path.home() / "Desktop" / "ImageForge_Output"
    rate_limit_delay: float = 1.0  # Seconds between API calls
    max_retries: int = 3
    retry_delay: float = 10.0  # Seconds to wait on rate limit
    save_manifest: bool = True
    verbose: bool = False


CONFIG = Config()

# Add projects to path
PROJECTS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECTS_DIR))


# ============================================================
# TOOL REGISTRY
# ============================================================
class Tool(Enum):
    QUOTE = "quote"
    DIAGRAM = "diagram"
    SCROLL = "scroll"
    POSTER = "poster"
    CRAPPY = "crappy"
    PRODUCT = "product"
    ALBUM = "album"


TOOL_INFO = {
    Tool.QUOTE: {
        "name": "QuoteCard",
        "emoji": "🎯",
        "description": "Motivational quote graphics",
        "themes": ["minimal", "wizard_matrix", "vaporwave", "cyberpunk", "cottagecore",
                   "dark_academia", "lofi", "studio_ghibli", "ocean", "space", "nature", "retro"],
    },
    Tool.DIAGRAM: {
        "name": "DiagramForge",
        "emoji": "📊",
        "description": "Technical diagrams & flowcharts",
        "types": ["flowchart", "sequence", "architecture", "mindmap", "entity", "timeline", "org"],
        "themes": ["technical", "hand_drawn", "neon", "blueprint", "watercolor", "minimal",
                   "retro", "isometric", "dark_mode", "playful"],
    },
    Tool.SCROLL: {
        "name": "ScrollForge",
        "emoji": "📜",
        "description": "Ancient documents & manuscripts",
        "styles": ["medieval", "egyptian", "alchemist", "pirate", "wizard", "asian", "roman", "lovecraft"],
    },
    Tool.POSTER: {
        "name": "PosterForge",
        "emoji": "🖼️",
        "description": "Motivational & demotivational posters",
        "styles": ["motivational", "demotivational", "propaganda", "vintage", "movie",
                   "concert", "minimalist", "safety"],
    },
    Tool.CRAPPY: {
        "name": "CrappyDesign",
        "emoji": "💀",
        "description": "Intentionally bad 90s design",
        "styles": ["90s_web", "wordart", "clipart_hell", "mall_kiosk", "myspace",
                   "ransom", "powerpoint", "vaporwave_ironic"],
    },
    Tool.PRODUCT: {
        "name": "ProductShot",
        "emoji": "📸",
        "description": "Product photography mockups",
        "styles": ["minimal", "lifestyle", "tech", "flat_lay", "outdoor", "food", "cosmetics", "packaging"],
    },
    Tool.ALBUM: {
        "name": "AlbumArt",
        "emoji": "🎵",
        "description": "Music album covers",
        "genres": ["synthwave", "metal", "hiphop", "lofi", "jazz", "indie", "electronic",
                   "classical", "punk", "rnb", "country", "psychedelic"],
    },
}


# ============================================================
# PROGRESS TRACKER
# ============================================================
class ProgressTracker:
    """Track batch generation progress with ETA."""

    def __init__(self, total: int):
        self.total = total
        self.completed = 0
        self.failed = 0
        self.start_time = time.time()
        self.results = []

    def update(self, success: bool, result: Optional[dict] = None):
        """Update progress after an item completes."""
        if success:
            self.completed += 1
            if result:
                self.results.append(result)
        else:
            self.failed += 1

    @property
    def elapsed(self) -> float:
        return time.time() - self.start_time

    @property
    def eta(self) -> Optional[float]:
        done = self.completed + self.failed
        if done == 0:
            return None
        avg_time = self.elapsed / done
        remaining = self.total - done
        return avg_time * remaining

    @property
    def progress_str(self) -> str:
        done = self.completed + self.failed
        pct = (done / self.total) * 100 if self.total > 0 else 0

        eta_str = ""
        if self.eta:
            mins = int(self.eta // 60)
            secs = int(self.eta % 60)
            eta_str = f" | ETA: {mins}m {secs}s"

        return f"[{done}/{self.total}] {pct:.0f}%{eta_str}"

    def summary(self) -> str:
        elapsed_mins = self.elapsed / 60
        return f"""
{'='*60}
📊 GENERATION COMPLETE
{'='*60}
   ✅ Successful: {self.completed}
   ❌ Failed: {self.failed}
   📁 Total: {self.completed + self.failed}/{self.total}
   ⏱️  Time: {elapsed_mins:.1f} minutes
   📂 Output: {CONFIG.output_dir}
{'='*60}
"""


# ============================================================
# CORE GENERATION FUNCTIONS
# ============================================================
def load_env():
    """Load environment variables."""
    from dotenv import load_dotenv
    load_dotenv()
    load_dotenv(PROJECTS_DIR.parent / ".env")


def ensure_output_dir() -> Path:
    """Ensure output directory exists and return it."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = CONFIG.output_dir / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def generate_with_retry(gen_func, max_retries: int = None, **kwargs) -> Optional[dict]:
    """Execute generation with retry logic."""
    max_retries = max_retries or CONFIG.max_retries

    for attempt in range(max_retries):
        try:
            result = gen_func(**kwargs)
            return result
        except Exception as e:
            error_str = str(e)

            if "429" in error_str or "rate" in error_str.lower():
                wait_time = CONFIG.retry_delay * (attempt + 1)
                log.warning(f"Rate limited. Waiting {wait_time}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            elif "'NoneType'" in error_str:
                log.warning(f"Empty response. Retrying... (attempt {attempt + 1}/{max_retries})")
                time.sleep(2)
            else:
                log.error(f"Generation failed: {e}")
                if attempt < max_retries - 1:
                    log.debug(f"Retrying... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(2)

    return None


def generate_quote(quote: str, author: str, theme: str, output_dir: Path) -> Optional[dict]:
    """Generate a quote card."""
    from quotecard.quotecard import generate_card
    log.debug(f"Generating quote: {theme} - \"{quote[:40]}...\"")
    return generate_with_retry(generate_card, quote=quote, author=author, theme=theme, output_dir=output_dir)


def generate_diagram(description: str, diagram_type: str, theme: str, output_dir: Path) -> Optional[dict]:
    """Generate a diagram."""
    from diagramforge.diagramforge import generate_diagram as gen_diag
    log.debug(f"Generating diagram: {diagram_type}/{theme}")
    return generate_with_retry(gen_diag, description=description, diagram_type=diagram_type, theme=theme, output_dir=output_dir)


def generate_scroll(text: str, style: str, output_dir: Path) -> Optional[dict]:
    """Generate an ancient scroll."""
    from scrollforge.scrollforge import generate_scroll as gen_scroll
    log.debug(f"Generating scroll: {style}")
    return generate_with_retry(gen_scroll, text=text, style=style, output_dir=output_dir)


def generate_poster(title: str, subtitle: str, style: str, output_dir: Path) -> Optional[dict]:
    """Generate a poster."""
    from posterforge.posterforge import generate_poster as gen_poster
    log.debug(f"Generating poster: {style} - {title}")
    return generate_with_retry(gen_poster, title=title, subtitle=subtitle, style=style, output_dir=output_dir)


def generate_crappy(text: str, style: str, output_dir: Path) -> Optional[dict]:
    """Generate intentionally bad design."""
    from crappydesign.crappydesign import generate_bad_design
    log.debug(f"Generating crappy design: {style}")
    return generate_with_retry(generate_bad_design, text=text, style=style, output_dir=output_dir)


def generate_product(product: str, style: str, output_dir: Path) -> Optional[dict]:
    """Generate a product shot."""
    from productshot.productshot import generate_product_shot
    log.debug(f"Generating product shot: {style}")
    return generate_with_retry(generate_product_shot, product=product, style=style, output_dir=output_dir)


def generate_album(title: str, artist: str, genre: str, output_dir: Path) -> Optional[dict]:
    """Generate album artwork."""
    from albumart.albumart import generate_album_art
    log.debug(f"Generating album art: {genre} - {title}")
    return generate_with_retry(generate_album_art, album_title=title, artist=artist, genre=genre, output_dir=output_dir)


# ============================================================
# BATCH GENERATION
# ============================================================
def run_batch(jobs: List[dict], output_dir: Path = None) -> ProgressTracker:
    """Run a batch of generation jobs."""
    load_env()

    output_dir = output_dir or ensure_output_dir()
    tracker = ProgressTracker(len(jobs))

    log.info(f"Starting batch generation: {len(jobs)} items")
    log.info(f"Output directory: {output_dir}")
    print()

    for i, job in enumerate(jobs):
        tool = job.get("tool")
        tool_info = TOOL_INFO.get(Tool(tool), {})
        emoji = tool_info.get("emoji", "🎨")

        print(f"{tracker.progress_str} {emoji} {tool}: ", end="", flush=True)

        result = None
        try:
            if tool == "quote":
                result = generate_quote(
                    job["quote"], job.get("author", "Unknown"),
                    job.get("theme", "minimal"), output_dir
                )
            elif tool == "diagram":
                result = generate_diagram(
                    job["description"], job.get("type", "flowchart"),
                    job.get("theme", "technical"), output_dir
                )
            elif tool == "scroll":
                result = generate_scroll(job["text"], job.get("style", "medieval"), output_dir)
            elif tool == "poster":
                result = generate_poster(
                    job["title"], job.get("subtitle", ""),
                    job.get("style", "motivational"), output_dir
                )
            elif tool == "crappy":
                result = generate_crappy(job["text"], job.get("style", "90s_web"), output_dir)
            elif tool == "product":
                result = generate_product(job["product"], job.get("style", "minimal"), output_dir)
            elif tool == "album":
                result = generate_album(
                    job["title"], job.get("artist"),
                    job.get("genre", "synthwave"), output_dir
                )

            if result:
                print(f"✅ {Path(result.get('path', '')).name}")
                tracker.update(True, result)
            else:
                print("❌ Failed")
                tracker.update(False)

        except Exception as e:
            print(f"❌ {e}")
            tracker.update(False)

        # Rate limiting
        if i < len(jobs) - 1:
            time.sleep(CONFIG.rate_limit_delay)

    # Save manifest
    if CONFIG.save_manifest and tracker.results:
        manifest_path = output_dir / "_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump({
                "generated_at": datetime.now().isoformat(),
                "total": len(jobs),
                "successful": tracker.completed,
                "failed": tracker.failed,
                "items": tracker.results,
            }, f, indent=2, default=str)
        log.info(f"Manifest saved: {manifest_path}")

    print(tracker.summary())
    return tracker


def generate_random_batch(count: int) -> List[dict]:
    """Generate random batch jobs for showcase."""
    jobs = []

    # Sample data
    quotes = [
        ("The only way to do great work is to love what you do.", "Steve Jobs"),
        ("Innovation distinguishes between a leader and a follower.", "Steve Jobs"),
        ("Stay hungry, stay foolish.", "Steve Jobs"),
        ("In the middle of difficulty lies opportunity.", "Albert Einstein"),
        ("The future belongs to those who believe in their dreams.", "Eleanor Roosevelt"),
    ]

    diagrams = [
        "User -> API -> Database -> Response",
        "Frontend, Backend, Database, Cache",
        "Start -> Process -> Decision -> End",
    ]

    scrolls = [
        "Hear ye! The code shall be clean and bugs vanquished.",
        "The sacred recipe for eternal productivity.",
        "X marks the spot where clean architecture lies.",
    ]

    posters = [
        ("TEAMWORK", "Because none of us is as dumb as all of us"),
        ("MEETINGS", "Where progress goes to die"),
        ("DEADLINES", "The ultimate motivator"),
    ]

    crappys = [
        "GRAND OPENING SALE!!!",
        "HAPPY BIRTHDAY!!!",
        "QUARTERLY REPORT",
    ]

    products = [
        "Premium wireless earbuds",
        "Artisan coffee bag",
        "Smartphone with app",
    ]

    albums = [
        ("Neon Nights", "The Midnight"),
        ("Rage Protocol", "Steel Fury"),
        ("Chill Vibes", "Lofi Dreamer"),
    ]

    for _ in range(count):
        tool = random.choice(list(Tool))
        info = TOOL_INFO[tool]

        if tool == Tool.QUOTE:
            q, a = random.choice(quotes)
            jobs.append({"tool": "quote", "quote": q, "author": a, "theme": random.choice(info["themes"])})
        elif tool == Tool.DIAGRAM:
            jobs.append({"tool": "diagram", "description": random.choice(diagrams),
                        "type": random.choice(info["types"]), "theme": random.choice(info["themes"])})
        elif tool == Tool.SCROLL:
            jobs.append({"tool": "scroll", "text": random.choice(scrolls), "style": random.choice(info["styles"])})
        elif tool == Tool.POSTER:
            t, s = random.choice(posters)
            jobs.append({"tool": "poster", "title": t, "subtitle": s, "style": random.choice(info["styles"])})
        elif tool == Tool.CRAPPY:
            jobs.append({"tool": "crappy", "text": random.choice(crappys), "style": random.choice(info["styles"])})
        elif tool == Tool.PRODUCT:
            jobs.append({"tool": "product", "product": random.choice(products), "style": random.choice(info["styles"])})
        elif tool == Tool.ALBUM:
            t, a = random.choice(albums)
            jobs.append({"tool": "album", "title": t, "artist": a, "genre": random.choice(info["genres"])})

    return jobs


# ============================================================
# CLI
# ============================================================
def cmd_list(args):
    """List all available tools and options."""
    print("\n" + "=" * 60)
    print("🎨 IMAGEFORGE TOOLKIT")
    print("=" * 60 + "\n")

    for tool, info in TOOL_INFO.items():
        print(f"{info['emoji']} {info['name']} ({tool.value})")
        print(f"   {info['description']}")

        if "themes" in info:
            print(f"   Themes: {', '.join(info['themes'][:5])}...")
        if "types" in info:
            print(f"   Types: {', '.join(info['types'])}")
        if "styles" in info:
            print(f"   Styles: {', '.join(info['styles'])}")
        if "genres" in info:
            print(f"   Genres: {', '.join(info['genres'][:5])}...")
        print()


def cmd_single(args):
    """Handle single generation commands."""
    load_env()
    output_dir = ensure_output_dir()

    tool = args.tool
    result = None

    log.info(f"Generating {tool}...")

    if tool == "quote":
        result = generate_quote(args.text, args.author, args.theme, output_dir)
    elif tool == "diagram":
        result = generate_diagram(args.text, args.type, args.theme, output_dir)
    elif tool == "scroll":
        result = generate_scroll(args.text, args.style, output_dir)
    elif tool == "poster":
        result = generate_poster(args.text, args.subtitle or "", args.style, output_dir)
    elif tool == "crappy":
        result = generate_crappy(args.text, args.style, output_dir)
    elif tool == "product":
        result = generate_product(args.text, args.style, output_dir)
    elif tool == "album":
        result = generate_album(args.text, args.artist, args.genre, output_dir)

    if result:
        log.info(f"Generated: {result.get('path')}")
        if args.open:
            import subprocess
            subprocess.run(["open", str(output_dir)])
    else:
        log.error("Generation failed")


def cmd_batch(args):
    """Handle batch generation."""
    if args.config:
        with open(args.config) as f:
            jobs = json.load(f)
    elif args.random:
        jobs = generate_random_batch(args.random)
    else:
        log.error("Specify --config FILE or --random COUNT")
        return

    output_dir = Path(args.output) if args.output else None
    tracker = run_batch(jobs, output_dir)

    if args.open and tracker.completed > 0:
        import subprocess
        subprocess.run(["open", str(CONFIG.output_dir)])


def main():
    parser = argparse.ArgumentParser(
        description="ImageForge - Unified AI Image Generation Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--open", action="store_true", help="Open output folder when done")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # List command
    subparsers.add_parser("list", help="List all tools and options")

    # Single generation commands
    for tool in Tool:
        info = TOOL_INFO[tool]
        p = subparsers.add_parser(tool.value, help=info["description"])
        p.add_argument("text", help="Main text/content")

        if tool == Tool.QUOTE:
            p.add_argument("--author", "-a", default="Unknown")
            p.add_argument("--theme", "-t", default="minimal", choices=info["themes"])
        elif tool == Tool.DIAGRAM:
            p.add_argument("--type", "-t", default="flowchart", choices=info["types"])
            p.add_argument("--theme", "-s", default="technical", choices=info["themes"])
        elif tool == Tool.SCROLL:
            p.add_argument("--style", "-s", default="medieval", choices=info["styles"])
        elif tool == Tool.POSTER:
            p.add_argument("--subtitle", "-sub", default="")
            p.add_argument("--style", "-s", default="motivational", choices=info["styles"])
        elif tool == Tool.CRAPPY:
            p.add_argument("--style", "-s", default="90s_web", choices=info["styles"])
        elif tool == Tool.PRODUCT:
            p.add_argument("--style", "-s", default="minimal", choices=info["styles"])
        elif tool == Tool.ALBUM:
            p.add_argument("--artist", "-a", default=None)
            p.add_argument("--genre", "-g", default="synthwave", choices=info["genres"])

        p.set_defaults(tool=tool.value)

    # Batch command
    batch_p = subparsers.add_parser("batch", help="Batch generation from config or random")
    batch_p.add_argument("--config", "-c", help="JSON config file with jobs")
    batch_p.add_argument("--random", "-r", type=int, help="Generate N random images")
    batch_p.add_argument("--output", "-o", help="Output directory")

    args = parser.parse_args()

    if args.verbose:
        CONFIG.verbose = True
        global log
        log = setup_logging(verbose=True)

    if not args.command:
        parser.print_help()
        return

    if args.command == "list":
        cmd_list(args)
    elif args.command == "batch":
        cmd_batch(args)
    else:
        cmd_single(args)


if __name__ == "__main__":
    main()
