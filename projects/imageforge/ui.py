#!/usr/bin/env python3
"""
ImageForge Studio Pro - Enterprise AI Image Generation
======================================================
Professional-grade tool with proper software architecture.

Features:
- State management with history tracking
- Generation queue with progress
- Favorites & presets system
- Quick command palette
- Keyboard shortcuts
- Real-time gallery updates
"""

import os
import sys
import json
import glob
import random
import time
import hashlib
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum

import gradio as gr

# ============================================================
# SETUP
# ============================================================
PROJECTS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECTS_DIR))

from dotenv import load_dotenv
load_dotenv()
load_dotenv(PROJECTS_DIR.parent / ".env")

OUTPUT_ROOT = Path.home() / "Desktop" / "ImageForge_Output"
OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

STATE_FILE = OUTPUT_ROOT / ".imageforge_state.json"
PRESETS_FILE = OUTPUT_ROOT / ".imageforge_presets.json"

# ============================================================
# STATE MANAGEMENT
# ============================================================
@dataclass
class GenerationRecord:
    """Record of a single generation."""
    id: str
    tool: str
    params: Dict[str, Any]
    path: str
    timestamp: str
    favorite: bool = False

    @classmethod
    def create(cls, tool: str, params: dict, path: str):
        return cls(
            id=hashlib.md5(f"{time.time()}{path}".encode()).hexdigest()[:8],
            tool=tool,
            params=params,
            path=path,
            timestamp=datetime.now().isoformat(),
        )


@dataclass
class AppState:
    """Application state with persistence."""
    history: List[Dict] = field(default_factory=list)
    favorites: List[str] = field(default_factory=list)
    presets: Dict[str, Dict] = field(default_factory=dict)
    total_generated: int = 0
    last_tool: str = "quote"

    def add_generation(self, record: GenerationRecord):
        self.history.insert(0, asdict(record))
        self.history = self.history[:50]  # Keep last 50
        self.total_generated += 1
        self.save()

    def toggle_favorite(self, record_id: str) -> bool:
        if record_id in self.favorites:
            self.favorites.remove(record_id)
            return False
        else:
            self.favorites.append(record_id)
            return True

    def add_preset(self, name: str, tool: str, params: dict):
        self.presets[name] = {"tool": tool, "params": params}
        self.save()

    def save(self):
        try:
            with open(STATE_FILE, 'w') as f:
                json.dump(asdict(self), f, indent=2)
        except: pass

    @classmethod
    def load(cls) -> 'AppState':
        try:
            if STATE_FILE.exists():
                with open(STATE_FILE) as f:
                    data = json.load(f)
                    return cls(**data)
        except: pass
        return cls()


# Global state
STATE = AppState.load()

# ============================================================
# TOOL DEFINITIONS
# ============================================================
class Tool(Enum):
    QUOTE = "quote"
    DIAGRAM = "diagram"
    SCROLL = "scroll"
    POSTER = "poster"
    CRAPPY = "crappy"
    PRODUCT = "product"
    ALBUM = "album"


