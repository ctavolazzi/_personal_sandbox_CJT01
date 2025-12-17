# AI Agent Instructions

This document provides instructions for AI assistants working with this codebase, including MCP (Model Context Protocol) server configurations and usage guidelines.

## ⚠️ Pre-Work Checklist

**Before starting any work session, AI assistants MUST:**

1. **Check current date and time:**
   ```bash
   date
   ```
   - Verify you have the correct date and time
   - This ensures proper context for time-sensitive operations

2. **Read this file (AGENTS.md):**
   - Review MCP server configurations
   - Check available tools and their status
   - Understand testing requirements (mock-only for cost control)
   - Review environment variable requirements

3. **Test MCP server connectivity (mock mode only):**
   - Run MCP server tests to verify servers are loaded and working
   - **IMPORTANT:** Use mock mode only - no real API calls that incur costs
   - See [MCP Server Testing](#mcp-server-testing) section below

4. **Check related work efforts:**
   - Review `_work_efforts/` for relevant active work
   - Check if task relates to existing work efforts
   - Update or create work efforts as needed

**Failure to complete this checklist may result in:**
- Incorrect date/time context
- Unnecessary API costs
- Duplicate work
- Missing configuration context

## MCP Servers

This project uses Model Context Protocol (MCP) servers to extend AI assistant capabilities. MCP servers are configured in `.cursor/mcp.json` (project-local) or in Cursor's global settings.

### Configuration Location

- **Project-local:** `.cursor/mcp.json` (gitignored, per-project configuration)
- **Global:** Cursor Settings → MCP → Add Custom MCP

### Available MCP Servers

#### 1. Pixel Lab API Server

**Type:** HTTP-based remote server
**Purpose:** Generate pixel art characters, animations, and tilesets for game development
**Status:** ✅ Configured

**Configuration:**
```json
{
  "mcpServers": {
    "pixellab": {
      "url": "https://api.pixellab.ai/mcp",
      "transport": "http",
      "headers": {
        "Authorization": "Bearer ${PIXELLAB_API_TOKEN}"
      }
    }
  }
}
```

**Setup:**
1. Set `PIXELLAB_API_TOKEN` environment variable (separate from `PIXELLAB_API_KEY` used by Python client)
2. Restart Cursor to load configuration
3. Reference `https://api.pixellab.ai/mcp/docs` in prompts to see available tools

**Available Tools:**
- `create_character` - Create pixel art characters with 4 or 8 directional views
- `animate_character` - Add animations to existing characters (walk, run, idle, etc.)
- `create_topdown_tileset` - Generate Wang tilesets for seamless terrain transitions
- `create_sidescroller_tileset` - Generate platform tilesets for 2D platformer games
- `create_isometric_tile` - Create individual isometric tiles
- `create_map_object` - Create pixel art objects with transparent backgrounds

**Usage Example:**
```
@https://api.pixellab.ai/mcp/docs

Create a pixel art wizard character with 8 directions, then animate it walking.
```

**Documentation:** https://api.pixellab.ai/mcp/docs

---

#### 2. DiagramForge MCP Server

**Type:** Local Python server
**Purpose:** Generate diagrams from text descriptions or Mermaid syntax
**Status:** ⚠️ Available but not configured in `.cursor/mcp.json`

**Configuration:**
```json
{
  "mcpServers": {
    "diagramforge": {
      "command": "python3",
      "args": ["/Users/ctavolazzi/Code/_personal_sandbox_CJT01/projects/diagramforge/server.py"]
    }
  }
}
```

**Setup:**
1. Ensure dependencies are installed: `cd projects/diagramforge && pip install -r requirements.txt`
2. Set `GEMINI_API_KEY` in environment (used for diagram generation)
3. Add configuration to `.cursor/mcp.json`
4. Restart Cursor

**Available Tools:**
- Generate flowcharts, sequence diagrams, architecture diagrams
- Support for 7 diagram types and 10 visual themes
- Accepts plain text descriptions or Mermaid syntax

**Usage Example:**
```
Generate a flowchart showing user authentication flow with neon theme
Create an architecture diagram for a microservices system
```

**Location:** `projects/diagramforge/server.py`
**Documentation:** `projects/diagramforge/README.md`

---

#### 3. QuoteCard MCP Server

**Type:** Local Python server
**Purpose:** Generate quote graphics for social media
**Status:** ⚠️ Available but not configured in `.cursor/mcp.json`

**Configuration:**
```json
{
  "mcpServers": {
    "quotecard": {
      "command": "python3",
      "args": ["/Users/ctavolazzi/Code/_personal_sandbox_CJT01/projects/quotecard/server.py"]
    }
  }
}
```

**Setup:**
1. Ensure dependencies are installed: `cd projects/quotecard && pip install -r requirements.txt`
2. Set `GEMINI_API_KEY` in environment (used for background generation)
3. Add configuration to `.cursor/mcp.json`
4. Restart Cursor

**Available Tools:**
- Generate quote cards with 12 visual themes
- Support for custom quotes, authors, and branding
- Random quote generation

**Usage Example:**
```
Generate a quote card with 'Dream big' by Norman Vaughan, use the cyberpunk theme
Make a random motivational quote graphic
List available quote card themes
```

**Location:** `projects/quotecard/server.py`
**Documentation:** `projects/quotecard/README.md`

---

## MCP Server Testing

**CRITICAL: Always use MOCK mode for testing - no real API calls that incur costs.**

### Testing Philosophy

All MCP server tests should:
- ✅ Use mock/fixture data when available
- ✅ Verify server connectivity and tool availability
- ✅ Test tool schemas and parameter validation
- ❌ **NEVER make real API calls that cost money**
- ❌ **NEVER generate actual images/diagrams unless explicitly requested**

### Testing Pixel Lab MCP Server

The Pixel Lab Python client has built-in mock/live support. Use it for testing:

```bash
cd projects/api-testing-framework

# Run tests in MOCK mode (default, no API costs)
pytest tests/test_pixellab.py -m mock

# Verify MCP server tools are available (no calls made)
# In Cursor, check MCP server status in Output panel
```

**Mock Testing Steps:**
1. Set `API_MODE=MOCK` (default)
2. Run pytest tests - they use fixtures, not real API calls
3. Verify fixtures exist in `fixtures/pixellab/`
4. If fixtures missing, create them manually or use a test token

### Testing Local Python MCP Servers (DiagramForge, QuoteCard)

For local Python servers, test the server directly without making API calls:

```bash
# Test DiagramForge server (dry-run, no API calls)
cd projects/diagramforge
python3 -c "
import sys
sys.path.insert(0, '.')
from server import handle_request
# Test initialize request (no API call)
result = handle_request({'method': 'initialize', 'id': 1})
print('Server responds:', result.get('result', {}).get('serverInfo', {}).get('name'))
"

# Test QuoteCard server (dry-run, no API calls)
cd projects/quotecard
python3 -c "
import sys
sys.path.insert(0, '.')
from server import handle_request
# Test tools/list request (no API call)
result = handle_request({'method': 'tools/list', 'id': 1})
print('Available tools:', len(result.get('result', {}).get('tools', [])))
"
```

### Verifying MCP Server Status in Cursor

1. **Check MCP Server Logs:**
   - Open Cursor's Output panel
   - Select "MCP" from the dropdown
   - Look for server initialization messages
   - Verify no authentication errors

2. **List Available Tools:**
   - Use Cursor's MCP tool browser (if available)
   - Or check server documentation URLs:
     - Pixel Lab: `https://api.pixellab.ai/mcp/docs`
     - DiagramForge: See `projects/diagramforge/README.md`
     - QuoteCard: See `projects/quotecard/README.md`

3. **Test Tool Schema (No Execution):**
   ```
   @https://api.pixellab.ai/mcp/docs

   What tools are available from the Pixel Lab MCP server?
   Show me the schema for create_character tool (don't execute it).
   ```

### Cost Control Rules

| Test Type | Allowed? | Notes |
|-----------|----------|-------|
| Mock/fixture tests | ✅ Yes | Use existing fixtures, no cost |
| Schema inspection | ✅ Yes | Just reading tool definitions |
| Server connectivity | ✅ Yes | Just checking if server responds |
| Tool list requests | ✅ Yes | No actual API calls |
| Real API calls | ❌ **NO** | Only if explicitly requested by user |
| Image generation | ❌ **NO** | Only if explicitly requested by user |
| Diagram generation | ❌ **NO** | Only if explicitly requested by user |

### Creating Test Fixtures

If you need to create fixtures for testing (one-time setup):

1. **Use test/development API keys** (not production)
2. **Set explicit mode to LIVE** for fixture creation only:
   ```python
   from config import api_config
   api_config.global_mode = "LIVE"
   # Make ONE test call to capture fixture
   api_config.global_mode = "MOCK"  # Immediately revert
   ```
3. **Document fixture creation** in work efforts
4. **Never commit API keys** - use environment variables

---

## Environment Variables

MCP servers require the following environment variables:

| Variable | Purpose | Used By |
|----------|---------|---------|
| `PIXELLAB_API_TOKEN` | Pixel Lab API authentication | Pixel Lab MCP server |
| `GEMINI_API_KEY` | Google Gemini API for image generation | DiagramForge, QuoteCard |
| `PIXELLAB_API_KEY` | Pixel Lab API for Python client | `pixellab_client.py` (separate from MCP) |

**Note:** `PIXELLAB_API_TOKEN` and `PIXELLAB_API_KEY` can use the same value, but they're separate variables for different purposes (MCP vs Python client).

---

## Adding New MCP Servers

To add a new MCP server:

1. **For HTTP-based servers:**
   ```json
   {
     "mcpServers": {
       "server-name": {
         "url": "https://api.example.com/mcp",
         "transport": "http",
         "headers": {
           "Authorization": "Bearer ${API_TOKEN}"
         }
       }
     }
   }
   ```

2. **For local Python servers:**
   ```json
   {
     "mcpServers": {
       "server-name": {
         "command": "python3",
         "args": ["/absolute/path/to/server.py"]
       }
     }
   }
   ```

3. **Update this file** with server documentation
4. **Restart Cursor** to load the new configuration

---

## Best Practices

1. **Use environment variables** for API tokens/keys (never hardcode)
2. **Reference documentation URLs** in prompts to help AI discover available tools
3. **Test server connectivity** after configuration changes
4. **Keep `.cursor/mcp.json` gitignored** (already configured in `.gitignore`)
5. **Document new servers** in this file for future reference

---

## Troubleshooting

### MCP Server Not Working

1. **Check environment variables:**
   ```bash
   echo $PIXELLAB_API_TOKEN
   echo $GEMINI_API_KEY
   ```

2. **Verify configuration syntax:**
   ```bash
   cat .cursor/mcp.json | python3 -m json.tool
   ```

3. **Check server logs:**
   - Open Cursor's MCP server logs (usually in Output panel)
   - Look for connection errors or authentication failures

4. **Restart Cursor:**
   - MCP configuration changes require a full restart

### Local Python Servers Not Starting

1. **Check Python path:**
   ```bash
   which python3
   ```

2. **Verify dependencies:**
   ```bash
   cd projects/diagramforge && pip install -r requirements.txt
   ```

3. **Test server manually:**
   ```bash
   python3 projects/diagramforge/server.py
   ```

4. **Check file permissions:**
   ```bash
   ls -la projects/diagramforge/server.py
   chmod +x projects/diagramforge/server.py  # if needed
   ```

---

## Related Documentation

- [DEVELOPERS.md](DEVELOPERS.md) - Development guidelines and conventions
- [README.md](README.md) - Project overview
- [projects/api-testing-framework/README.md](projects/api-testing-framework/README.md) - API testing framework (includes Pixel Lab Python client)

---

*Last updated: 2025-12-16*

---

## Quick Reference

### Start of Session Checklist
```bash
# 1. Check date/time
date

# 2. Read this file
cat AGENTS.md

# 3. Test MCP servers (mock mode)
cd projects/api-testing-framework
pytest tests/test_pixellab.py -m mock

# 4. Check work efforts
ls -la _work_efforts/10-19_development/10_active/
```

### Common Commands
```bash
# Test Pixel Lab client (mock mode, no cost)
cd projects/api-testing-framework
API_MODE=MOCK pytest tests/test_pixellab.py -m mock

# Verify MCP configuration
cat .cursor/mcp.json | python3 -m json.tool

# Check environment variables
echo $PIXELLAB_API_TOKEN
echo $GEMINI_API_KEY
```
