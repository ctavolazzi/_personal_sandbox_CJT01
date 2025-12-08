"""
Tools Package
-------------
Reusable Python utilities for the personal sandbox.

Available modules:
    - decision_matrix: Quantitative decision-making with weighted criteria
"""

from .decision_matrix import make_decision, compare_methods, DecisionMatrix, DecisionResult

__all__ = ["make_decision", "compare_methods", "DecisionMatrix", "DecisionResult"]