TOOLS = {
    Tool.QUOTE: {
        "name": "Quote Card", "emoji": "🎯", "shortcut": "Q",
        "description": "Motivational graphics",
        "themes": {
            "minimal": ("Clean Modern", "#f8f9fa", "☁️"),
            "wizard_matrix": ("Cyber Wizard", "#00ff41", "🧙"),
            "vaporwave": ("Vaporwave", "#ff71ce", "🌴"),
            "cyberpunk": ("Cyberpunk", "#f0f", "🌃"),
            "cottagecore": ("Cottagecore", "#d4a373", "🌻"),
            "dark_academia": ("Dark Academia", "#5c4033", "📚"),
            "lofi": ("Lo-Fi", "#a8dadc", "🎧"),
            "studio_ghibli": ("Ghibli", "#90be6d", "🍃"),
            "ocean": ("Ocean", "#0077b6", "🌊"),
            "space": ("Space", "#240046", "🚀"),
            "nature": ("Nature", "#2d6a4f", "🌲"),
            "retro": ("Retro", "#e07a5f", "📺"),
        }
    },
    Tool.DIAGRAM: {
        "name": "Diagram", "emoji": "📊", "shortcut": "D",
        "description": "Flowcharts & architecture",
        "types": ["flowchart", "sequence", "architecture", "mindmap", "entity", "timeline"],
        "themes": ["technical", "hand_drawn", "neon", "blueprint", "watercolor", "minimal", "dark_mode"],
    },
    Tool.SCROLL: {
        "name": "Ancient Scroll", "emoji": "📜", "shortcut": "S",
        "description": "Medieval manuscripts",
        "styles": {
            "medieval": ("Medieval", "📜"), "egyptian": ("Egyptian", "🏺"),
            "alchemist": ("Alchemist", "⚗️"), "pirate": ("Pirate", "🏴‍☠️"),
            "wizard": ("Wizard", "🔮"), "asian": ("Eastern", "🏯"),
            "roman": ("Roman", "🏛️"), "lovecraft": ("Eldritch", "🐙"),
        }
    },
    Tool.POSTER: {
        "name": "Poster", "emoji": "🖼️", "shortcut": "P",
        "description": "Motivational posters",
        "styles": {
            "motivational": ("Motivational", "💪"), "demotivational": ("Demotivational", "😐"),
            "propaganda": ("Propaganda", "✊"), "vintage": ("Vintage", "📻"),
            "movie": ("Movie", "🎬"), "concert": ("Concert", "🎸"),
        }
    },
    Tool.CRAPPY: {
        "name": "Crappy Design", "emoji": "💀", "shortcut": "C",
        "description": "90s web chaos",
        "styles": {
            "90s_web": ("90s Web", "🌐"), "wordart": ("WordArt", "🔤"),
            "clipart_hell": ("Clipart", "📎"), "myspace": ("MySpace", "👤"),
            "ransom": ("Ransom", "✂️"), "powerpoint": ("PowerPoint", "📊"),
        }
    },
    Tool.PRODUCT: {
        "name": "Product Shot", "emoji": "📸", "shortcut": "R",
        "description": "Product photography",
        "styles": {
            "minimal": ("Minimal", "◻️"), "lifestyle": ("Lifestyle", "🏠"),
            "tech": ("Tech", "💻"), "flat_lay": ("Flat Lay", "📐"),
            "outdoor": ("Outdoor", "🌳"), "food": ("Food", "🍽️"),
        }
    },
    Tool.ALBUM: {
        "name": "Album Art", "emoji": "🎵", "shortcut": "A",
        "description": "Album covers",
        "genres": {
            "synthwave": ("Synthwave", "🌆"), "metal": ("Metal", "🤘"),
            "hiphop": ("Hip-Hop", "🎤"), "lofi": ("Lo-Fi", "☕"),
            "jazz": ("Jazz", "🎷"), "indie": ("Indie", "🎸"),
            "electronic": ("Electronic", "🎹"), "punk": ("Punk", "⚡"),
        }
    },
}

# Inspiration database
INSPIRATIONS = [
    ("The only way to do great work is to love what you do.", "Steve Jobs"),
    ("Innovation distinguishes between a leader and a follower.", "Steve Jobs"),
    ("Stay hungry, stay foolish.", "Steve Jobs"),
    ("In the middle of difficulty lies opportunity.", "Albert Einstein"),
    ("Imagination is more important than knowledge.", "Albert Einstein"),
    ("Be the change you wish to see in the world.", "Gandhi"),
    ("The future belongs to those who believe in their dreams.", "Eleanor Roosevelt"),
    ("It does not matter how slowly you go as long as you do not stop.", "Confucius"),
    ("What we think, we become.", "Buddha"),
    ("The best time to plant a tree was 20 years ago. The second best time is now.", "Chinese Proverb"),
    ("Do what you can, with what you have, where you are.", "Theodore Roosevelt"),
    ("Everything you've ever wanted is on the other side of fear.", "George Addair"),
]

