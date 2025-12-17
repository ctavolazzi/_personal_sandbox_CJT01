# DiagramForge 📊

**AI-Powered Diagram Generator**

Generate beautiful, themed diagrams from plain text or Mermaid syntax.

## Features

- 📊 **7 Diagram Types**: Flowchart, Sequence, Architecture, Mind Map, ER, Timeline, Org Chart
- 🎨 **10 Visual Themes**: Technical, Hand-drawn, Neon, Blueprint, Watercolor, and more
- 📝 **Multiple Inputs**: Plain text descriptions OR Mermaid syntax
- 🖥️ **CLI Tool**: Quick generation from terminal
- 🔌 **MCP Server**: Use from AI assistants

## Installation

```bash
cd projects/diagramforge
pip install -r requirements.txt
```

## Setup

Add your Gemini API key to `.env`:
```
GEMINI_API_KEY=your_key_here
```

## Usage

### CLI - Plain Text

```bash
# Simple flowchart
python diagramforge.py "User logs in -> Auth check -> Success or Failure"

# Architecture diagram
python diagramforge.py "Frontend, API Gateway, Microservices, Database, Cache" \
    --type architecture --theme blueprint

# Mind map
python diagramforge.py "AI: Machine Learning, Deep Learning, NLP, Vision" \
    --type mindmap --theme watercolor

# Sequence diagram (wide format)
python diagramforge.py "User sends request, Server validates, DB queries, Response" \
    --type sequence --theme neon --aspect 16:9
```

### CLI - Mermaid Syntax

```bash
# Interpret Mermaid code
python diagramforge.py --mermaid "graph TD; A[Start]-->B{Decision}; B-->|Yes|C[Do]; B-->|No|D[Skip]"

# Complex flowchart from Mermaid
python diagramforge.py --mermaid "
graph LR
    A[User] --> B[Frontend]
    B --> C[API]
    C --> D[(Database)]
    C --> E[Cache]
" --theme dark_mode
```

### List Options

```bash
python diagramforge.py --list-types    # See all diagram types
python diagramforge.py --list-themes   # See all visual themes
```

### MCP Server

Add to `.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "diagramforge": {
      "command": "python3",
      "args": ["/path/to/diagramforge/server.py"]
    }
  }
}
```

Then use in Cursor:
- "Generate a flowchart showing user authentication flow with neon theme"
- "Create an architecture diagram for a microservices system"
- "Make a mind map about machine learning concepts in watercolor style"

## Diagram Types

| Type | Use For |
|------|---------|
| 🔀 flowchart | Process flows, decisions, workflows |
| ↔️ sequence | API calls, message passing, interactions |
| 🏗️ architecture | System design, infrastructure |
| 🧠 mindmap | Brainstorming, concept mapping |
| 🔗 entity | Database schemas, relationships |
| 📅 timeline | Events, milestones, history |
| 👥 org | Org charts, hierarchies |

## Visual Themes

| Theme | Style |
|-------|-------|
| ⚙️ technical | Clean professional documentation |
| ✏️ hand_drawn | Sketchy whiteboard aesthetic |
| 💫 neon | Cyberpunk glowing lines |
| 📐 blueprint | Architectural drawing |
| 🎨 watercolor | Soft painted illustration |
| ⬜ minimal | Clean Apple-style |
| 💾 retro | 80s computer terminal |
| 📦 isometric | 3D infographic |
| 🌙 dark_mode | Modern dark UI |
| 🎪 playful | Fun cartoon style |

## Output

Diagrams save to `~/Desktop/DiagramForge/`

## Cost

~$0.03 per diagram (Gemini image generation)

## Tips

- Use `->` to indicate connections in text descriptions
- Use commas to list components
- Add context: "showing data flow" or "with error handling"
- Try different themes for the same diagram!

## License

MIT
