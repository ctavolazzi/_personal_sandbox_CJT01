#!/usr/bin/env python3
"""
ImageForge Toolkit Showcase Generator
=====================================
Generate 40 diverse examples showcasing all tools and styles.
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime

# Add projects to path
PROJECTS = Path(__file__).parent
sys.path.insert(0, str(PROJECTS))

from dotenv import load_dotenv
load_dotenv(PROJECTS.parent / ".env")

# Output folder
SHOWCASE_DIR = Path.home() / "Desktop" / "ImageForge_Showcase"
SHOWCASE_DIR.mkdir(parents=True, exist_ok=True)

# Track progress
generated = 0
failed = 0

def progress(tool, desc):
    global generated
    generated += 1
    print(f"[{generated}/40] {tool}: {desc}")

def gen_quote(quote, author, theme):
    from quotecard.quotecard import generate_card
    progress("QuoteCard", f"{theme} - \"{quote[:30]}...\"")
    return generate_card(quote, author, theme, output_dir=SHOWCASE_DIR)

def gen_diagram(desc, dtype, theme):
    from diagramforge.diagramforge import generate_diagram
    progress("DiagramForge", f"{dtype}/{theme}")
    return generate_diagram(desc, dtype, theme, output_dir=SHOWCASE_DIR)

def gen_scroll(text, style):
    from scrollforge.scrollforge import generate_scroll
    progress("ScrollForge", f"{style}")
    return generate_scroll(text, style, output_dir=SHOWCASE_DIR)

def gen_poster(title, subtitle, style):
    from posterforge.posterforge import generate_poster
    progress("PosterForge", f"{style} - {title}")
    return generate_poster(title, subtitle, style, output_dir=SHOWCASE_DIR)

def gen_crappy(text, style):
    from crappydesign.crappydesign import generate_bad_design
    progress("CrappyDesign", f"{style}")
    return generate_bad_design(text, style, output_dir=SHOWCASE_DIR)

def gen_product(product, style):
    from productshot.productshot import generate_product_shot
    progress("ProductShot", f"{style}")
    return generate_product_shot(product, style, output_dir=SHOWCASE_DIR)

def gen_album(title, artist, genre):
    from albumart.albumart import generate_album_art
    progress("AlbumArt", f"{genre} - {title}")
    return generate_album_art(title, artist, genre, output_dir=SHOWCASE_DIR)

def main():
    global failed

    print("=" * 60)
    print("🎨 IMAGEFORGE TOOLKIT SHOWCASE")
    print("   Generating 40 diverse examples")
    print(f"   Output: {SHOWCASE_DIR}")
    print("=" * 60)
    print()

    examples = [
        # === QUOTECARD (6) ===
        lambda: gen_quote("The only way to do great work is to love what you do.", "Steve Jobs", "minimal"),
        lambda: gen_quote("In the middle of difficulty lies opportunity.", "Albert Einstein", "wizard_matrix"),
        lambda: gen_quote("Stay hungry, stay foolish.", "Steve Jobs", "vaporwave"),
        lambda: gen_quote("The future belongs to those who believe in the beauty of their dreams.", "Eleanor Roosevelt", "lofi"),
        lambda: gen_quote("It does not matter how slowly you go as long as you do not stop.", "Confucius", "studio_ghibli"),
        lambda: gen_quote("Innovation distinguishes between a leader and a follower.", "Steve Jobs", "cyberpunk"),

        # === DIAGRAMFORGE (6) ===
        lambda: gen_diagram("User Request -> Load Balancer -> API Server -> Database -> Response", "flowchart", "neon"),
        lambda: gen_diagram("Frontend React, API Gateway, Auth Service, User Service, PostgreSQL, Redis Cache", "architecture", "blueprint"),
        lambda: gen_diagram("Machine Learning: Supervised Learning, Unsupervised Learning, Reinforcement Learning, Deep Learning", "mindmap", "watercolor"),
        lambda: gen_diagram("Client sends request, Server authenticates, Database query, Return response", "sequence", "technical"),
        lambda: gen_diagram("CEO, CTO, CFO, Engineering Team, Product Team, Sales Team", "org", "minimal"),
        lambda: gen_diagram("Start -> Input Data -> Process -> Decision -> Output or Retry", "flowchart", "hand_drawn"),

        # === SCROLLFORGE (6) ===
        lambda: gen_scroll("Hear ye, hear ye! Let it be known throughout the realm that the code shall be clean and the bugs shall be vanquished.", "medieval"),
        lambda: gen_scroll("In the year of our machines, the great algorithm awakened and brought forth wisdom unto the developers.", "wizard"),
        lambda: gen_scroll("The sacred recipe for the Elixir of Productivity: One part coffee, two parts determination, and a sprinkle of debugging.", "alchemist"),
        lambda: gen_scroll("X marks the spot where the treasure of clean architecture lies buried beneath layers of technical debt.", "pirate"),
        lambda: gen_scroll("The path to enlightenment begins with a single commit. Let your code flow like water.", "asian"),
        lambda: gen_scroll("By decree of the Emperor: All citizens shall write tests before implementation. So it is written, so it shall be done.", "roman"),

        # === POSTERFORGE (6) ===
        lambda: gen_poster("TEAMWORK", "Because none of us is as dumb as all of us", "demotivational"),
        lambda: gen_poster("PERSEVERANCE", "The summit is just one step away", "motivational"),
        lambda: gen_poster("CODE REVIEW", "Where friendships go to die", "demotivational"),
        lambda: gen_poster("INNOVATION", "Building tomorrow, today", "propaganda"),
        lambda: gen_poster("DEBUGGING", "It's not a bug, it's an undocumented feature", "vintage"),
        lambda: gen_poster("DEADLINE", "Coming soon to a stressed developer near you", "movie"),

        # === CRAPPYDESIGN (6) ===
        lambda: gen_crappy("GRAND OPENING SALE!!! 50% OFF EVERYTHING!!!", "90s_web"),
        lambda: gen_crappy("HAPPY BIRTHDAY JENNIFER!!!", "wordart"),
        lambda: gen_crappy("QUARTERLY BUSINESS SYNERGY REPORT", "clipart_hell"),
        lambda: gen_crappy("HUGE MATTRESS LIQUIDATION EVENT", "mall_kiosk"),
        lambda: gen_crappy("~*~ThAnKs FoR tHe AdD~*~", "myspace"),
        lambda: gen_crappy("Q3 STRATEGIC INITIATIVES OVERVIEW", "powerpoint"),

        # === PRODUCTSHOT (5) ===
        lambda: gen_product("Premium wireless earbuds in white charging case", "minimal"),
        lambda: gen_product("Artisan coffee bag, dark roast, kraft paper packaging", "lifestyle"),
        lambda: gen_product("Smartphone showing fitness app interface", "tech"),
        lambda: gen_product("Organic skincare set with botanical ingredients", "cosmetics"),
        lambda: gen_product("Craft beer bottle, amber ale, condensation droplets", "food"),

        # === ALBUMART (5) ===
        lambda: gen_album("Neon Nights", "The Midnight", "synthwave"),
        lambda: gen_album("Rage Protocol", "Steel Fury", "metal"),
        lambda: gen_album("Rainy Day Studies", "Lofi Dreamer", "lofi"),
        lambda: gen_album("Electric Dreams", "Voltage", "electronic"),
        lambda: gen_album("Cosmic Journey", "Astral Projections", "psychedelic"),
    ]

    print(f"Starting generation of {len(examples)} images...\n")
    start_time = time.time()

    for i, gen_func in enumerate(examples):
        try:
            gen_func()
            time.sleep(1)  # Small delay to avoid rate limiting
        except Exception as e:
            failed += 1
            print(f"   ❌ Error: {e}")

    elapsed = time.time() - start_time

    print()
    print("=" * 60)
    print(f"🎉 SHOWCASE COMPLETE!")
    print(f"   ✅ Generated: {generated - failed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   ⏱️  Time: {elapsed/60:.1f} minutes")
    print(f"   📂 Location: {SHOWCASE_DIR}")
    print("=" * 60)

    # Open folder
    import subprocess
    subprocess.run(["open", str(SHOWCASE_DIR)])


if __name__ == "__main__":
    main()
