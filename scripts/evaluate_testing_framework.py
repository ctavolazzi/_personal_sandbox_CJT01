#!/usr/bin/env python3
"""
Evaluate 5 alternatives for the API Testing Framework architecture.

Requirements from user:
1. Single variable to toggle ALL components between LIVE/MOCK
2. Granular per-component override capability  
3. Component-level overrides should work WITHOUT changing many variables
4. Use real API responses as fixtures for future tests
"""

from decision_matrix import Alternative, print_matrix

# =============================================================================
# DEFINE 5 ALTERNATIVES
# =============================================================================

alternatives = [
    Alternative(
        name="1. Env Var Cascade",
        description=(
            "Global API_MODE env var (LIVE/MOCK) + per-component overrides like "
            "API_MODE_GEMINI=LIVE. Components check their specific var first, "
            "fall back to global. Simple but scattered across environment."
        ),
        scores={
            "simplicity": 4,      # Easy concept, but env vars get messy
            "single_toggle": 5,   # Just change API_MODE
            "granular": 3,        # Works but requires knowing all component names
            "testability": 3,     # Env vars can be tricky in pytest
            "maintainability": 2, # Env vars scattered, hard to see full config
            "discoverability": 2, # Can't easily see what components exist
        }
    ),
    
    Alternative(
        name="2. Config Dict + Overrides",
        description=(
            "Single Python dict: {'global': 'MOCK', 'overrides': {'gemini': 'LIVE'}}. "
            "Components query config.get_mode('component_name'). All config visible "
            "in one place. Override dict can be empty for pure global control."
        ),
        scores={
            "simplicity": 5,      # Dead simple, one dict
            "single_toggle": 5,   # Change config['global']
            "granular": 5,        # Just add to overrides dict
            "testability": 5,     # Easy to swap config in tests
            "maintainability": 4, # All in one place, but manual
            "discoverability": 4, # Can inspect config to see structure
        }
    ),
    
    Alternative(
        name="3. Decorator Registry",
        description=(
            "@mockable('gemini') decorator registers components. Central registry "
            "tracks all mockable components. Toggle via registry.set_global(MOCK) "
            "or registry.set('gemini', LIVE). Pythonic but more complex."
        ),
        scores={
            "simplicity": 3,      # Decorators add cognitive load
            "single_toggle": 5,   # registry.set_global()
            "granular": 5,        # registry.set() per component
            "testability": 4,     # Good, but decorator magic can confuse
            "maintainability": 3, # Must understand decorator system
            "discoverability": 5, # Registry knows all components
        }
    ),
    
    Alternative(
        name="4. Context Manager Scopes",
        description=(
            "with mock_mode(): or with live_mode(): blocks. Nested contexts for "
            "overrides: with mock_mode(): with live_for('gemini'):. Clean for "
            "test blocks but awkward for application-wide settings."
        ),
        scores={
            "simplicity": 3,      # Context managers are clean but nested gets ugly
            "single_toggle": 4,   # Works but requires wrapping code
            "granular": 4,        # Nested contexts work but verbose
            "testability": 5,     # Perfect for pytest fixtures
            "maintainability": 3, # Nesting can get confusing
            "discoverability": 2, # No central registry of components
        }
    ),
    
    Alternative(
        name="5. DI Container",
        description=(
            "Dependency injection container (like dependency-injector). Register "
            "MockGeminiClient and LiveGeminiClient, container decides which to inject "
            "based on config. Most flexible but heaviest abstraction."
        ),
        scores={
            "simplicity": 1,      # DI containers are complex
            "single_toggle": 4,   # Container config controls all
            "granular": 5,        # Full control over every dependency
            "testability": 5,     # DI is designed for testability
            "maintainability": 2, # Steep learning curve, lots of boilerplate
            "discoverability": 4, # Container knows all dependencies
        }
    ),
]

# =============================================================================
# CRITERIA WEIGHTS (must sum to 1.0)
# =============================================================================
# Weighted based on user's stated priorities:
# - Single variable control: HIGH (explicitly requested)
# - Granular override: HIGH (explicitly requested)
# - Simplicity: HIGH (user wants minimal complexity)
# - Testability: MEDIUM (important but implied)
# - Maintainability: MEDIUM (long-term concern)
# - Discoverability: LOW (nice to have)

criteria = {
    "simplicity": 0.25,       # User explicitly dislikes complexity
    "single_toggle": 0.25,    # "change ONLY ONE variable"
    "granular": 0.20,         # "granular control built in from the very start"
    "testability": 0.15,      # Must work well with tests
    "maintainability": 0.10,  # Long-term maintainability
    "discoverability": 0.05,  # Ability to see what's mockable
}

# =============================================================================
# RUN EVALUATION
# =============================================================================

if __name__ == "__main__":
    winner = print_matrix(alternatives, criteria)
    
    print("\n" + "=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)
    print(f"""
Based on the weighted criteria analysis, '{winner[0]}' is the recommended approach.

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

