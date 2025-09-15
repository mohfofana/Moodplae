"""
MoodPlay Phi models package.

This package contains the core data models and algorithms for the MoodPlay Phi
recommendation system.
"""

from .context import ContextField, ContextFieldType, ContextSignals
from .user_state import UserState, create_new_user
from .scoring import (
    cosine_similarity,
    calculate_resonance,
    calculate_rhythm_compatibility,
    calculate_diversity,
    calculate_engagement_score,
    update_taste_vector
)

__all__ = [
    # Context
    'ContextField',
    'ContextFieldType',
    'ContextSignals',
    
    # User State
    'UserState',
    'create_new_user',
    
    # Scoring Functions
    'cosine_similarity',
    'calculate_resonance',
    'calculate_rhythm_compatibility',
    'calculate_diversity',
    'calculate_engagement_score',
    'update_taste_vector',
]