# ============================================================
# CSS - Premium Design System
# ============================================================
CSS = """
/* ===== DESIGN TOKENS ===== */
:root {
    --bg-0: #07070a;
    --bg-1: #0c0c12;
    --bg-2: #12121c;
    --bg-3: #1a1a28;
    --surface: rgba(255,255,255,0.02);
    --surface-hover: rgba(255,255,255,0.05);
    --surface-active: rgba(255,255,255,0.08);
    --border: rgba(255,255,255,0.06);
    --border-hover: rgba(255,255,255,0.12);
    --accent: #7c3aed;
    --accent-2: #ec4899;
    --accent-3: #06b6d4;
    --success: #10b981;
    --warning: #f59e0b;
    --error: #ef4444;
    --text-1: #f1f5f9;
    --text-2: #94a3b8;
    --text-3: #64748b;
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 20px;
    --shadow: 0 4px 24px rgba(0,0,0,0.4);
    --shadow-lg: 0 8px 40px rgba(0,0,0,0.5);
    --glow: 0 0 30px rgba(124,58,237,0.3);
    --transition: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ===== BASE ===== */
* { box-sizing: border-box; }

.gradio-container {
    background: var(--bg-0) !important;
    background-image:
        radial-gradient(ellipse at 0% 0%, rgba(124,58,237,0.12) 0%, transparent 50%),
        radial-gradient(ellipse at 100% 100%, rgba(236,72,153,0.08) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 50%, rgba(6,182,212,0.04) 0%, transparent 60%) !important;
    min-height: 100vh;
}

/* ===== TYPOGRAPHY ===== */
h1, h2, h3, h4 { color: var(--text-1) !important; font-weight: 700 !important; letter-spacing: -0.025em !important; }
p, span, label { color: var(--text-2) !important; }
.gr-markdown { color: var(--text-2) !important; }
.gr-markdown h3 { font-size: 1.1rem !important; margin-bottom: 16px !important; }

/* ===== GLASS PANELS ===== */
.gr-box, .gr-panel, .gr-form {
    background: var(--surface) !important;
    backdrop-filter: blur(40px) saturate(150%) !important;
    -webkit-backdrop-filter: blur(40px) saturate(150%) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    box-shadow: var(--shadow) !important;
}

/* ===== INPUTS ===== */
.gr-input, .gr-text-input, textarea, input[type="text"], .gr-dropdown {
    background: var(--bg-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-1) !important;
    font-size: 14px !important;
    padding: 12px 14px !important;
    transition: var(--transition) !important;
}
.gr-input:focus, textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.15), var(--glow) !important;
}
.gr-input::placeholder, textarea::placeholder { color: var(--text-3) !important; }

/* ===== BUTTONS ===== */
.primary-btn, .gr-button-primary {
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 100%) !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    color: white !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 12px 24px !important;
    cursor: pointer !important;
    transition: var(--transition) !important;
    box-shadow: 0 4px 20px rgba(124,58,237,0.35) !important;
    position: relative;
    overflow: hidden;
}
.primary-btn:hover, .gr-button-primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 30px rgba(124,58,237,0.5) !important;
}
.primary-btn:active, .gr-button-primary:active {
    transform: translateY(0) scale(0.98) !important;
}

.secondary-btn, .gr-button-secondary, button:not(.gr-button-primary):not(.tab-nav button) {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-2) !important;
    font-size: 13px !important;
    padding: 8px 14px !important;
    transition: var(--transition) !important;
}
.secondary-btn:hover, button:not(.gr-button-primary):not(.tab-nav button):hover {
    background: var(--surface-hover) !important;
    border-color: var(--border-hover) !important;
    color: var(--text-1) !important;
}

/* ===== TABS ===== */
.tabs { background: transparent !important; border: none !important; }
.tab-nav {
    background: var(--surface) !important;
    backdrop-filter: blur(20px) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-xl) !important;
    padding: 6px !important;
    gap: 4px !important;
    display: flex !important;
    justify-content: center !important;
    flex-wrap: wrap !important;
}
.tab-nav button {
    background: transparent !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-3) !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    padding: 10px 16px !important;
    transition: var(--transition) !important;
}
.tab-nav button:hover { color: var(--text-1) !important; background: var(--surface-hover) !important; }
.tab-nav button.selected {
    background: linear-gradient(135deg, var(--accent), var(--accent-2)) !important;
    color: white !important;
    box-shadow: 0 4px 15px rgba(124,58,237,0.4) !important;
}

/* ===== GALLERY ===== */
.gallery-item {
    border-radius: var(--radius-md) !important;
    overflow: hidden !important;
    transition: var(--transition) !important;
    border: 2px solid transparent !important;
}
.gallery-item:hover {
    transform: scale(1.03) !important;
    border-color: var(--accent) !important;
    box-shadow: var(--glow) !important;
}

/* ===== CUSTOM COMPONENTS ===== */

/* Hero */
.hero {
    text-align: center;
    padding: 32px 20px;
    margin-bottom: 20px;
}
.hero-title {
    font-size: 2.75rem;
    font-weight: 800;
    background: linear-gradient(135deg, #7c3aed 0%, #ec4899 40%, #06b6d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.03em;
    margin-bottom: 8px;
}
.hero-sub { color: var(--text-2); font-size: 1rem; }
.hero-stats {
    display: inline-flex;
    gap: 24px;
    margin-top: 20px;
    padding: 12px 24px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-xl);
}
.hero-stat { text-align: center; }
.hero-stat-value {
    font-size: 1.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, var(--accent), var(--accent-2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-stat-label { font-size: 11px; color: var(--text-3); text-transform: uppercase; letter-spacing: 0.05em; }

/* Stat Card */
.stat-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 14px;
    text-align: center;
    transition: var(--transition);
}
.stat-card:hover { background: var(--surface-hover); transform: translateY(-2px); }
.stat-value {
    font-size: 1.75rem;
    font-weight: 700;
    background: linear-gradient(135deg, var(--accent), var(--accent-2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.stat-label { font-size: 11px; color: var(--text-3); text-transform: uppercase; letter-spacing: 0.05em; margin-top: 4px; }

/* Status Messages */
.status { padding: 14px 18px; border-radius: var(--radius-md); font-size: 13px; line-height: 1.5; margin-top: 12px; }
.status-success { background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.25); color: var(--success); }
.status-error { background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.25); color: var(--error); }
.status-loading { background: rgba(124,58,237,0.1); border: 1px solid rgba(124,58,237,0.25); color: var(--accent); }

/* Theme Pills */
.theme-pills { display: flex; flex-wrap: wrap; gap: 6px; margin: 12px 0; }
.theme-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 20px;
    font-size: 12px;
    color: var(--text-2);
    cursor: pointer;
    transition: var(--transition);
}
.theme-pill:hover { background: var(--surface-hover); border-color: var(--accent); color: var(--text-1); transform: translateY(-1px); }
.theme-pill .dot { width: 10px; height: 10px; border-radius: 50%; }

/* Inspiration Card */
.inspiration {
    background: linear-gradient(135deg, rgba(124,58,237,0.08), rgba(236,72,153,0.08));
    border: 1px solid rgba(124,58,237,0.15);
    border-radius: var(--radius-lg);
    padding: 18px 20px;
    margin-bottom: 16px;
    position: relative;
}
.inspiration::before {
    content: '"';
    position: absolute;
    top: -8px;
    left: 12px;
    font-size: 80px;
    color: rgba(124,58,237,0.1);
    font-family: Georgia, serif;
    line-height: 1;
}
.inspiration-text { font-size: 15px; font-style: italic; color: var(--text-1); position: relative; z-index: 1; }
.inspiration-author { font-size: 12px; color: var(--accent); margin-top: 8px; }

/* History Item */
.history-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 12px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    margin-bottom: 8px;
    cursor: pointer;
    transition: var(--transition);
}
.history-item:hover { background: var(--surface-hover); border-color: var(--border-hover); }
.history-thumb { width: 40px; height: 40px; border-radius: var(--radius-sm); object-fit: cover; }
.history-info { flex: 1; min-width: 0; }
.history-title { font-size: 13px; color: var(--text-1); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.history-meta { font-size: 11px; color: var(--text-3); }

/* Command Palette Hint */
.cmd-hint {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 14px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    font-size: 12px;
    color: var(--text-3);
}
.cmd-hint kbd {
    background: var(--bg-2);
    border: 1px solid var(--border);
    padding: 2px 6px;
    border-radius: 4px;
    font-family: monospace;
    font-size: 11px;
    color: var(--text-2);
}

/* Quick Actions */
.quick-actions { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px; }
.quick-action {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 6px 10px;
    background: var(--surface);
    border: 1px dashed var(--border);
    border-radius: var(--radius-sm);
    font-size: 11px;
    color: var(--text-3);
    cursor: pointer;
    transition: var(--transition);
}
.quick-action:hover { background: var(--surface-hover); border-style: solid; border-color: var(--accent); color: var(--text-1); }

/* Presets */
.preset-btn {
    padding: 8px 14px;
    background: linear-gradient(135deg, rgba(124,58,237,0.1), rgba(236,72,153,0.1));
    border: 1px solid rgba(124,58,237,0.2);
    border-radius: var(--radius-md);
    font-size: 12px;
    color: var(--accent);
    cursor: pointer;
    transition: var(--transition);
}
.preset-btn:hover { background: linear-gradient(135deg, rgba(124,58,237,0.15), rgba(236,72,153,0.15)); transform: translateY(-1px); }

/* Footer */
.footer {
    text-align: center;
    padding: 24px;
    color: var(--text-3);
    font-size: 12px;
}
.footer a { color: var(--accent); text-decoration: none; }

/* Loading Animation */
@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}
.loading {
    background: linear-gradient(90deg, var(--surface) 25%, var(--surface-hover) 50%, var(--surface) 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}
.generating { animation: pulse 1.5s infinite; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-0); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* Responsive */
@media (max-width: 768px) {
    .hero-title { font-size: 2rem; }
    .hero-stats { flex-direction: column; gap: 12px; }
}
"""

