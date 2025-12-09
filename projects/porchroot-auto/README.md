# Porchroot Auto 🏭

Social media content factory that generates branded quote images with AI-powered captions.

## Features

- ✅ **Reliable text rendering** - Uses Pillow (no AI text-in-image spelling errors)
- ✅ **AI-powered captions** - Gemini generates engaging captions with hashtags
- ✅ **Quote history tracking** - Never repeats the same quote
- ✅ **Batch generation** - Generate multiple posts at once
- ✅ **Variety** - Random backgrounds keep your feed fresh

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment (copy .env.example to .env)
cp .env.example .env
# Edit .env with your GEMINI_API_KEY

# 3. Generate a post
python factory.py

# 4. Generate multiple posts
python factory.py --batch 5

# 5. Reset quote history (to reuse quotes)
python factory.py --reset
```

## Output

Each run generates:
- `output/post_XXX.jpg` - The quote image (1080x1080)
- `output/post_XXX_caption.txt` - Ready-to-paste caption with hashtags

## Customization

### Fonts
Drop `.ttf` or `.otf` files into `assets/fonts/`. The script picks the first one found.

Recommended: [Inter](https://fonts.google.com/specimen/Inter), [Montserrat](https://fonts.google.com/specimen/Montserrat), or [Poppins](https://fonts.google.com/specimen/Poppins)

### Backgrounds
Drop dark texture images into `assets/backgrounds/`. The script randomly selects one for variety.

Recommended: 1080x1080 or larger, dark/moody textures

### Quotes
Edit `quotes_db.json` to add your own quotes:

```json
[
  {"id": 1, "text": "Your quote here", "author": "Author Name"},
  {"id": 2, "text": "Another quote", "author": "Another Author"}
]
```

### Branding
Set in `.env`:
- `BRAND_HANDLE` - Your social handle (appears on images)
- `BRAND_WEBSITE` - Your website (for captions)

## Architecture

```
porchroot-auto/
├── factory.py          # Main script
├── quotes_db.json      # Quote database
├── used_quotes.txt     # History (auto-generated)
├── assets/
│   ├── fonts/          # Your .ttf files
│   └── backgrounds/    # Your texture images
└── output/             # Generated posts
```

Reuses `GeminiClient` from `../api-testing-framework` for caption generation.

## API Usage

This uses the Gemini API for caption generation only (not image generation).

- **Free tier**: ~60 requests/minute
- **Cost**: Essentially free for this use case
- **Get API key**: https://aistudio.google.com/apikey
