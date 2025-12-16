# API Testing Framework

A testing framework with sophisticated mock/live control for API testing.

> **Part of:** [_personal_sandbox_CJT01](../../README.md)

## Supported Providers

| Provider | Client | Model Default | Status |
|----------|--------|---------------|--------|
| **Google Gemini** | `gemini_client.py` | gemini-2.5-flash | ✅ Ready |
| **OpenAI** | `openai_client.py` | gpt-4o-mini | ✅ Ready |
| **Anthropic** | `anthropic_client.py` | claude-3-5-sonnet | ✅ Ready |
| **Pixel Lab** | `pixellab_client.py` | v2 API | ✅ Ready |

## Features

- **Single Variable Control**: Change `api_config.global_mode` to toggle ALL components
- **Granular Overrides**: Override specific components without changing others
- **Fixture Capture**: Automatically saves live API responses for future mock tests
- **Zero Config Mocking**: Just set mode to MOCK and fixtures are used automatically
- **Multi-Provider**: Same pattern works for Gemini, OpenAI, Anthropic, and Pixel Lab

## Architecture Decision

This framework uses the **Config Dict + Overrides** pattern, selected via weighted decision matrix analysis (score: 4.85/5.00).

**Why this approach:**
- Maximum simplicity - just a Python dict, no magic
- Single toggle - change one value and everything follows
- Full granular control - add component overrides to one dict
- Test-friendly - swap entire config in pytest fixtures

See `../../scripts/evaluate_testing_framework.py` to run the full evaluation.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up your API keys (.env file)
GEMINI_API_KEY=your-gemini-key
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
PIXELLAB_API_KEY=your-pixellab-key

# Run tests (mock mode by default - 30 tests)
pytest

# Run tests with live API
API_MODE=LIVE pytest -m live
```

## Usage

### Basic Mode Control

```python
from config import api_config

# Check current mode
print(api_config.global_mode)  # "MOCK" by default

# Set everything to LIVE
api_config.global_mode = "LIVE"

# Set everything to MOCK
api_config.global_mode = "MOCK"
```

### Granular Overrides

```python
from config import api_config

# Everything MOCK except gemini (for integration testing)
api_config.global_mode = "MOCK"
api_config.set_override("gemini", "LIVE")

# Everything LIVE except expensive APIs (for development)
api_config.global_mode = "LIVE"
api_config.set_override("billing_api", "MOCK")
api_config.set_override("analytics_api", "MOCK")
```

### Convenience Functions

```python
from config import mock_except, live_except

# MOCK everything except these components
mock_except("gemini", "fast_api")

# LIVE everything except these components
live_except("slow_api", "expensive_api")
```

### In Tests

```python
def test_with_mock(mock_mode):
    """Test runs in MOCK mode."""
    client = GeminiClient()
    # Uses fixtures, no API calls

def test_with_live(live_mode):
    """Test runs in LIVE mode."""
    client = GeminiClient()
    # Makes real API calls, captures fixtures
```

## API Client Usage

### Gemini
```python
from gemini_client import GeminiClient, generate_text

client = GeminiClient()
response = client.generate("What is 2+2?")
print(response["text"])
```

### OpenAI
```python
from openai_client import OpenAIClient, generate_text

client = OpenAIClient()  # Uses gpt-4o-mini by default
response = client.generate("What is 2+2?")
print(response["text"])

# Or use GPT-4
client = OpenAIClient(model="gpt-4")
```

### Anthropic
```python
from anthropic_client import AnthropicClient, generate_text

client = AnthropicClient()  # Uses claude-3-5-sonnet by default
response = client.generate("What is 2+2?")
print(response["text"])

# Or use Haiku for faster/cheaper
client = AnthropicClient(model="claude-3-haiku-20240307")
```

### Pixel Lab
```python
from pixellab_client import PixelLabClient, generate_image

