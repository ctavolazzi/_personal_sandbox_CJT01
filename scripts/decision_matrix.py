#!/usr/bin/env python3
"""
Decision Matrix Tool
Evaluates alternatives against weighted criteria.
"""

from dataclasses import dataclass

@dataclass
class Alternative:
    name: str
    description: str
    scores: dict[str, int]  # criterion -> score (1-5)

def evaluate(alternatives: list[Alternative], criteria: dict[str, float]) -> list[tuple[str, float, str]]:
    """
    Evaluate alternatives against weighted criteria.
    
    Args:
        alternatives: List of alternatives with scores per criterion
        criteria: Dict of criterion_name -> weight (should sum to 1.0)
    
    Returns:
        Sorted list of (name, weighted_score, description)
    """
    results = []
    for alt in alternatives:
        weighted_score = sum(
            alt.scores.get(c, 0) * weight 
            for c, weight in criteria.items()
        )
        results.append((alt.name, weighted_score, alt.description))
    
    return sorted(results, key=lambda x: x[1], reverse=True)

def print_matrix(alternatives: list[Alternative], criteria: dict[str, float]):
    """Print a formatted decision matrix and results."""
    print("\n" + "=" * 80)
    print("DECISION MATRIX")
    print("=" * 80)
    
    # Header
    print(f"\n{'Alternative':<30} | ", end="")
    for c in criteria:
        print(f"{c[:8]:<10}", end="")
    print(f"{'WEIGHTED':<10}")
    print("-" * 80)
    
    results = evaluate(alternatives, criteria)
    result_map = {r[0]: r[1] for r in results}
    
    for alt in alternatives:
        print(f"{alt.name:<30} | ", end="")
        for c in criteria:
            score = alt.scores.get(c, 0)
            print(f"{score:<10}", end="")
        print(f"{result_map[alt.name]:<10.2f}")
    
    print("\n" + "-" * 80)
    print("CRITERIA WEIGHTS:")
    for c, w in criteria.items():
        print(f"  {c}: {w:.0%}")
    
    print("\n" + "=" * 80)
    print("RANKING:")
    print("=" * 80)
    for i, (name, score, desc) in enumerate(results, 1):
        marker = " 👑 WINNER" if i == 1 else ""
        print(f"\n{i}. {name} (Score: {score:.2f}){marker}")
        print(f"   {desc}")
    
    return results[0]  # Return winner


if __name__ == "__main__":
    # Example usage - will be replaced with actual evaluation
    print("Decision Matrix Tool - import and use evaluate() or print_matrix()")

