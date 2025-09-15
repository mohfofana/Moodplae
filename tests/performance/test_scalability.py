"""
Performance tests for system scalability.
"""
import time
import pytest
import random
from datetime import datetime, timedelta

from moodplay_phi.core import MoodPlayEngine
from moodplay_phi.models.user_state import UserState
from moodplay_phi.utils.data_gen import generate_synthetic_users, generate_synthetic_data

# Test parameters
NUM_USERS = [10, 100, 1000]  # Test with different user counts
ITEMS_PER_USER = 50  # Number of recommendations per user

def generate_test_users_and_items(num_users):
    """Generate test users and items."""
    users = generate_synthetic_users(num_users)
    items = generate_synthetic_data(num_users * 10)  # 10x more items than users
    return users, items

@pytest.mark.parametrize("num_users", NUM_USERS)
def test_recommendation_throughput(benchmark, num_users):
    """Test how many recommendations per second the system can handle."""
    # Setup
    engine = MoodPlayEngine()
    engine.initialize()
    
    # Generate test data
    users, items = generate_test_users_and_items(num_users)
    
    # Create user states
    user_states = [
        UserState(
            user_id=user['user_id'],
            preferences={
                'favorite_genres': user.get('preferred_moods', []),
                'explicit_content': user.get('explicit', False)
            }
        )
        for user in users
    ]
    
    # Test function
    def recommend_for_users():
        for user_state in user_states:
            context = {
                'time_of_day': random.choice(['morning', 'afternoon', 'evening', 'night']),
                'day_of_week': random.choice(['weekday', 'weekend'])
            }
            engine.recommend(user_state, context)
    
    # Run benchmark
    benchmark(recommend_for_users)
    
    # Log results
    print(f"\nThroughput for {num_users} users: {benchmark.stats['ops']:.2f} ops/s")

def test_memory_usage(benchmark):
    """Test memory usage with large numbers of users and items."""
    # This test is more about monitoring memory usage than asserting specific values
    num_users = 1000
    num_items = 10000
    
    # Generate test data
    users = generate_synthetic_users(num_users)
    items = generate_synthetic_data(num_items)
    
    # Create engine and user states
    engine = MoodPlayEngine()
    engine.initialize()
    
    user_states = [
        UserState(
            user_id=user['user_id'],
            preferences={
                'favorite_genres': user.get('preferred_moods', []),
                'explicit_content': user.get('explicit', False)
            }
        )
        for user in users[:100]  # Test with first 100 users for memory
    ]
    
    # Test function
    def process_recommendations():
        for user_state in user_states:
            context = {
                'time_of_day': 'afternoon',
                'day_of_week': 'weekday'
            }
            engine.recommend(user_state, context)
    
    # Run benchmark
    benchmark(process_recommendations)
    
    # Memory assertions would typically use pytest-benchmark's memory_usage plugin
    # This is just a placeholder for the actual memory measurement
    print("\nMemory usage test completed. Check memory usage in benchmark results.")
