"""
Data generation utilities for testing and development.
"""
import random
from typing import List, Dict, Any
from datetime import datetime, timedelta

def generate_synthetic_users(n: int = 100) -> List[Dict[str, Any]]:
    """
    Generate synthetic user data.
    
    Args:
        n: Number of users to generate
        
    Returns:
        List of user dictionaries
    """
    moods = ['happy', 'sad', 'energetic', 'relaxed', 'focused']
    countries = ['US', 'UK', 'CA', 'AU', 'DE', 'FR', 'JP', 'BR', 'IN', 'CN']
    
    users = []
    for i in range(n):
        user = {
            'user_id': f'user_{i:04d}',
            'age': random.randint(18, 80),
            'gender': random.choice(['M', 'F', 'NB', 'other', 'prefer not to say']),
            'country': random.choice(countries),
            'preferred_moods': random.sample(moods, k=random.randint(1, 3)),
            'account_age_days': random.randint(1, 365 * 5),  # Up to 5 years
            'premium': random.random() < 0.2  # 20% chance of premium
        }
        users.append(user)
    
    return users

def generate_synthetic_data(
    n_items: int = 1000,
    n_categories: int = 20,
    n_artists: int = 100
) -> List[Dict[str, Any]]:
    """
    Generate synthetic item data.
    
    Args:
        n_items: Number of items to generate
        n_categories: Number of unique categories
        n_artists: Number of unique artists
        
    Returns:
        List of item dictionaries
    """
    categories = [f'category_{i}' for i in range(n_categories)]
    artists = [f'artist_{i}' for i in range(n_artists)]
    
    items = []
    for i in range(n_items):
        item = {
            'item_id': f'item_{i:06d}',
            'title': f'Track {i}',
            'artist': random.choice(artists),
            'category': random.choice(categories),
            'duration_seconds': random.randint(120, 600),  # 2-10 minutes
            'popularity': random.randint(1, 100),
            'release_date': (datetime.now() - timedelta(days=random.randint(0, 365*10))).strftime('%Y-%m-%d'),
            'explicit': random.random() < 0.2,  # 20% chance of explicit content
            'danceability': random.random(),
            'energy': random.random(),
            'valence': random.random(),
            'tempo': random.uniform(60, 200)
        }
        items.append(item)
    
    return items
