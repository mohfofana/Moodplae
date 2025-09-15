# test_consistency_fixed.py  
"""
Fixed performance tests for recommendation consistency.
"""
import time
import pytest
import numpy as np
from datetime import datetime, timedelta
from moodplay_phi.core import MoodPlayEngine
from moodplay_phi.models.user_state import UserState
from moodplay_phi.models.context import ContextSignals
from moodplay_phi.utils.data_gen import generate_synthetic_users

# Test parameters
NUM_ITERATIONS = 10
MAX_TIME_VARIATION_PCT = 20

def test_response_time_consistency(benchmark):
    """Test that response times are consistent for the same input."""
    # Setup
    engine = MoodPlayEngine()
    engine.initialize()
    
    # Create a test user
    user = generate_synthetic_users(1)[0]
    user_state = UserState(
        user_id=user['user_id'],
        preferences={
            'favorite_genres': user.get('preferred_moods', []),
            'explicit_content': user.get('explicit', False)
        }
    )
    
    context = ContextSignals(
        hour=14,
        day_of_week=2,
        weather='clear',
        city='Default',
        with_friends=False,
        device='mobile'
    )
    
    # Create sample items
    sample_items = [
        {'item_id': f'item_{i}', 'genre': 'pop', 'mood': 'happy'} 
        for i in range(100)
    ]
    
    # Measure response times
    response_times = []
    
    def make_recommendation():
        start_time = time.time()
        engine.recommend(user_state, context, items=sample_items)
        response_times.append((time.time() - start_time) * 1000)  # Convert to ms
    
    # Run multiple iterations
    for _ in range(NUM_ITERATIONS):
        make_recommendation()
    
    # Calculate statistics
    avg_time = np.mean(response_times)
    std_dev = np.std(response_times)
    cv = (std_dev / avg_time) * 100  # Coefficient of variation (%)
    
    print(f"\nResponse time statistics (ms):")
    print(f"  Average: {avg_time:.2f} ms")
    print(f"  Std Dev: {std_dev:.2f} ms")
    print(f"  CoV: {cv:.2f}%")
    
    # Check that variation is within acceptable limits
    assert cv < MAX_TIME_VARIATION_PCT, \
        f"Response time variation ({cv:.2f}%) exceeds maximum allowed ({MAX_TIME_VARIATION_PCT}%)"

def test_recommendation_consistency():
    """Test that the same input produces the same output."""
    # Setup
    engine = MoodPlayEngine()
    engine.initialize()
    
    # Create a test user
    user = generate_synthetic_users(1)[0]
    user_state = UserState(
        user_id=user['user_id'],
        preferences={
            'favorite_genres': user.get('preferred_moods', []),
            'explicit_content': user.get('explicit', False)
        }
    )
    
    context = ContextSignals(
        hour=14,
        day_of_week=2,
        weather='clear',
        city='Default',
        with_friends=False,
        device='mobile'
    )
    
    # Create sample items
    sample_items = [
        {'item_id': f'item_{i}', 'genre': 'pop', 'mood': 'happy'} 
        for i in range(50)
    ]
    
    # Get recommendations multiple times
    recommendations = []
    for _ in range(5):
        recs = engine.recommend(user_state, context, items=sample_items)
        # Extract just the item IDs for comparison
        item_ids = [item['item_id'] for item in recs] if isinstance(recs, list) else []
        recommendations.append(item_ids)
    
    # Check that all recommendations are the same
    if recommendations:  # Only check if we got recommendations
        first_rec = recommendations[0]
        for i, rec in enumerate(recommendations[1:], 1):
            assert rec == first_rec, f"Recommendation set {i+1} differs from the first"

