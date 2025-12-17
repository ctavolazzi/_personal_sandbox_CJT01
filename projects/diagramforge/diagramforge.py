"""
DiagramForge - AI-Powered Diagram Generator
============================================
Generate beautiful, themed diagrams from Mermaid syntax or plain text.

Features:
- Input: Mermaid code OR plain English description
- Multiple diagram types: Flowchart, Sequence, Architecture, Mind Map
- Visual themes: Technical, Hand-drawn, Neon, Blueprint, Watercolor
- CLI + MCP server support

Usage:
  diagramforge "User logs in -> Auth check -> Dashboard" --type flowchart --theme neon
  diagramforge --mermaid "graph TD; A-->B; B-->C" --theme blueprint
  diagramforge --describe "API architecture with frontend, backend, database" --theme technical
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from dataclasses import dataclass

# ============================================================
# CONFIGURATION
# ============================================================
@dataclass
class DiagramConfig:
    output_dir: Path = Path.home() / "Desktop" / "DiagramForge"
    default_theme: str = "technical"
    default_type: str = "flowchart"
    image_size: str = "1:1"  # or "16:9" for wide diagrams


CONFIG = DiagramConfig()


# ============================================================
# DIAGRAM TYPES
# ============================================================
DIAGRAM_TYPES = {
    "flowchart": {
        "name": "Flowchart",
        "emoji": "🔀",
        "description": "Process flows, decision trees, workflows",
        "prompt_hint": "boxes connected by arrows showing process flow, decision diamonds, start/end ovals",
    },
    "sequence": {
        "name": "Sequence Diagram",
        "emoji": "↔️",
        "description": "Interactions between entities over time",
        "prompt_hint": "vertical lifelines for each actor, horizontal arrows showing messages between them, time flows downward",
    },
    "architecture": {
        "name": "Architecture Diagram",
        "emoji": "🏗️",
        "description": "System components and connections",
        "prompt_hint": "system components as boxes/icons, databases as cylinders, clouds for services, arrows for data flow",
    },
    "mindmap": {
        "name": "Mind Map",
        "emoji": "🧠",
        "description": "Ideas branching from central concept",
        "prompt_hint": "central topic in middle, branches radiating outward, sub-branches for details, organic flowing connections",
    },
    "entity": {
        "name": "Entity Relationship",
        "emoji": "🔗",
        "description": "Database tables and relationships",
        "prompt_hint": "rectangular tables with field names, crow's foot notation for relationships, primary keys highlighted",
    },
    "timeline": {
        "name": "Timeline",
        "emoji": "📅",
        "description": "Events over time",
        "prompt_hint": "horizontal or vertical line with events marked at points, dates/labels, milestone markers",
    },
    "org": {
        "name": "Org Chart",
        "emoji": "👥",
        "description": "Organizational hierarchy",
        "prompt_hint": "hierarchical boxes connected vertically, CEO at top, departments below, reporting lines",
    },
}


# ============================================================
# VISUAL THEMES
# ============================================================
THEMES = {
    "technical": {
        "name": "Technical",
        "emoji": "⚙️",
        "style": """
            Style: Clean technical diagram, professional documentation quality
            Colors: Blues, grays, white backgrounds, subtle gradients
            Lines: Crisp straight lines, proper arrows, clean connectors
            Text: Sans-serif fonts, clear labels, proper spacing
            Overall: Like a well-made technical specification diagram
        """,
    },
    "hand_drawn": {
        "name": "Hand Drawn",
        "emoji": "✏️",
        "style": """
            Style: Sketchy hand-drawn whiteboard aesthetic
            Colors: Black lines on white/cream, maybe blue or red accents
            Lines: Slightly wobbly, imperfect but charming, marker-like
            Text: Handwritten font style, casual but readable
            Overall: Like someone drew it on a whiteboard during a meeting
        """,
    },
    "neon": {
        "name": "Neon Glow",
        "emoji": "💫",
        "style": """
            Style: Cyberpunk neon glow aesthetic
            Colors: Bright cyan, magenta, electric blue on dark background
            Lines: Glowing neon tubes, light bloom effects
            Text: Neon sign style, glowing edges
            Overall: Like a futuristic holographic display
        """,
    },
    "blueprint": {
        "name": "Blueprint",
        "emoji": "📐",
        "style": """
            Style: Architectural blueprint aesthetic
            Colors: White lines on deep blue background, classic blueprint
            Lines: Precise technical drawing style, measurement marks
            Text: Technical stencil font, engineering notation
            Overall: Like an architect's technical drawing
        """,
    },
    "watercolor": {
        "name": "Watercolor",
        "emoji": "🎨",
        "style": """
            Style: Soft watercolor illustration
            Colors: Soft pastels, watercolor washes, organic bleeds
            Lines: Soft edges, painterly strokes, artistic flow
            Text: Elegant script or soft sans-serif
            Overall: Like a beautiful hand-painted illustration
        """,
    },
    "minimal": {
        "name": "Minimal",
        "emoji": "⬜",
        "style": """
            Style: Ultra-minimal, clean white space
            Colors: Black on white, maybe one accent color
            Lines: Thin precise lines, lots of negative space
            Text: Modern minimal sans-serif, small and elegant
            Overall: Apple-style minimalist design documentation
        """,
    },
    "retro": {
        "name": "Retro Computing",
        "emoji": "💾",
        "style": """
            Style: 1980s computer graphics aesthetic
            Colors: Green/amber on black, CRT monitor colors
            Lines: Pixelated edges, scanlines, low-res charm
            Text: Monospace pixel font, DOS/terminal style
            Overall: Like an old computer terminal or vintage software
        """,
    },
    "isometric": {
        "name": "Isometric 3D",
        "emoji": "📦",
        "style": """
            Style: 3D isometric projection
            Colors: Bright colors, clean gradients, subtle shadows
            Lines: 30-degree angles, 3D depth illusion
            Text: Floating labels, perspective-aware
            Overall: Like a modern infographic with 3D elements
        """,
    },
    "dark_mode": {
        "name": "Dark Mode",
        "emoji": "🌙",
        "style": """
            Style: Modern dark theme UI
            Colors: Dark grays, subtle blues, white text, accent colors
            Lines: Clean with subtle glow, modern UI style
            Text: Clean sans-serif, high contrast on dark
            Overall: Like a modern dark-mode application interface
        """,
    },
    "playful": {
        "name": "Playful",
        "emoji": "🎪",
        "style": """
            Style: Fun, cartoon-like illustration
            Colors: Bright primary colors, cheerful palette
            Lines: Rounded corners, bouncy shapes, friendly
            Text: Rounded friendly fonts, maybe with shadows
            Overall: Like a fun educational illustration for kids
        """,
    },
}


# ============================================================
# CORE FUNCTIONS
# ============================================================
def get_gemini_client():
    """Lazy load Gemini client."""
    from google import genai
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")
    return genai.Client(api_key=api_key)


def parse_mermaid_to_description(mermaid_code: str) -> str:
    """Convert Mermaid syntax to plain English for AI."""
    # Basic parsing - AI will handle the rest
    lines = mermaid_code.strip().split('\n')

    # Detect diagram type
    first_line = lines[0].lower() if lines else ""
    if "graph" in first_line or "flowchart" in first_line:
        diagram_type = "flowchart"
    elif "sequencediagram" in first_line.replace(" ", ""):
        diagram_type = "sequence diagram"
    elif "erdiagram" in first_line.replace(" ", ""):
        diagram_type = "entity relationship diagram"
    elif "classDiagram" in first_line:
        diagram_type = "class diagram"
    else:
        diagram_type = "diagram"

    return f"""
    This is a {diagram_type} defined in Mermaid syntax:

    ```mermaid
    {mermaid_code}
    ```

    Please interpret this Mermaid diagram and create a visual representation.
    Parse the nodes, connections, and relationships accurately.
    """


def generate_diagram(
    description: str,
    diagram_type: str = "flowchart",
    theme: str = "technical",
    mermaid_code: Optional[str] = None,
    output_dir: Optional[Path] = None,
    filename: Optional[str] = None,
    aspect_ratio: str = "1:1",
) -> dict:
    """
    Generate a diagram image using AI.

    Args:
        description: Plain text description of the diagram
        diagram_type: Type of diagram (flowchart, sequence, etc.)
        theme: Visual theme
        mermaid_code: Optional Mermaid syntax to interpret
        output_dir: Where to save
        filename: Custom filename
        aspect_ratio: "1:1" (square) or "16:9" (wide)

    Returns:
        dict with path, description, type, theme
    """
    from google.genai import types
    from dotenv import load_dotenv
    load_dotenv()

    # Validate inputs
    if diagram_type not in DIAGRAM_TYPES:
        raise ValueError(f"Unknown diagram type: {diagram_type}. Options: {list(DIAGRAM_TYPES.keys())}")
    if theme not in THEMES:
        raise ValueError(f"Unknown theme: {theme}. Options: {list(THEMES.keys())}")

    dtype = DIAGRAM_TYPES[diagram_type]
    theme_data = THEMES[theme]

    # Setup output
    output_dir = Path(output_dir) if output_dir else CONFIG.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build prompt
    if mermaid_code:
        content_desc = parse_mermaid_to_description(mermaid_code)
    else:
        content_desc = f"Create a {dtype['name']} diagram showing: {description}"

    prompt = f"""Generate a beautiful {dtype['name']} diagram.

