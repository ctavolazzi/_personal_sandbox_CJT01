# ImageForge Toolkit 🎨

**A collection of AI-powered image generation tools**

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| 🎯 **QuoteCard** | Motivational quote graphics | `python quotecard/quotecard.py` |
| 📊 **DiagramForge** | Technical diagrams & flowcharts | `python diagramforge/diagramforge.py` |
| 📜 **ScrollForge** | Ancient documents & manuscripts | `python scrollforge/scrollforge.py` |
| 🖼️ **PosterForge** | Motivational/demotivational posters | `python posterforge/posterforge.py` |
| 💀 **CrappyDesign** | Intentionally bad 90s design | `python crappydesign/crappydesign.py` |
| 📸 **ProductShot** | Product photography mockups | `python productshot/productshot.py` |
| 🎵 **AlbumArt** | Music album covers | `python albumart/albumart.py` |

## Quick Start

```bash
# Setup (from projects folder)
export GEMINI_API_KEY=your_key_here
# Or add to .env file

# Generate a quote card
python quotecard/quotecard.py "Your quote" --author "Author" --theme lofi

# Generate a diagram
python diagramforge/diagramforge.py "A -> B -> C" --type flowchart --theme neon

# Generate an ancient scroll
python scrollforge/scrollforge.py "Hear ye, hear ye..." --style medieval

# Generate a demotivational poster
python posterforge/posterforge.py "MEETINGS" "Because none of us is as dumb as all of us" --style demotivational

# Generate gloriously bad design
python crappydesign/crappydesign.py "GRAND OPENING SALE!!!" --style 90s_web

# Generate product shot
python productshot/productshot.py "Wireless earbuds, white case" --style minimal

# Generate album cover
python albumart/albumart.py "Midnight Dreams" --artist "The Echoes" --genre synthwave
```

## List Options

Each tool has a `--list-*` option to see available styles:

```bash
python quotecard/quotecard.py --list-themes
python diagramforge/diagramforge.py --list-types
python diagramforge/diagramforge.py --list-themes
python scrollforge/scrollforge.py --list-styles
python posterforge/posterforge.py --list-styles
python crappydesign/crappydesign.py --list-styles
python productshot/productshot.py --list-styles
python albumart/albumart.py --list-genres
```

## Output Locations

All tools save to `~/Desktop/[ToolName]/` by default:
- `~/Desktop/QuoteCards/`
- `~/Desktop/DiagramForge/`
- `~/Desktop/ScrollForge/`
- `~/Desktop/PosterForge/`
- `~/Desktop/CrappyDesign/`
- `~/Desktop/ProductShot/`
- `~/Desktop/AlbumArt/`

## MCP Integration

All tools can be exposed as MCP servers for use with AI assistants.
See `.cursor/mcp.json` for configuration.

## Cost

~$0.03 per image (Gemini image generation)
