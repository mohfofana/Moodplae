"""
MoodPlay Phi - A mood-based recommendation system.

This package provides a recommendation engine that suggests content based on
user mood, context, and preferences using advanced algorithms including
optimal transport for slate selection.
"""

__version__ = '0.2.0'

from .core import (
    MoodPlayEngine,
    Item,
    UserState,
    ContextSignals,
    step_recommend,
    online_update_after_interactions
)

from .models import (
    ContextField,
    create_new_user,
    calculate_resonance,
    calculate_rhythm_compatibility,
    calculate_diversity
)

__all__ = [
    # Core classes
    'MoodPlayEngine',
    'Item',
    'UserState',
    'ContextSignals',
    
    # Core functions
    'step_recommend',
    'online_update_after_interactions',
    
    # Model components
    'ContextField',
    'create_new_user',
    'calculate_resonance',
    'calculate_rhythm_compatibility',
    'calculate_diversity',
]
