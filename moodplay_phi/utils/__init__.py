"""
Utility functions for the MoodPlay Phi recommendation system.
"""

from .data_gen import generate_synthetic_data, generate_synthetic_users
from .metrics import (
    calculate_precision,
    calculate_recall,
    calculate_ndcg,
    calculate_serendipity
)

__all__ = [
    'generate_synthetic_data',
    'generate_synthetic_users',
    'calculate_precision',
    'calculate_recall',
    'calculate_ndcg',
    'calculate_serendipity'
]