client = PixelLabClient()
response = client.generate_image(
    description="a cute wizard with a blue hat",
    width=64,
    height=64
)
# response["images"] contains list of base64-encoded images

# Create character with 4 directions
character = client.create_character_4_directions(
    description="brave knight with shining armor",
    width=64,
    height=64
)
# Returns character_id and background_job_id for async processing
```

### Multi-Provider Example
```python
from config import api_config, mock_except
from gemini_client import GeminiClient
from openai_client import OpenAIClient
from anthropic_client import AnthropicClient

# All MOCK except OpenAI (for comparison testing)
mock_except("openai")

gemini = GeminiClient()
openai = OpenAIClient()
claude = AnthropicClient()

prompt = "Explain quantum computing in one sentence."

# Only OpenAI makes a real API call
responses = {
    "gemini": gemini.generate_text(prompt),   # From fixture
    "openai": openai.generate_text(prompt),   # Live API
    "claude": claude.generate_text(prompt),   # From fixture
}
```

## File Structure

```
api-testing-framework/
├── config.py             # MockConfig class and api_config instance
├── gemini_client.py      # Gemini API client with mock/live support
├── openai_client.py      # OpenAI API client with mock/live support
├── anthropic_client.py   # Anthropic API client with mock/live support
├── pixellab_client.py    # Pixel Lab API client with mock/live support
├── fixtures/             # Auto-captured API responses
│   ├── gemini/           # Gemini-specific fixtures
│   ├── openai/           # OpenAI-specific fixtures
│   ├── anthropic/        # Anthropic-specific fixtures
│   └── pixellab/         # Pixel Lab-specific fixtures
├── tests/
│   ├── conftest.py       # pytest fixtures (mock_mode, live_mode, etc.)
│   ├── test_config.py    # Tests for config system
│   ├── test_gemini.py    # Tests for Gemini client
│   ├── test_openai.py    # Tests for OpenAI client
│   ├── test_anthropic.py # Tests for Anthropic client
│   └── test_pixellab.py  # Tests for Pixel Lab client
├── requirements.txt
└── README.md
```

## How Fixtures Work

1. **Capture**: When in LIVE mode, API responses are automatically saved to `fixtures/`
2. **Replay**: When in MOCK mode, saved fixtures are loaded instead of making API calls
3. **Deterministic**: Same prompt always maps to same fixture file (hash-based naming)

## Running Tests

```bash
# Run all tests (uses MOCK mode, fixtures required)
pytest

# Run only config tests (no API needed)
pytest tests/test_config.py

# Run live API tests
pytest -m live

# Run tests excluding live
pytest -m "not live"

# Verbose output
pytest -v

# See test coverage
pytest --cov=. --cov-report=term-missing
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_MODE` | Global mode (LIVE/MOCK) | MOCK |
| `GEMINI_API_KEY` | Gemini API key | Required for LIVE gemini |
| `OPENAI_API_KEY` | OpenAI API key | Required for LIVE openai |
| `ANTHROPIC_API_KEY` | Anthropic API key | Required for LIVE anthropic |
| `PIXELLAB_API_KEY` | Pixel Lab API key | Required for LIVE pixellab |

## Dependencies

- `google-generativeai` - Gemini API client
- `openai` - OpenAI API client
- `anthropic` - Anthropic API client
- `requests` - HTTP client for Pixel Lab API
- `python-dotenv` - Environment variable management
- `pytest` - Testing framework

## Extending to Other APIs

To add a new API client:

1. Create `new_client.py` following `gemini_client.py` pattern
2. Use `api_config.get_mode("new_api")` to check mode
3. Create fixtures directory: `fixtures/new_api/`
4. Add tests in `tests/test_new_api.py`

```python
# Example: new_client.py
from config import api_config

class NewClient:
    def __init__(self):
        self.mode = api_config.get_mode("new_api")

    def call_api(self, params):
        if self.mode == "MOCK":
            return self._load_fixture(params)
        else:
            return self._call_live(params)
```