CONTENT:
{content_desc}

DIAGRAM TYPE: {dtype['name']}
- {dtype['description']}
- Visual elements: {dtype['prompt_hint']}

VISUAL STYLE: {theme_data['name']}
{theme_data['style']}

REQUIREMENTS:
- Make the diagram clear and easy to understand
- Include all elements from the description
- Use proper diagram conventions for this type
- Text labels should be readable
- Professional quality suitable for presentations
- NO title text at the top - just the diagram itself
"""

    # Generate filename
    if not filename:
        slug = description[:30].replace(' ', '_').replace('->', '_')
        slug = ''.join(c for c in slug if c.isalnum() or c == '_')
        timestamp = datetime.now().strftime("%H%M%S")
        filename = f"{diagram_type}_{theme}_{slug}_{timestamp}.png"

    output_path = output_dir / filename

    # Generate with Gemini
    client = get_gemini_client()

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_modalities=['IMAGE'],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio
                )
            )
        )

        for part in response.parts:
            if part.inline_data is not None:
                with open(output_path, "wb") as f:
                    f.write(part.inline_data.data)

                return {
                    "path": str(output_path),
                    "description": description,
                    "diagram_type": diagram_type,
                    "theme": theme,
                    "mermaid": mermaid_code,
                }

        raise Exception("No image in response")

    except Exception as e:
        if "429" in str(e):
            import time
            time.sleep(10)
            return generate_diagram(description, diagram_type, theme, mermaid_code, output_dir, filename, aspect_ratio)
        raise


def list_themes() -> dict:
    """Return available themes."""
    return {k: {"name": v["name"], "emoji": v["emoji"]} for k, v in THEMES.items()}


def list_diagram_types() -> dict:
    """Return available diagram types."""
    return {k: {"name": v["name"], "emoji": v["emoji"], "description": v["description"]}
            for k, v in DIAGRAM_TYPES.items()}


# ============================================================
# CLI
# ============================================================
def cli():
    """Command-line interface."""
    import argparse
    from dotenv import load_dotenv
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="DiagramForge - AI-Powered Diagram Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # From plain text description
  diagramforge "User login -> Authentication -> Dashboard or Error"

  # With specific type and theme
  diagramforge "Frontend, Backend, Database, Cache" --type architecture --theme blueprint

  # From Mermaid code
  diagramforge --mermaid "graph TD; A[Start]-->B{Decision}; B-->|Yes|C[Do it]; B-->|No|D[Skip]"

  # Mind map
  diagramforge "AI: Machine Learning, Deep Learning, NLP, Computer Vision" --type mindmap --theme watercolor

  # Wide format for presentations
  diagramforge "API request flow" --type sequence --aspect 16:9
        """
    )

    parser.add_argument("description", nargs="?", help="Diagram description (use -> for connections)")
    parser.add_argument("--mermaid", "-m", help="Mermaid syntax to interpret")
    parser.add_argument("--type", "-t", default="flowchart",
                        help=f"Diagram type: {', '.join(DIAGRAM_TYPES.keys())}")
    parser.add_argument("--theme", "-s", default="technical",
                        help=f"Visual theme: {', '.join(THEMES.keys())}")
    parser.add_argument("--output", "-o", help="Output directory")
    parser.add_argument("--aspect", "-a", default="1:1", choices=["1:1", "16:9", "9:16"],
                        help="Aspect ratio")
    parser.add_argument("--list-themes", action="store_true", help="List themes")
    parser.add_argument("--list-types", action="store_true", help="List diagram types")
    parser.add_argument("--open", action="store_true", help="Open output folder")

    args = parser.parse_args()

    # List themes
    if args.list_themes:
        print("\n🎨 VISUAL THEMES:\n")
        for key, info in list_themes().items():
            print(f"  {info['emoji']} {key:15} - {info['name']}")
        print()
        return

    # List types
    if args.list_types:
        print("\n📊 DIAGRAM TYPES:\n")
        for key, info in list_diagram_types().items():
            print(f"  {info['emoji']} {key:15} - {info['name']}")
            print(f"      {info['description']}")
        print()
        return

    # Need either description or mermaid
    if not args.description and not args.mermaid:
        parser.print_help()
        return

    # Set config
    if args.output:
        CONFIG.output_dir = Path(args.output)

    # Generate
    print(f"🎨 Generating {args.type} diagram ({args.theme} theme)...")

    try:
        result = generate_diagram(
            description=args.description or "Interpret the Mermaid code",
            diagram_type=args.type,
            theme=args.theme,
            mermaid_code=args.mermaid,
            aspect_ratio=args.aspect,
        )

        print(f"✅ {result['path']}")
        print(f"\n📂 Output: {CONFIG.output_dir}")

        if args.open:
            import subprocess
            subprocess.run(["open", str(CONFIG.output_dir)])

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    cli()
