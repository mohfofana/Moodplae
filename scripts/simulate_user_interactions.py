#!/usr/bin/env python3
"""
Script to simulate user interactions with the recommendation system for testing and evaluation.
"""
import os
import json
import random
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from tqdm import tqdm

from moodplay_phi import (
    MoodPlayEngine, 
    UserState, 
    ContextSignals, 
    create_new_user,
    Item
)

def load_items(items_file: str) -> Tuple[Dict[str, Item], List[Item]]:
    """Load items from a JSON file."""
    with open(items_file, 'r') as f:
        items_data = json.load(f)
    
    items = []
    items_by_id = {}
    
    for item_data in items_data:
        item = Item(
            id=item_data['id'],
            title=item_data['title'],
            type=item_data['type'],
            genres=item_data.get('genres', []),
            moods=item_data.get('moods', []),
            duration_min=item_data.get('duration_min', 3.5),
            region_tags=item_data.get('region_tags', ['global']),
            embedding=np.array(item_data.get('embedding', np.random.rand(64))),
            facet=tuple(item_data.get('facet', (0, 0)))
        )
        items.append(item)
        items_by_id[item.id] = item
    
    return items_by_id, items

def simulate_session(
    engine: MoodPlayEngine,
    user: UserState,
    items: List[Item],
    items_by_id: Dict[str, Item],
    context: ContextSignals,
    session_id: int
) -> Dict:
    """Simulate a single user session."""
    # Generate recommendations
    slate, ui_info = engine.recommend(
        user_state=user,
        context=context,
        items=items,
        session_minutes=60,
        slate_size=10
    )
    
    # Simulate user interactions
    watched = []
    for item in slate[:random.randint(1, 4)]:  # User watches 1-4 items
        watch_ratio = min(1.0, random.betavariate(2, 5))  # Most watches are partial
        liked = watch_ratio > 0.7 and random.random() > 0.3  # Higher watch ratio -> more likely to like
        watched.append((item.id, watch_ratio, liked))
    
    # Update user state based on interactions
    if watched:
        engine.update_user_state(user, watched, items_by_id)
    
    # Log session results
    return {
        'session_id': session_id,
        'timestamp': datetime.utcnow().isoformat(),
        'context': {
            'hour': context.hour,
            'day_of_week': context.day_of_week,
            'weather': context.weather,
            'city': context.city,
            'with_friends': context.with_friends,
            'device': context.device
        },
        'slate_size': len(slate),
        'items_recommended': [item.id for item in slate],
        'items_watched': [
            {
                'item_id': item_id,
                'watch_ratio': ratio,
                'liked': liked
            } for item_id, ratio, liked in watched
        ],
        'user_state_after': {
            'comfort': user.C,
            'novelty': user.N,
            'exposure_count': len(user.exposure)
        }
    }

def main():
    parser = argparse.ArgumentParser(description='Simulate user interactions with the recommendation system')
    parser.add_argument('--items-file', type=str, required=True,
                       help='Path to JSON file containing items')
    parser.add_argument('--output-dir', type=str, default='data/simulations',
                       help='Output directory for simulation results')
    parser.add_argument('--num-users', type=int, default=100,
                       help='Number of users to simulate')
    parser.add_argument('--sessions-per-user', type=int, default=10,
                       help='Number of sessions per user')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load items
    print(f"Loading items from {args.items_file}...")
    items_by_id, items = load_items(args.items_file)
    print(f"Loaded {len(items)} items")
    
    # Initialize engine
    engine = MoodPlayEngine(embedding_dim=64)
    engine.initialize()
    
    # Simulate users
    results = []
    
    for user_id in tqdm(range(args.num_users), desc="Simulating users"):
        # Create a new user
        user = create_new_user()
        
        # Simulate sessions
        for session_num in range(args.sessions_per_user):
            # Vary context slightly between sessions
            hour = (12 + session_num * 2) % 24  # Progress through the day
            weather = random.choice(["sunny", "cloudy", "rainy"])
            device = random.choice(["mobile", "desktop", "smart_speaker"])
            
            context = ContextSignals(
                hour=hour,
                day_of_week=session_num % 7,
                weather=weather,
                city="TestCity",
                with_friends=random.random() > 0.7,
                device=device
            )
            
            # Run session
            session_result = simulate_session(
                engine=engine,
                user=user,
                items=items,
                items_by_id=items_by_id,
                context=context,
                session_id=f"user_{user_id}_session_{session_num}"
            )
            session_result['user_id'] = f"user_{user_id}"
            results.append(session_result)
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(args.output_dir, f'simulation_{timestamp}.json')
    
    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'num_users': args.num_users,
            'sessions_per_user': args.sessions_per_user,
            'sessions': results
        }, f, indent=2)
    
    print(f"\nSimulation complete. Results saved to {os.path.abspath(output_file)}")

if __name__ == '__main__':
    main()