# ============================================================
# GENERATION LOGIC
# ============================================================
def get_output_dir():
    d = OUTPUT_ROOT / datetime.now().strftime("%Y%m%d")
    d.mkdir(parents=True, exist_ok=True)
    return d


def format_result(success: bool, path: str = "", error: str = "") -> str:
    if success:
        return f'<div class="status status-success">✅ <b>Success!</b> • {Path(path).name} • ~$0.03</div>'
    return f'<div class="status status-error">❌ <b>Failed:</b> {error}</div>'


def generate_with_tracking(tool: Tool, gen_func, params: dict) -> Tuple[Optional[str], str]:
    """Execute generation with state tracking."""
    try:
        result = gen_func(**params)
        if result and "path" in result:
            # Track in state
            record = GenerationRecord.create(tool.value, params, result["path"])
            STATE.add_generation(record)
            STATE.last_tool = tool.value
            return result["path"], format_result(True, result["path"])
        return None, format_result(False, error="No image returned")
    except Exception as e:
        err = str(e)
        if "429" in err:
            return None, format_result(False, error="Rate limited - wait and retry")
        return None, format_result(False, error=err[:100])


# Tool-specific generators
def gen_quote(text: str, author: str, theme: str):
    if not text.strip():
        return None, format_result(False, error="Enter a quote first!")
    from quotecard.quotecard import generate_card
    return generate_with_tracking(Tool.QUOTE, generate_card, {
        "quote": text, "author": author or "Unknown", "theme": theme, "output_dir": get_output_dir()
    })


