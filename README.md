# Personal Sandbox CJT01

A personal catchall sandbox for coding experiments, prototypes, and learning projects.

## 📁 Structure

```
_personal_sandbox_CJT01/
├── projects/                # Standalone project experiments
│   └── api-testing-framework/  # Gemini API testing with mock/live control
├── tools/                   # Reusable Python utilities (importable)
│   └── decision_matrix.py   # Quantitative decision-making tool
├── scripts/                 # One-off scripts (run directly)
├── snippets/                # Code snippets and references
├── learning/                # Tutorials, courses, practice code
├── scratch/                 # Temporary experiments (gitignored)
├── .private/                # Security scripts & reports (gitignored)
└── _work_efforts_/          # Local-only project tracking (gitignored)
```

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/ctavolazzi/_personal_sandbox_CJT01.git
cd _personal_sandbox_CJT01

# Run the API testing framework
cd projects/api-testing-framework
pip install -r requirements.txt
pytest
```

## 📦 Available Tools

### Decision Matrix (`tools/decision_matrix.py`)
Quantitative decision-making with weighted criteria analysis.

```python
from tools.decision_matrix import make_decision

result = make_decision(
    options=["Option A", "Option B", "Option C"],
    criteria=["Cost", "Speed", "Quality"],
    scores={
        "Option A": [7, 8, 6],
        "Option B": [9, 5, 7],
        "Option C": [6, 9, 8]
    },
    weights=[0.3, 0.2, 0.5]
)
print(result)
```

**Features:**
- 4 analysis methods (weighted, normalized, ranking, best-worst)
- Confidence scoring and recommendations
- Strengths/weaknesses breakdown
- JSON export for serialization

## 📂 Active Projects

### API Testing Framework
**Location:** `projects/api-testing-framework/`

A testing framework for the Gemini API with sophisticated mock/live control:
- Single variable toggles all components between LIVE/MOCK
- Granular per-component override capability
- Captured API responses as fixtures for tests

See [projects/api-testing-framework/README.md](projects/api-testing-framework/README.md) for details.

## 🗂️ Directory Guide

| Directory | Purpose | Tracked in Git |
|-----------|---------|----------------|
| `projects/` | Standalone experiments | ✅ Yes |
| `tools/` | Reusable Python packages | ✅ Yes |
| `scripts/` | One-off automation scripts | ✅ Yes |
| `snippets/` | Code fragments for reference | ✅ Yes |
| `learning/` | Tutorials and practice | ✅ Yes |
| `scratch/` | Temporary work | ❌ No |
| `.private/` | Security scripts/reports | ❌ No |
| `_work_efforts_/` | Project tracking (Johnny Decimal) | ❌ No |

## 🛠️ Development

See [DEVELOPERS.md](DEVELOPERS.md) for detailed development guidelines.

### Prerequisites
- Python 3.10+
- Git

### Key Conventions
- **tools/** = Importable packages (`from tools.x import y`)
- **scripts/** = Run directly (`python scripts/x.py`)
- Keep scratch work in `/scratch/`
- Each project has its own README

## 📝 Notes

- This is a personal sandbox - code quality varies by purpose
- Some experiments may be incomplete or abandoned
- Work efforts and private files stay local (not pushed to GitHub)

## 📜 License

MIT License - See [LICENSE](LICENSE) for details.
