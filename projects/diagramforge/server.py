#!/usr/bin/env python3
"""
DiagramForge MCP Server
=======================
Exposes DiagramForge to AI assistants via Model Context Protocol.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from diagramforge import (
    generate_diagram, list_themes, list_diagram_types,
    THEMES, DIAGRAM_TYPES
)


def handle_request(request: dict) -> dict:
    """Handle an MCP request."""
    method = request.get("method", "")
    params = request.get("params", {})
    req_id = request.get("id")

    try:
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "diagramforge",
                        "version": "1.0.0"
                    }
                }
            }

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": [
                        {
                            "name": "generate_diagram",
                            "description": "Generate a beautiful diagram from text description or Mermaid code",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "description": {
                                        "type": "string",
                                        "description": "Plain text description of the diagram (use -> for connections)"
                                    },
                                    "diagram_type": {
                                        "type": "string",
                                        "description": f"Type of diagram: {', '.join(DIAGRAM_TYPES.keys())}",
                                        "default": "flowchart"
                                    },
                                    "theme": {
                                        "type": "string",
                                        "description": f"Visual theme: {', '.join(THEMES.keys())}",
                                        "default": "technical"
                                    },
                                    "mermaid_code": {
                                        "type": "string",
                                        "description": "Optional Mermaid syntax to interpret"
                                    },
                                    "aspect_ratio": {
                                        "type": "string",
                                        "description": "1:1 (square), 16:9 (wide), or 9:16 (tall)",
                                        "default": "1:1"
                                    }
                                },
                                "required": ["description"]
                            }
                        },
                        {
                            "name": "list_diagram_themes",
                            "description": "List available visual themes for diagrams",
                            "inputSchema": {"type": "object", "properties": {}}
                        },
                        {
                            "name": "list_diagram_types",
                            "description": "List available diagram types (flowchart, sequence, etc.)",
                            "inputSchema": {"type": "object", "properties": {}}
                        }
                    ]
                }
            }

        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})

            if tool_name == "generate_diagram":
                result = generate_diagram(
                    description=tool_args.get("description", ""),
                    diagram_type=tool_args.get("diagram_type", "flowchart"),
                    theme=tool_args.get("theme", "technical"),
                    mermaid_code=tool_args.get("mermaid_code"),
                    aspect_ratio=tool_args.get("aspect_ratio", "1:1"),
                )
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": f"✅ Diagram generated!\n\nPath: {result['path']}\nType: {result['diagram_type']}\nTheme: {result['theme']}"
                        }]
                    }
                }

            elif tool_name == "list_diagram_themes":
                themes = list_themes()
                theme_list = "\n".join([
                    f"  {info['emoji']} {key}: {info['name']}"
                    for key, info in themes.items()
                ])
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": f"🎨 Visual Themes:\n\n{theme_list}"
                        }]
                    }
                }

            elif tool_name == "list_diagram_types":
                types_data = list_diagram_types()
                type_list = "\n".join([
                    f"  {info['emoji']} {key}: {info['name']} - {info['description']}"
                    for key, info in types_data.items()
                ])
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": f"📊 Diagram Types:\n\n{type_list}"
                        }]
                    }
                }

            else:
                raise ValueError(f"Unknown tool: {tool_name}")

        elif method == "notifications/initialized":
            return None

        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Unknown method: {method}"}
            }

    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32000, "message": str(e)}
        }


def main():
    """Run MCP server."""
    from dotenv import load_dotenv
    load_dotenv()
    load_dotenv(Path(__file__).parent.parent.parent / ".env")

    print("DiagramForge MCP Server started", file=sys.stderr)

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            request = json.loads(line.strip())
            response = handle_request(request)
            if response:
                print(json.dumps(response), flush=True)
        except json.JSONDecodeError:
            continue
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