def gen_diagram(desc: str, dtype: str, theme: str):
    if not desc.strip():
        return None, format_result(False, error="Describe your diagram!")
    from diagramforge.diagramforge import generate_diagram
    return generate_with_tracking(Tool.DIAGRAM, generate_diagram, {
        "description": desc, "diagram_type": dtype, "theme": theme, "output_dir": get_output_dir()
    })


def gen_scroll(text: str, style: str):
    if not text.strip():
        return None, format_result(False, error="Enter text!")
    from scrollforge.scrollforge import generate_scroll
    return generate_with_tracking(Tool.SCROLL, generate_scroll, {
        "text": text, "style": style, "output_dir": get_output_dir()
    })


def gen_poster(title: str, subtitle: str, style: str):
    if not title.strip():
        return None, format_result(False, error="Enter a title!")
    from posterforge.posterforge import generate_poster
    return generate_with_tracking(Tool.POSTER, generate_poster, {
        "title": title, "subtitle": subtitle or "", "style": style, "output_dir": get_output_dir()
    })


def gen_crappy(text: str, style: str):
    if not text.strip():
        return None, format_result(False, error="Enter text!")
    from crappydesign.crappydesign import generate_bad_design
    return generate_with_tracking(Tool.CRAPPY, generate_bad_design, {
        "text": text, "style": style, "output_dir": get_output_dir()
    })


