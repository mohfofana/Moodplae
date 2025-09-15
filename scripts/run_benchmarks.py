#!/usr/bin/env python3
"""
Script to run performance benchmarks for the MoodPlay Phi recommendation system.
"""
import time
import json
import argparse
import statistics
from datetime import datetime
from pathlib import Path

import pytest

# Default benchmark parameters
DEFAULT_NUM_USERS = 100
DEFAULT_NUM_ITEMS = 1000
DEFAULT_NUM_ITERATIONS = 10

def run_benchmark(test_name, params=None, output_dir='benchmarks'):
    """Run a single benchmark test and return the results."""
    # Format the test name and parameters
    test_path = f'tests/performance/test_{test_name}.py::test_{test_name}'
    if params:
        param_str = '_'.join(f'{k}-{v}' for k, v in params.items())
        test_path += f'[{param_str}]'
    
    # Run the benchmark
    start_time = time.time()
    exit_code = pytest.main([
        test_path,
        '--benchmark-json', f'{output_dir}/benchmark_{test_name}.json',
        '-v',
        '--benchmark-warmup', 'on',
        '--benchmark-warmup-iterations', '3'
    ])
    duration = time.time() - start_time
    
    # Return results
    return {
        'test_name': test_name,
        'exit_code': exit_code,
        'duration_seconds': duration,
        'parameters': params or {}
    }

def main():
    parser = argparse.ArgumentParser(description='Run MoodPlay Phi benchmarks')
    parser.add_argument('--output-dir', type=str, default='benchmarks',
                       help='Output directory for benchmark results')
    parser.add_argument('--num-users', type=int, default=DEFAULT_NUM_USERS,
                       help='Number of users for scalability tests')
    parser.add_argument('--num-items', type=int, default=DEFAULT_NUM_ITEMS,
                       help='Number of items for performance tests')
    parser.add_argument('--iterations', type=int, default=DEFAULT_NUM_ITERATIONS,
                       help='Number of iterations per test')
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Define benchmarks to run
    benchmarks = [
        ('scalability', {'num_users': args.num_users}),
        ('consistency', {'iterations': args.iterations}),
    ]
    
    # Run benchmarks
    results = []
    for test_name, params in benchmarks:
        print(f"\n{'=' * 80}")
        print(f"Running benchmark: {test_name}")
        print(f"Parameters: {params}")
        print("-" * 80)
        
        result = run_benchmark(test_name, params, str(output_dir))
        results.append(result)
        
        print(f"\nCompleted in {result['duration_seconds']:.2f} seconds")
        print(f"Exit code: {result['exit_code']}")
    
    # Generate summary report
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    report_file = output_dir / f'summary_{timestamp}.json'
    
    with open(report_file, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'parameters': vars(args),
            'results': results
        }, f, indent=2)
    
    print(f"\nBenchmark summary saved to: {report_file}")

if __name__ == '__main__':
    main()
