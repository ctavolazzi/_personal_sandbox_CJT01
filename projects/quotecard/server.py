#!/usr/bin/env python3
"""
QuoteCard MCP Server
====================
Exposes QuoteCard functionality to AI assistants via Model Context Protocol.

Run: python server.py
Or configure in .cursor/mcp.json
"""

import json
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from quotecard import generate_card, generate_random_card, list_themes, CONFIG, THEMES


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
                        "name": "quotecard",
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
                            "name": "generate_quote_card",
                            "description": "Generate a beautiful quote card image with AI background and text overlay",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "quote": {
                                        "type": "string",
                                        "description": "The quote text to display"
                                    },
                                    "author": {
                                        "type": "string",
                                        "description": "Attribution for the quote"
                                    },
                                    "theme": {
                                        "type": "string",
                                        "description": f"Visual theme. Options: {', '.join(THEMES.keys())}",
                                        "default": "minimal"
                                    },
                                    "brand": {
                                        "type": "string",
                                        "description": "Brand handle to display (e.g. @YourBrand)"
                                    }
                                },
                                "required": ["quote", "author"]
                            }
                        },
                        {
                            "name": "generate_random_quote_card",
                            "description": "Generate a quote card with a random quote and/or theme",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "theme": {
                                        "type": "string",
                                        "description": f"Visual theme. Options: {', '.join(THEMES.keys())}. Leave empty for random."
                                    },
                                    "quotes_file": {
                                        "type": "string",
                                        "description": "Path to JSON file with quotes"
                                    }
                                }
                            }
                        },
                        {
                            "name": "list_quote_themes",
                            "description": "List all available visual themes for quote cards",
                            "inputSchema": {
                                "type": "object",
                                "properties": {}
                            }
                        }
                    ]
                }
            }

        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})

            if tool_name == "generate_quote_card":
                result = generate_card(
                    quote=tool_args["quote"],
                    author=tool_args["author"],
                    theme=tool_args.get("theme", "minimal"),
                    brand=tool_args.get("brand")
                )
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": f"✅ Quote card generated!\n\nPath: {result['path']}\nTheme: {result['theme']}\n\nCaption (copy-paste ready):\n{result['caption']}"
                        }]
                    }
                }

            elif tool_name == "generate_random_quote_card":
                result = generate_random_card(
                    quotes_file=tool_args.get("quotes_file"),
                    theme=tool_args.get("theme")
                )
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": f"✅ Random quote card generated!\n\nQuote: \"{result['quote']}\"\nAuthor: {result['author']}\nTheme: {result['theme']}\nPath: {result['path']}\n\nCaption:\n{result['caption']}"
                        }]
                    }
                }

            elif tool_name == "list_quote_themes":
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
                            "text": f"🎨 Available themes:\n\n{theme_list}"
                        }]
                    }
                }

            else:
                raise ValueError(f"Unknown tool: {tool_name}")

        elif method == "notifications/initialized":
            # Notification, no response needed
            return None

        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Unknown method: {method}"
                }
            }

    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {
                "code": -32000,
                "message": str(e)
            }
        }


def main():
    """Run the MCP server (stdio transport)."""
    import sys

    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    load_dotenv(Path(__file__).parent.parent.parent / ".env")

    print("QuoteCard MCP Server started", file=sys.stderr)

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
