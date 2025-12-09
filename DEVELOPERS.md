# Developer Guide

This guide covers development practices, conventions, and workflows for this sandbox repository.

## Table of Contents
- [Project Structure](#project-structure)
- [Adding New Code](#adding-new-code)
- [Tools vs Scripts](#tools-vs-scripts)
- [Work Efforts System](#work-efforts-system)
- [AI-Assisted Development](#ai-assisted-development)
- [Security Practices](#security-practices)
- [Commit Guidelines](#commit-guidelines)

---

## Project Structure

```
_personal_sandbox_CJT01/
├── projects/           # Standalone experiments with their own structure
├── tools/              # Reusable Python packages (importable)
├── scripts/            # One-off scripts (run directly)
├── snippets/           # Code fragments for copy-paste reference
├── learning/           # Tutorials and practice code
├── scratch/            # Temporary work (gitignored)
├── .private/           # Security scripts & reports (gitignored)
├── .cursor/            # Cursor IDE configuration (gitignored)
│   └── scripts/        # AI session automation scripts
└── _work_efforts_/     # Project tracking (gitignored, local-only)
```

---

## Adding New Code

### Decision Tree

```
Is this a standalone project with its own dependencies?
├── YES → projects/<project-name>/
└── NO → Continue...

Is this reusable code you'll import from multiple places?
├── YES → tools/<module>.py
└── NO → Continue...

Is this a one-off script you run directly?
├── YES → scripts/<script>.py
└── NO → Continue...

Is this a code snippet for reference?
├── YES → snippets/<language>/<snippet>.py
└── NO → Continue...

Is this temporary/experimental work?
├── YES → scratch/<anything> (gitignored)
└── NO → Consider where it best fits
```

### Creating a New Project

```bash
mkdir -p projects/my-project
cd projects/my-project

# Create standard files
touch README.md
touch requirements.txt  # or package.json, Cargo.toml, etc.

# Add a .env.example if using environment variables
touch .env.example
```

### Creating a New Tool

```bash
# Create the module
touch tools/my_utility.py

# Update tools/__init__.py to export it
# Then import: from tools.my_utility import my_function
```

---

## Tools vs Scripts

| Aspect | `tools/` | `scripts/` |
|--------|----------|------------|
| **Purpose** | Reusable libraries | One-off automation |
| **Usage** | `from tools.x import y` | `python scripts/x.py` |
| **Dependencies** | Import from anywhere | Run standalone |
| **Structure** | Package with `__init__.py` | Single files |
| **Examples** | decision_matrix.py | evaluate_testing_framework.py |

### tools/ Example
```python
# tools/my_utility.py
def helper_function():
    return "I can be imported anywhere"

# Usage in any file:
from tools.my_utility import helper_function
```

### scripts/ Example
```python
#!/usr/bin/env python3
# scripts/my_script.py
"""Run this directly: python scripts/my_script.py"""

if __name__ == "__main__":
    print("I run as a standalone script")
```

---

## Work Efforts System

Work efforts use the **Johnny Decimal** system for organization. They are **local-only** (gitignored) to keep personal notes, plans, and decisions private.

### Structure
```
_work_efforts_/
├── 00-09_admin/           # Administration & meta
│   ├── 00_organization/   # System organization
│   └── 01_devlog/         # Development logs
├── 10-19_projects/        # Project tracking
├── 20-29_learning/        # Learning efforts
├── 30-39_experiments/     # Experiment tracking
├── 40-49_utilities/       # Utility work
└── 50-59_archive/         # Completed work
```

### Naming Convention
```
XX.YY_descriptive_name.md

XX = Category (00-99)
YY = Document number (00-99)
00 = Always the index file
```

### Creating a Work Effort
1. Find the appropriate category
2. Get next available number from index
3. Create file: `XX.YY_YYYY-MM-DD_topic.md`
4. Update the category index
5. Update the devlog

---

## AI-Assisted Development

This repo includes automation scripts for AI coding sessions.

### Pre-flight Check (Before Creating Files)
```bash
python3 .cursor/scripts/preflight.py "search term"
```
- Searches for existing files with similar names
- Finds related code in the codebase
- Lists related work efforts
- **Prevents accidental duplication**

### Post-flight Check (After Making Changes)
```bash
python3 .cursor/scripts/postflight.py
```
- Verifies Python syntax
- Checks Johnny Decimal compliance
- Reviews git status
- Confirms devlog is updated

### AI Session Protocol
See `.cursor/scripts/ai_session_protocol.md` for the full workflow.

**Key Rules:**
1. Always run pre-flight before creating new files
2. Search source code, not just documentation
3. Never rationalize keeping duplicates—consolidate
4. Update devlog after every session
5. Run post-flight to verify compliance

---

## Security Practices

### Security Checkup Script
```bash
python3 .private/security_checkup.py
```

**Checks for:**
- Exposed secrets (API keys, passwords, tokens)
- Dangerous files not in gitignore
- Gitignore completeness
- Potential security issues

**Reports saved to:** `.private/reports/`

### What's Gitignored
| Pattern | Reason |
|---------|--------|
| `.env*` | Environment variables with secrets |
| `.private/` | Security scripts and reports |
| `_work_efforts_/` | Personal notes and plans |
| `scratch/` | Temporary experiments |
| `*.pem`, `*.key` | Certificates and keys |

### Best Practices
- Never commit `.env` files
- Use `.env.example` for templates
- Run security checkup before pushing
- Keep secrets in environment variables

---

## Commit Guidelines

### Message Format
```
<action>: <brief description>

- Detail 1
- Detail 2
```

### Actions
| Action | When to Use |
|--------|-------------|
| `Add` | New feature or file |
| `Update` | Enhancement to existing feature |
| `Fix` | Bug fix |
| `Remove` | Deleting code or features |
| `Refactor` | Code restructuring without behavior change |
| `Docs` | Documentation only |
| `Test` | Test additions or changes |

### Examples
```bash
# Good
git commit -m "Add decision matrix utility for quantitative analysis"
git commit -m "Fix import path in evaluate_testing_framework.py"
git commit -m "Update README with tools documentation"

# Bad
git commit -m "stuff"
git commit -m "WIP"
git commit -m "fixed things"
```

---

## Quick Reference

### Common Commands
```bash
# Run tests for a project
cd projects/api-testing-framework && pytest

# Use decision matrix
python -c "from tools.decision_matrix import make_decision; help(make_decision)"

# Pre-flight check
python3 .cursor/scripts/preflight.py "topic"

# Post-flight check
python3 .cursor/scripts/postflight.py

# Security checkup
python3 .private/security_checkup.py
```

### File Locations
| Need | Location |
|------|----------|
| Reusable utility | `tools/` |
| One-off script | `scripts/` |
| New project | `projects/<name>/` |
| Temporary work | `scratch/` |
| Code reference | `snippets/` |
| Development log | `_work_efforts_/00-09_admin/01_devlog/` |
| Security reports | `.private/reports/` |

---

## Troubleshooting

### Import Error: "No module named 'tools'"
Run Python from the project root:
```bash
cd /path/to/_personal_sandbox_CJT01
python -c "from tools.decision_matrix import make_decision"
```

Or add to PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/_personal_sandbox_CJT01"
```

### Pre/Post-flight Scripts Not Found
Scripts are in `.cursor/scripts/` which is gitignored. They're created during AI sessions. To recreate, ask the AI assistant to set up the automation scripts.

### Work Efforts Missing
`_work_efforts_/` is gitignored and stays local. Each developer maintains their own. See the Work Efforts System section to set up.

---

*Last updated: 2025-12-08*
