#!/usr/bin/env python3
"""
Evaluate 5 alternatives for the API Testing Framework architecture.

Requirements from user:
1. Single variable to toggle ALL components between LIVE/MOCK
2. Granular per-component override capability
3. Component-level overrides should work WITHOUT changing many variables
4. Use real API responses as fixtures for future tests

Now uses tools/decision_matrix for full-featured analysis.
"""

import sys
from pathlib import Path

# Add project root to path for tools import
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.decision_matrix import make_decision

# =============================================================================
# DEFINE ALTERNATIVES AND SCORES
# =============================================================================

# Alternative names
options = [
    "1. Env Var Cascade",
    "2. Config Dict + Overrides",
    "3. Decorator Registry",
    "4. Context Manager Scopes",
    "5. DI Container",
]

# Descriptions for reference
descriptions = {
    "1. Env Var Cascade": (
        "Global API_MODE env var (LIVE/MOCK) + per-component overrides like "
        "API_MODE_GEMINI=LIVE. Components check their specific var first, "
        "fall back to global. Simple but scattered across environment."
    ),
    "2. Config Dict + Overrides": (
        "Single Python dict: {'global': 'MOCK', 'overrides': {'gemini': 'LIVE'}}. "
        "Components query config.get_mode('component_name'). All config visible "
        "in one place. Override dict can be empty for pure global control."
    ),
    "3. Decorator Registry": (
        "@mockable('gemini') decorator registers components. Central registry "
        "tracks all mockable components. Toggle via registry.set_global(MOCK) "
        "or registry.set('gemini', LIVE). Pythonic but more complex."
    ),
    "4. Context Manager Scopes": (
        "with mock_mode(): or with live_mode(): blocks. Nested contexts for "
        "overrides: with mock_mode(): with live_for('gemini'):. Clean for "
        "test blocks but awkward for application-wide settings."
    ),
    "5. DI Container": (
        "Dependency injection container (like dependency-injector). Register "
        "MockGeminiClient and LiveGeminiClient, container decides which to inject "
        "based on config. Most flexible but heaviest abstraction."
    ),
}

# Criteria to evaluate against
criteria = [
    "simplicity",       # User explicitly dislikes complexity
    "single_toggle",    # "change ONLY ONE variable"
    "granular",         # "granular control built in from the very start"
    "testability",      # Must work well with tests
    "maintainability",  # Long-term maintainability
    "discoverability",  # Ability to see what's mockable
]

# Weights for each criterion (must correspond to criteria order)
weights = [0.25, 0.25, 0.20, 0.15, 0.10, 0.05]

# Scores for each alternative (order matches criteria list)
# Format: option_name -> [simplicity, single_toggle, granular, testability, maintainability, discoverability]
scores = {
    "1. Env Var Cascade":        [4, 5, 3, 3, 2, 2],
    "2. Config Dict + Overrides": [5, 5, 5, 5, 4, 4],
    "3. Decorator Registry":      [3, 5, 5, 4, 3, 5],
    "4. Context Manager Scopes":  [3, 4, 4, 5, 3, 2],
    "5. DI Container":            [1, 4, 5, 5, 2, 4],
}

# =============================================================================
# RUN EVALUATION
# =============================================================================

if __name__ == "__main__":
    result = make_decision(
        options=options,
        criteria=criteria,
        scores=scores,
        weights=weights,
        method="weighted"
    )

    print(result)
    print(result.comparison_table())

    print("\n" + "=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)

    winner = result.winner
    print(f"""
Based on the weighted criteria analysis, '{winner}' is the recommended approach.

DESCRIPTION:
{descriptions[winner]}

KEY REASONS:
1. Maximum simplicity - just a Python dict, no magic
2. Single toggle - change config['global'] and everything follows
3. Full granular control - add component overrides to one dict
4. Test-friendly - swap the entire config dict in pytest fixtures
5. Visible - all settings in one place, easy to debug

IMPLEMENTATION APPROACH:
- config.py: Single MockConfig class with get_mode(component) method
- api_client.py: Checks config.get_mode('gemini') before each call
- Fixtures saved to fixtures/ directory with timestamps
- pytest fixtures can override entire config for test isolation
""")
