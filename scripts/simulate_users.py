#!/usr/bin/env python3
"""
Script to simulate user interactions with the MoodPlay Phi recommendation system.
"""
import os
import json
import time
import random
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Any

from tqdm import tqdm

from moodplay_phi.core import MoodPlayEngine
from moodplay_phi.models.user_state import UserState, UserStateUpdate
from moodplay_phi.utils.data_gen import generate_synthetic_users, generate_synthetic_data

class UserSimulator:
    """Simulates user interactions with the recommendation system."""
    
    def __init__(self, engine: MoodPlayEngine, num_users: int = 100, num_items: int = 1000):
        self.engine = engine
        self.users = []
        self.items = []
        self.num_users = num_users
        self.num_items = num_items
        self.interaction_log = []
        
    def initialize(self):
        """Initialize the simulator with test data."""
        print("Generating test data...")
        self.users = generate_synthetic_users(self.num_users)
        self.items = generate_synthetic_data(self.num_items)
        
        # Create a mapping of item IDs to items for quick lookup
        self.item_lookup = {item['item_id']: item for item in self.items}
    
    def create_user_state(self, user_data: Dict[str, Any]) -> UserState:
        """Create a UserState object from user data."""
        return UserState(
            user_id=user_data['user_id'],
            preferences={
                'favorite_genres': user_data.get('preferred_moods', []),
                'explicit_content': user_data.get('explicit', False)
            },
            metadata={
                'created_at': datetime.utcnow().isoformat(),
                'simulation_data': True
            }
        )
    
    def simulate_session(self, user_state: UserState) -> List[Dict[str, Any]]:
        """Simulate a single user session."""
        # Randomly select a time of day and day type
        time_of_day = random.choice(['morning', 'afternoon', 'evening', 'night'])
        day_type = random.choice(['weekday', 'weekend'])
        
        context = {
            'time_of_day': time_of_day,
            'day_of_week': day_type,
            'device': random.choice(['mobile', 'desktop', 'smart_speaker']),
            'location': random.choice(['home', 'work', 'commute', 'gym']),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Get recommendations
        recommendations = self.engine.recommend(user_state, context)
        
        # Simulate interactions with recommendations
        session_interactions = []
        
        # User interacts with 1-5 items per session
        num_interactions = random.randint(1, min(5, len(recommendations)))
        
        for item in recommendations[:num_interactions]:
            # 70% play, 20% skip, 10% like
            action = random.choices(
                ['play', 'skip', 'like'],
                weights=[0.7, 0.2, 0.1]
            )[0]
            
            # Generate interaction data
            interaction = {
                'user_id': user_state.user_id,
                'item_id': item['item_id'],
                'action': action,
                'timestamp': datetime.utcnow().isoformat(),
                'context': context.copy()
            }
            
            # Add duration for play actions
            if action == 'play':
                interaction['duration_seconds'] = random.randint(30, 300)  # 30s to 5 minutes
            
            session_interactions.append(interaction)
            
            # Update user state based on interaction
            self.update_user_state(user_state, interaction)
            
            # Small delay between interactions
            time.sleep(0.1)
        
        return session_interactions
    
    def update_user_state(self, user_state: UserState, interaction: Dict[str, Any]):
        """Update user state based on interaction."""
        update_data = {
            'history': [{
                'item_id': interaction['item_id'],
                'action': interaction['action'],
                'timestamp': interaction['timestamp']
            }],
            'last_played': interaction['timestamp']
        }
        
        if interaction['action'] == 'like':
            if 'liked_items' not in user_state.metadata:
                user_state.metadata['liked_items'] = []
            user_state.metadata['liked_items'].append(interaction['item_id'])
        
        update = UserStateUpdate(
            user_id=user_state.user_id,
            updates=update_data
        )
        update.apply(user_state)
    
    def run_simulation(self, num_sessions: int = 1000, output_dir: str = 'simulation_results'):
        """Run the simulation with multiple users and sessions."""
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize user states
        user_states = {}
        for user in self.users:
            user_states[user['user_id']] = self.create_user_state(user)
        
        # Run simulation
        print(f"Simulating {num_sessions} sessions across {len(user_states)} users...")
        
        session_logs = []
        
        with tqdm(total=num_sessions) as pbar:
            for _ in range(num_sessions):
                # Select a random user
                user_id = random.choice(list(user_states.keys()))
                user_state = user_states[user_id]
                
                # Simulate a session
                session = self.simulate_session(user_state)
                session_logs.extend(session)
                
                pbar.update(1)
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(output_dir, f'simulation_{timestamp}.json')
        
        with open(output_file, 'w') as f:
            json.dump(session_logs, f, indent=2)
        
        print(f"\nSimulation complete. Results saved to: {os.path.abspath(output_file)}")
        
        # Generate summary statistics
        actions = [log['action'] for log in session_logs]
        action_counts = {action: actions.count(action) for action in set(actions)}
        
        print("\nSimulation Summary:")
        print(f"Total interactions: {len(session_logs)}")
        for action, count in action_counts.items():
            print(f"- {action.capitalize()}: {count} ({count/len(session_logs):.1%})")

def main():
    parser = argparse.ArgumentParser(description='Simulate user interactions with MoodPlay Phi')
    parser.add_argument('--num-users', type=int, default=100,
                       help='Number of users to simulate')
    parser.add_argument('--num-items', type=int, default=1000,
                       help='Number of items in the catalog')
    parser.add_argument('--num-sessions', type=int, default=1000,
                       help='Number of user sessions to simulate')
    parser.add_argument('--output-dir', type=str, default='simulation_results',
                       help='Output directory for simulation results')
    
    args = parser.parse_args()
    
    # Initialize the recommendation engine
    print("Initializing MoodPlay Phi engine...")
    engine = MoodPlayEngine()
    engine.initialize()
    
    # Create and run the simulator
    simulator = UserSimulator(
        engine=engine,
        num_users=args.num_users,
        num_items=args.num_items
    )
    
    simulator.initialize()
    simulator.run_simulation(
        num_sessions=args.num_sessions,
        output_dir=args.output_dir
    )

if __name__ == '__main__':
    main()