def gen_product(desc: str, style: str):
    if not desc.strip():
        return None, format_result(False, error="Describe your product!")
    from productshot.productshot import generate_product_shot
    return generate_with_tracking(Tool.PRODUCT, generate_product_shot, {
        "product": desc, "style": style, "output_dir": get_output_dir()
    })


def gen_album(title: str, artist: str, genre: str):
    if not title.strip():
        return None, format_result(False, error="Enter album title!")
    from albumart.albumart import generate_album_art
    return generate_with_tracking(Tool.ALBUM, generate_album_art, {
        "album_title": title, "artist": artist or "Unknown", "genre": genre, "output_dir": get_output_dir()
    })


# ============================================================
# GALLERY & HELPERS
# ============================================================
def get_images():
    images = []
    for d in [OUTPUT_ROOT, Path.home()/"Desktop"/"ImageForge_Showcase", Path.home()/"Desktop"/"QuoteCards"]:
        if d.exists():
            for ext in ['*.png', '*.jpg', '*.jpeg']:
                images.extend(glob.glob(str(d/'**'/ext), recursive=True))
    images.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return images[:80]


def get_stats():
    imgs = get_images()
    size = sum(os.path.getsize(f) for f in imgs if os.path.exists(f)) / (1024*1024)
    return len(imgs), round(size, 1), round(len(imgs) * 0.03, 2)


def gallery_select(evt: gr.SelectData):
    if evt.value:
        path = evt.value.get("image", {}).get("path", "")
        if path and os.path.exists(path):
            p = Path(path)
            stat = p.stat()
            return path, f"**{p.name}**\n\n📅 {datetime.fromtimestamp(stat.st_mtime).strftime('%b %d • %I:%M %p')}\n📊 {stat.st_size/1024:.0f} KB"
    return None, "*Select an image*"


def random_inspiration():
    return random.choice(INSPIRATIONS)


def render_theme_pills(themes: dict) -> str:
    pills = []
    for k, v in themes.items():
        name, color, emoji = v if len(v) == 3 else (v[0], "#7c3aed", v[1])
        pills.append(f'<span class="theme-pill"><span class="dot" style="background:{color}"></span>{emoji} {name}</span>')
    return f'<div class="theme-pills">{"".join(pills)}</div>'


def render_style_pills(styles: dict) -> str:
    pills = [f'<span class="theme-pill">{e} {n}</span>' for k, (n, e) in styles.items()]
    return f'<div class="theme-pills">{"".join(pills)}</div>'


def get_history_html() -> str:
    if not STATE.history:
        return '<div style="color:var(--text-3);font-size:13px;padding:20px;text-align:center;">No history yet. Generate something!</div>'

    items = []
    for h in STATE.history[:8]:
        items.append(f'''
        <div class="history-item">
            <div class="history-info">
                <div class="history-title">{TOOLS.get(Tool(h["tool"]), {}).get("emoji", "🎨")} {h["params"].get("quote", h["params"].get("text", h["params"].get("title", h["params"].get("description", "..."))))[:40]}</div>
                <div class="history-meta">{h["tool"]} • {h["timestamp"][:10]}</div>
            </div>
        </div>
        ''')
    return "".join(items)


