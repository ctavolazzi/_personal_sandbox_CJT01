"""
QuoteCard - AI-Powered Quote Graphics Generator
"""
from .quotecard import (
    generate_card,
    generate_random_card,
    list_themes,
    CONFIG,
    THEMES,
)

__version__ = "1.0.0"
__all__ = ["generate_card", "generate_random_card", "list_themes", "CONFIG", "THEMES"]
