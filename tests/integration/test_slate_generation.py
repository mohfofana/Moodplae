# test_slate_generation_fixed.py
"""
Fixed integration tests for slate generation.
"""
import pytest
from moodplay_phi.core import MoodPlayEngine
from moodplay_phi.models.user_state import UserState
from moodplay_phi.models.context import ContextSignals
from moodplay_phi.utils.metrics import calculate_diversity_score

def test_slate_diversity(sample_user_state, sample_items):
    """Test that generated slates have good diversity."""
    # Initialize engine
    engine = MoodPlayEngine()
    engine.initialize()
    
    # Create user state
    user_state = UserState(**sample_user_state)
    
    # Get recommendations multiple times
    all_recommendations = []
    for _ in range(5):
        context = ContextSignals(
            hour=14,
            day_of_week=2,
            weather='clear',
            city='Default',
            with_friends=False,
            device='mobile'
        )
        recommendations = engine.recommend(user_state, context, items=sample_items)
        all_recommendations.extend([r['item_id'] for r in recommendations])
    
    # Calculate diversity (should have some variety in recommendations)
    unique_items = len(set(all_recommendations))
    total_items = len(all_recommendations)
    
    # We should have some diversity in recommendations
    if total_items > 0:
        diversity = unique_items / total_items
        assert diversity > 0.5, f"Recommendations lack diversity: {diversity:.2f} uniqueness"

def test_slate_size(sample_user_state):
    """Test that the slate size is reasonable."""
    # Initialize engine
    engine = MoodPlayEngine()
    engine.initialize()
    
    # Create user state
    user_state = UserState(**sample_user_state)
    
    # Create sample items for testing
    sample_items = [
        {'item_id': f'item_{i}', 'genre': 'pop', 'mood': 'happy'} 
        for i in range(20)
    ]
    
    # Get recommendations
    context = ContextSignals(
        hour=14,
        day_of_week=2,
        weather='clear',
        city='Default',
        with_friends=False,
        device='mobile'
    )
    recommendations = engine.recommend(user_state, context, items=sample_items)
    
    # Slate size should be reasonable (e.g., between 5 and 20 items)
    assert 5 <= len(recommendations) <= 20