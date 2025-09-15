"""
Pytest configuration and fixtures.
"""

import pytest
from datetime import datetime, timedelta
import random

@pytest.fixture
def sample_user_state():
    """Create a sample user state for testing."""
    return {
        'user_id': 'test_user_001',
        'mood': 'happy',
        'preferences': {
            'favorite_genres': ['pop', 'rock'],
            'preferred_tempo': 'medium',
            'explicit_content': False
        },
        'history': [
            {'item_id': 'track_001', 'timestamp': '2023-01-01T12:00:00', 'liked': True},
            {'item_id': 'track_042', 'timestamp': '2023-01-01T12:30:00', 'liked': False}
        ],
        'last_updated': '2023-01-02T10:00:00',
        'metadata': {
            'account_age_days': 100,
            'subscription_type': 'premium'
        }
    }

@pytest.fixture
def sample_context():
    """Create a sample context for testing."""
    return {
        'time_of_day': 'afternoon',
        'day_of_week': 'weekday',
        'device': 'mobile',
        'location': 'home',
        'social_context': 'alone',
        'timestamp': datetime.utcnow().isoformat()
    }

@pytest.fixture
def sample_items():
    """Generate sample items for testing."""
    genres = ['pop', 'rock', 'jazz', 'classical', 'hiphop', 'electronic']
    moods = ['happy', 'sad', 'energetic', 'relaxed', 'focused']
    
    items = []
    for i in range(100):
        item = {
            'item_id': f'track_{i:03d}',
            'title': f'Sample Track {i}',
            'artist': f'Artist {i % 10}',
            'album': f'Album {i // 5}',
            'duration_seconds': random.randint(180, 300),
            'genre': random.choice(genres),
            'mood': random.choice(moods),
            'popularity': random.randint(1, 100),
            'explicit': random.random() < 0.2,
            'danceability': random.random(),
            'energy': random.random(),
            'valence': random.random(),
            'tempo': random.uniform(60, 200),
            'release_date': (
                datetime.now() - 
                timedelta(days=random.randint(0, 365*5))
            ).strftime('%Y-%m-%d')
        }
        items.append(item)
    
    return items
