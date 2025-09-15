#!/usr/bin/env python3
"""
Script to generate test data for the MoodPlay Phi recommendation system.
"""
import os
import json
import argparse
from datetime import datetime

from moodplay_phi.utils.data_gen import generate_synthetic_users, generate_synthetic_data

def main():
    parser = argparse.ArgumentParser(description='Generate test data for MoodPlay Phi')
    parser.add_argument('--output-dir', type=str, default='data/synthetic',
                       help='Output directory for generated data')
    parser.add_argument('--num-users', type=int, default=1000,
                       help='Number of synthetic users to generate')
    parser.add_argument('--num-items', type=int, default=10000,
                       help='Number of synthetic items to generate')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Generate data
    print(f"Generating {args.num_users} synthetic users...")
    users = generate_synthetic_users(args.num_users)
    
    print(f"Generating {args.num_items} synthetic items...")
    items = generate_synthetic_data(args.num_items)
    
    # Save data
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    users_file = os.path.join(args.output_dir, f'users_{timestamp}.json')
    with open(users_file, 'w') as f:
        json.dump(users, f, indent=2)
    
    items_file = os.path.join(args.output_dir, f'items_{timestamp}.json')
    with open(items_file, 'w') as f:
        json.dump(items, f, indent=2)
    
    print(f"\nGenerated data saved to:")
    print(f"- Users: {os.path.abspath(users_file)}")
    print(f"- Items: {os.path.abspath(items_file)}")

if __name__ == '__main__':
    main()
