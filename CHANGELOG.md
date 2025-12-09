# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-12-08

### Added

#### Tools Package (`tools/`)
- **Decision Matrix Utility** (`decision_matrix.py`) - Quantitative decision-making with weighted criteria
  - 4 analysis methods: weighted, normalized, ranking, best-worst
  - Confidence scoring and recommendations
  - Strengths/weaknesses breakdown per option
  - JSON export for serialization
  - Comparison tables and method consensus

#### API Testing Framework (`projects/api-testing-framework/`)
- **Mock/Live Control System** - Single variable toggle for all API components
  - `api_config.global_mode` controls everything
  - Per-component overrides with `set_override()`
  - Convenience functions: `mock_except()`, `live_except()`
- **Gemini API Client** - Full client with fixture capture/replay
- **OpenAI API Client** - GPT-4/3.5 with fixture capture/replay
- **Anthropic API Client** - Claude with fixture capture/replay
- **Fixture System** - Auto-captures live responses for mock tests
- **Test Suite** - 30 passing tests (config, mock, live, all providers)

#### Documentation
- `README.md` - Project overview with directory guide
- `DEVELOPERS.md` - Comprehensive development guidelines
- `CHANGELOG.md` - This file

#### Automation (Local-only)
- Pre-flight check script - Prevents duplicate file creation
- Post-flight check script - Verifies compliance after changes
- Security checkup script - Scans for exposed secrets
- AI session protocol documentation

### Project Structure
```
_personal_sandbox_CJT01/
├── projects/api-testing-framework/  # API testing with mock/live control
├── tools/decision_matrix.py         # Reusable decision matrix utility
├── scripts/                         # One-off automation scripts
├── DEVELOPERS.md                    # Developer guide
├── CHANGELOG.md                     # This file
└── VERSION                          # Current version (0.1.0)
```

### Technical Decisions
- **Config Dict + Overrides** pattern for API mock/live control (scored 4.85/5.00 in decision matrix)
- **Johnny Decimal** system for work effort organization (local-only)
- **tools/ vs scripts/** separation for reusable packages vs one-off scripts

---

## [Unreleased]

### Added
- **OpenAI API Client** (`openai_client.py`) - GPT-4/3.5 with mock/live support
- **Anthropic API Client** (`anthropic_client.py`) - Claude with mock/live support
- Test suites for new clients (30 total tests, up from 21)
- Fixture directories for OpenAI and Anthropic

### Changed
- Updated `requirements.txt` with `openai` and `anthropic` packages
- Updated API testing framework README with multi-provider documentation

### Technical Decisions
- Used decision matrix to select "Expand API Framework" direction (score: 8.75/10)
- Maintained same pattern across all providers for consistency

### Planned
- More utilities in `tools/`
- Enhanced fixture management
- Unified multi-provider interface

[0.1.0]: https://github.com/ctavolazzi/_personal_sandbox_CJT01/releases/tag/v0.1.0
[Unreleased]: https://github.com/ctavolazzi/_personal_sandbox_CJT01/compare/v0.1.0...HEAD
