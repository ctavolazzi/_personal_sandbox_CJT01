# QuoteCard 🎨

**AI-Powered Quote Graphics Generator**

Generate beautiful, themed quote cards for social media with a single command.

## Features

- 🎨 **12 Visual Themes**: Wizard Matrix, Vaporwave, Cyberpunk, Lo-Fi, Studio Ghibli, and more
- 🤖 **Hybrid AI Approach**: Gemini generates backgrounds, Pillow renders text (reliable!)
- 🖥️ **CLI Tool**: Quick generation from terminal
- 🔌 **MCP Server**: Use from AI assistants like Cursor
- 📦 **Python Module**: Import and use in your code

## Installation

```bash
cd projects/quotecard
pip install -r requirements.txt
```

## Setup

Add your Gemini API key to `.env`:
```
GEMINI_API_KEY=your_key_here
```

## Usage

### CLI

```bash
# Generate a single card
python quotecard.py "Be the change you wish to see" --author "Gandhi" --theme minimal

# Random quote with random theme
python quotecard.py --random

# Batch generate
python quotecard.py --batch 5 --theme lofi --quotes quotes.json

# List themes
python quotecard.py --list-themes

# Open output folder
python quotecard.py --random --open
```

### Python Module

```python
from quotecard import generate_card, list_themes

# Generate a card
result = generate_card(
    quote="Done is better than perfect",
    author="Sheryl Sandberg",
    theme="vaporwave",
    brand="@YourBrand"
)
print(result["path"])

# List available themes
themes = list_themes()
```

### MCP Server

Add to `.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "quotecard": {
      "command": "python",
      "args": ["/path/to/quotecard/server.py"]
    }
  }
}
```

Then use in Cursor:
- "Generate a quote card with 'Dream big' by Norman Vaughan, use the cyberpunk theme"
- "Make a random motivational quote graphic"
- "List available quote card themes"

## Themes

| Theme | Style |
|-------|-------|
| 🧙 wizard_matrix | 16-bit pixel art, Matrix code, cyber-fantasy |
| 🌴 vaporwave | Pink/cyan gradients, 80s aesthetic |
| 🌃 cyberpunk | Neon noir, Blade Runner vibes |
| 🍄 cottagecore | Soft watercolors, pastoral |
| 📚 dark_academia | Gothic library, scholarly |
| 🎧 lofi | Cozy study, anime-inspired |
| ✨ studio_ghibli | Magical, hand-painted |
| 🌊 ocean | Calm seas, sunsets |
| 🚀 space | Cosmic, nebulae |
| 🌿 nature | Lush landscapes |
| 📺 retro | Pop art, bold colors |
| ⬜ minimal | Clean gradients |

## Output

Cards save to `~/Desktop/QuoteCards/` with:
- Image file (theme_quote_timestamp.jpg)
- Caption file (.txt) ready to copy-paste

## Cost

~$0.03 per card (Gemini image generation)

## License

MIT
