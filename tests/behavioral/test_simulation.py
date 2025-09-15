# test_simulation_fixed.py
"""
Fixed behavioral tests using simulated users to validate system behavior.
"""
import pytest
import random
import numpy as np
from datetime import datetime
from typing import List, Dict, Any
from moodplay_phi import Item, MoodPlayEngine
from moodplay_phi.models.user_state import UserState, UserStateUpdate
from moodplay_phi.models.context import ContextSignals
from moodplay_phi.utils.data_gen import generate_synthetic_users, generate_synthetic_data

class SimulatedUser:
    """A simulated user for testing the recommendation system."""
    
    def __init__(self, user_id: str, preferences: Dict[str, Any]):
        self.user_id = user_id
        
        embedding_dim = 64  # Match the engine's default embedding dimension
        num_facets = 12    # 3 format buckets * 4 mood buckets
        
        g = np.random.randn(embedding_dim)
        g = g / (np.linalg.norm(g) + 1e-8)
        
        R = np.ones((num_facets, num_facets)) / num_facets
        z = np.zeros(embedding_dim)
        
        self.state = UserState(
            user_id=user_id,
            preferences=preferences,
            g=g,
            R=R,
            C=1.0,
            N=0.0,
            exposure={},
            last_facet=0,
            last_facet_consumed=0,
            z=z,
            metadata={
                'created_at': datetime.utcnow(),
                'sessions': 0,
                'total_plays': 0
            }
        )
        self.history: List[Dict[str, Any]] = []
    
    def interact(self, item, action: str = 'play', duration: int = None):
        """Simulate a user interaction with an item."""
        if duration is None:
            duration = random.randint(30, 300)
            
        item_id = item.id if hasattr(item, 'id') else item.get('item_id')
        
        interaction = {
            'item_id': item_id,
            'action': action,
            'timestamp': datetime.utcnow().isoformat(),
            'duration_seconds': duration,
            'completed': action != 'skip'
        }
        
        self.history.append(interaction)
        self.state.metadata['total_plays'] += 1
        
        update_data = {
            'history': [interaction],
            'last_played': interaction['timestamp']
        }
        
        if action == 'like':
            if 'liked_items' not in self.state.metadata:
                self.state.metadata['liked_items'] = []
            self.state.metadata['liked_items'].append(item_id)
        
        update = UserStateUpdate(updates=update_data)
        update.apply(self.state)
        
        return interaction

def test_simulated_user_behavior():
    """Test the system with simulated user behavior."""
    engine = MoodPlayEngine()
    engine.initialize()
    
    users = generate_synthetic_users(5)
    items = generate_synthetic_data(100)
    
    simple_items = []
    for item in items:
        item_obj = Item(
            id=item['item_id'],
            title=item.get('title', 'Test Item'),
            type=item.get('type', 'clip'),
            genres=[item.get('genre', 'pop')],
            moods=[item.get('mood', 'happy')],
            duration_min=item.get('duration_min', 5.0),
            region_tags=item.get('region_tags', ['global']),
            embedding=item.get('embedding', np.random.randn(64)),
            facet=item.get('facet', (0, 0))
        )
        simple_items.append(item_obj)
    
    simulated_users = [
        SimulatedUser(
            user_id=user['user_id'],
            preferences={
                'favorite_genres': user.get('preferred_moods', []),
                'explicit_content': user.get('explicit', False)
            }
        )
        for user in users
    ]
    
    for day in range(7):
        for user in simulated_users:
            if random.random() < 0.7:
                user.state.metadata['sessions'] += 1
                
                context = ContextSignals(
                    hour=random.randint(6, 23),
                    day_of_week=day % 7,
                    weather=random.choice(['sunny', 'cloudy', 'rainy']),
                    city='Default',
                    with_friends=random.choice([True, False]),
                    device=random.choice(['mobile', 'desktop'])
                )
                
                # Corrected: extract slate from recommend()
                slate, ui = engine.recommend(user.state, context, items=simple_items)
                recommendations = slate
                
                if recommendations:
                    num_interactions = random.randint(1, min(3, len(recommendations)))
                    items_to_interact = recommendations[:num_interactions]
                    
                    for item in items_to_interact:
                        action = random.choices(
                            ['play', 'skip', 'like'],
                            weights=[0.7, 0.2, 0.1]
                        )[0]
                        user.interact(item, action=action)
    
    for user in simulated_users:
        assert len(user.history) > 0, f"User {user.user_id} has no interaction history"
        assert user.state.metadata['sessions'] > 0, f"User {user.user_id} had no active sessions"
        assert 'last_played' in user.state.metadata, f"User {user.user_id} has no last_played timestamp"
        assert user.state.metadata['total_plays'] > 0, f"User {user.user_id} has no plays recorded"
        
        likes = len([h for h in user.history if h.get('action') == 'like'])
        skips = len([h for h in user.history if h.get('action') == 'skip'])
        plays = len([h for h in user.history if h.get('action') == 'play'])
        
        print(f"\nUser {user.user_id}: Sessions={user.state.metadata['sessions']}, Total={len(user.history)}, Plays={plays}, Likes={likes}, Skips={skips}")
