# API Testing Framework

A testing framework with sophisticated mock/live control for API testing.

## Features

- **Single Variable Control**: Change `api_config.global_mode` to toggle ALL components
- **Granular Overrides**: Override specific components without changing others
- **Fixture Capture**: Automatically saves live API responses for future mock tests
- **Zero Config Mocking**: Just set mode to MOCK and fixtures are used automatically

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up your API key
echo "GEMINI_API_KEY=your-key-here" > .env

# Run tests (mock mode by default)
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

```python
from gemini_client import GeminiClient, generate_text

# Using default client
response = generate_text("Hello, world!")

# Using custom client
client = GeminiClient(capture_fixtures=True)
response = client.generate("What is 2+2?")
print(response["text"])
```

## File Structure

```
api-testing-framework/
├── config.py           # MockConfig class and api_config instance
├── gemini_client.py    # Gemini API client with mock/live support
├── fixtures/           # Auto-captured API responses
│   └── gemini/         # Gemini-specific fixtures
├── tests/
│   ├── conftest.py     # pytest fixtures (mock_mode, live_mode, etc.)
│   ├── test_config.py  # Tests for config system
│   └── test_gemini.py  # Tests for Gemini client
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
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_MODE` | Global mode (LIVE/MOCK) | MOCK |
| `GEMINI_API_KEY` | Gemini API key | Required for LIVE |