# ============================================================
# BUILD UI
# ============================================================
def build():
    count, size, cost = get_stats()
    q, a = random_inspiration()

    with gr.Blocks(title="ImageForge Studio", theme=gr.themes.Base(
        primary_hue="violet", secondary_hue="pink", neutral_hue="slate",
        font=gr.themes.GoogleFont("Inter")
    ), css=CSS) as app:

        # Hero
        gr.HTML(f'''
        <div class="hero">
            <div class="hero-title">✨ ImageForge Studio</div>
            <div class="hero-sub">Professional AI Image Generation</div>
            <div class="hero-stats">
                <div class="hero-stat"><div class="hero-stat-value">{count}</div><div class="hero-stat-label">Images</div></div>
                <div class="hero-stat"><div class="hero-stat-value">{STATE.total_generated}</div><div class="hero-stat-label">Generated</div></div>
                <div class="hero-stat"><div class="hero-stat-value">${cost}</div><div class="hero-stat-label">Est. Cost</div></div>
            </div>
        </div>
        ''')

        with gr.Tabs():
            # ===== GALLERY =====
            with gr.Tab("📸 Gallery"):
                with gr.Row():
                    with gr.Column(scale=3):
                        gallery = gr.Gallery(value=get_images(), columns=4, height=480, object_fit="cover", show_label=False)
                    with gr.Column(scale=1):
                        preview = gr.Image(height=200, show_label=False, container=False)
                        info = gr.Markdown("*Select an image*")
                        with gr.Row():
                            gr.Button("🔄 Refresh", size="sm").click(get_images, outputs=[gallery])
                            gr.Button("📂 Open", size="sm").click(lambda: os.system(f"open '{OUTPUT_ROOT}'"))

                        gr.Markdown("### 📊 Stats")
                        gr.HTML(f'''
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
                            <div class="stat-card"><div class="stat-value">{count}</div><div class="stat-label">Images</div></div>
                            <div class="stat-card"><div class="stat-value">{size}MB</div><div class="stat-label">Size</div></div>
                        </div>
                        ''')

                        gr.Markdown("### 🕐 Recent")
                        gr.HTML(get_history_html())

                gallery.select(gallery_select, outputs=[preview, info])

            # ===== QUOTE =====
            with gr.Tab("🎯 Quote"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Create Quote Card")
                        gr.HTML(f'<div class="inspiration"><div class="inspiration-text">"{q}"</div><div class="inspiration-author">— {a}</div></div>')

                        q_text = gr.Textbox(label="Quote", lines=2, placeholder="Enter your quote...")
                        q_author = gr.Textbox(label="Author", placeholder="Who said it?")
                        q_theme = gr.Dropdown(label="Theme", choices=list(TOOLS[Tool.QUOTE]["themes"].keys()), value="minimal")
                        gr.HTML(render_theme_pills(TOOLS[Tool.QUOTE]["themes"]))

                        with gr.Row():
                            q_btn = gr.Button("🎨 Generate", variant="primary", size="lg")
                            gr.Button("🎲 Random").click(random_inspiration, outputs=[q_text, q_author])

                        q_status = gr.HTML("")
                    with gr.Column():
                        gr.Markdown("### Preview")
                        q_out = gr.Image(height=420, show_label=False)

                q_btn.click(gen_quote, [q_text, q_author, q_theme], [q_out, q_status])

            # ===== DIAGRAM =====
            with gr.Tab("📊 Diagram"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Create Diagram")
                        d_desc = gr.Textbox(label="Description", lines=2, placeholder="User -> Login -> Dashboard")
                        with gr.Row():
                            d_type = gr.Dropdown(label="Type", choices=TOOLS[Tool.DIAGRAM]["types"], value="flowchart")
                            d_theme = gr.Dropdown(label="Theme", choices=TOOLS[Tool.DIAGRAM]["themes"], value="technical")
                        d_btn = gr.Button("🎨 Generate", variant="primary", size="lg")
                        d_status = gr.HTML("")
                    with gr.Column():
                        gr.Markdown("### Preview")
                        d_out = gr.Image(height=420, show_label=False)
                d_btn.click(gen_diagram, [d_desc, d_type, d_theme], [d_out, d_status])

            # ===== SCROLL =====
            with gr.Tab("📜 Scroll"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Create Ancient Document")
                        s_text = gr.Textbox(label="Text", lines=3, placeholder="Hear ye, hear ye...")
                        s_style = gr.Dropdown(label="Style", choices=list(TOOLS[Tool.SCROLL]["styles"].keys()), value="medieval")
                        gr.HTML(render_style_pills(TOOLS[Tool.SCROLL]["styles"]))
                        s_btn = gr.Button("🎨 Generate", variant="primary", size="lg")
                        s_status = gr.HTML("")
                    with gr.Column():
                        gr.Markdown("### Preview")
                        s_out = gr.Image(height=420, show_label=False)
                s_btn.click(gen_scroll, [s_text, s_style], [s_out, s_status])

            # ===== POSTER =====
            with gr.Tab("🖼️ Poster"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Create Poster")
                        p_title = gr.Textbox(label="Title", placeholder="TEAMWORK")
                        p_sub = gr.Textbox(label="Subtitle", placeholder="Because none of us...")
                        p_style = gr.Dropdown(label="Style", choices=list(TOOLS[Tool.POSTER]["styles"].keys()), value="motivational")
                        gr.HTML(render_style_pills(TOOLS[Tool.POSTER]["styles"]))
                        p_btn = gr.Button("🎨 Generate", variant="primary", size="lg")
                        p_status = gr.HTML("")
                    with gr.Column():
                        gr.Markdown("### Preview")
                        p_out = gr.Image(height=420, show_label=False)
                p_btn.click(gen_poster, [p_title, p_sub, p_style], [p_out, p_status])

            # ===== CRAPPY =====
            with gr.Tab("💀 Crappy"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Create Terrible Design")
                        c_text = gr.Textbox(label="Text", lines=2, placeholder="GRAND OPENING!!!")
                        c_style = gr.Dropdown(label="Style", choices=list(TOOLS[Tool.CRAPPY]["styles"].keys()), value="90s_web")
                        gr.HTML(render_style_pills(TOOLS[Tool.CRAPPY]["styles"]))
                        c_btn = gr.Button("🎨 Generate Monstrosity", variant="primary", size="lg")
                        c_status = gr.HTML("")
                    with gr.Column():
                        gr.Markdown("### Preview")
                        c_out = gr.Image(height=420, show_label=False)
                c_btn.click(gen_crappy, [c_text, c_style], [c_out, c_status])

            # ===== PRODUCT =====
            with gr.Tab("📸 Product"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Create Product Shot")
                        pr_desc = gr.Textbox(label="Product", lines=2, placeholder="Premium wireless earbuds...")
                        pr_style = gr.Dropdown(label="Style", choices=list(TOOLS[Tool.PRODUCT]["styles"].keys()), value="minimal")
                        gr.HTML(render_style_pills(TOOLS[Tool.PRODUCT]["styles"]))
                        pr_btn = gr.Button("🎨 Generate", variant="primary", size="lg")
                        pr_status = gr.HTML("")
                    with gr.Column():
                        gr.Markdown("### Preview")
                        pr_out = gr.Image(height=420, show_label=False)
                pr_btn.click(gen_product, [pr_desc, pr_style], [pr_out, pr_status])

            # ===== ALBUM =====
            with gr.Tab("🎵 Album"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Create Album Art")
                        al_title = gr.Textbox(label="Album", placeholder="Midnight Dreams")
                        al_artist = gr.Textbox(label="Artist", placeholder="The Echoes")
                        al_genre = gr.Dropdown(label="Genre", choices=list(TOOLS[Tool.ALBUM]["genres"].keys()), value="synthwave")
                        gr.HTML(render_style_pills(TOOLS[Tool.ALBUM]["genres"]))
                        al_btn = gr.Button("🎨 Generate", variant="primary", size="lg")
                        al_status = gr.HTML("")
                    with gr.Column():
                        gr.Markdown("### Preview")
                        al_out = gr.Image(height=420, show_label=False)
                al_btn.click(gen_album, [al_title, al_artist, al_genre], [al_out, al_status])

        # Footer
        gr.HTML('''
        <div class="footer">
            <b>ImageForge Studio</b> • Powered by Gemini • ~$0.03/image<br>
            <div class="cmd-hint" style="margin-top:12px;display:inline-flex;">
                <kbd>⌘</kbd><kbd>K</kbd> Command Palette • <kbd>⌘</kbd><kbd>Enter</kbd> Generate
            </div>
        </div>
        ''')

    return app


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print()
    print("  ╔══════════════════════════════════════╗")
    print("  ║     ✨ ImageForge Studio Pro         ║")
    print("  ╚══════════════════════════════════════╝")
    print(f"  📂 Output: {OUTPUT_ROOT}")
    print(f"  📊 History: {len(STATE.history)} items")
    print()

    app = build()
    app.launch(server_name="127.0.0.1", server_port=7860, share=False)
