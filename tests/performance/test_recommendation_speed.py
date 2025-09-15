# test_recommendation_speed_fixed.py
"""
Fixed performance tests for recommendation speed and efficiency.
"""
import time
import numpy as np
import pytest
from moodplay_phi.core import MoodPlayEngine, Item, UserState, ContextSignals

# Test configurations
CATALOG_SIZES = [100, 1000, 5000, 10000]
SLATE_SIZES = [5, 10, 20]
EMBEDDING_DIM = 64

@pytest.fixture(scope="module")
def engine():
    """Create a shared engine instance for all tests."""
    engine = MoodPlayEngine(embedding_dim=EMBEDDING_DIM)
    engine.initialize()
    return engine

@pytest.fixture(scope="module")
def test_user():
    """Create a test user with random state."""
    return UserState(
        g=np.random.randn(EMBEDDING_DIM),
        R=np.ones((12, 12)) / 12,  # 12 facets (3 formats * 4 moods)
        C=0.5,
        N=0.2,
        exposure={},
        last_facet=0,
        z=np.zeros(EMBEDDING_DIM)
    )

@pytest.fixture(scope="module")
def test_context():
    """Create a test context."""
    return ContextSignals(
        hour=14,
        day_of_week=2,
        weather="sunny",
        city="Paris",
        with_friends=False,
        device="mobile"
    )

def generate_catalog(size):
    """Generate a catalog of test items."""
    items = []
    for i in range(size):
        items.append(Item(
            id=f"item_{i}",
            title=f"Test Item {i}",
            type=np.random.choice(["track", "album", "playlist"]),
            genres=np.random.choice(["pop", "rock", "jazz", "classical", "hiphop"], 
                                 size=np.random.randint(1, 4), 
                                 replace=False).tolist(),
            moods=np.random.choice(["happy", "sad", "energetic", "calm"], 
                                size=np.random.randint(1, 3), 
                                replace=False).tolist(),
            duration_min=np.random.uniform(2, 10),
            region_tags=["global"],
            embedding=np.random.randn(EMBEDDING_DIM),
            facet=(np.random.randint(0, 3), np.random.randint(0, 4))  # 3 formats * 4 moods
        ))
    return items

def test_recommendation_speed(engine, test_user, test_context, benchmark):
    """Benchmark recommendation speed with different catalog sizes."""
    catalog_sizes = [100, 1000, 5000, 10000]
    
    for size in catalog_sizes:
        items = generate_catalog(size)
        
        def _recommend():
            return engine.recommend(
                user_state=test_user,
                context=test_context,
                items=items,
                session_minutes=60,
                slate_size=10
            )
            
        # Run benchmark
        result = benchmark.pedantic(
            _recommend,
            rounds=10,
            iterations=1
        )
        
        # Verify results
        slate, _ = result
        assert len(slate) == 10
        assert all(isinstance(item, Item) for item in slate)
        
        # Log results - Fixed attribute access
        stats = benchmark.stats.stats
        print(f"\nCatalog size: {size}")
        print(f"  Mean time: {stats.mean:.4f}s ± {stats.stddev:.4f}s")  # Fixed: stddev not stdev
        print(f"  Min time: {stats.min:.4f}s")
        print(f"  Max time: {stats.max:.4f}s")

def test_slate_size_impact(engine, test_user, test_context, benchmark):
    """Test how slate size affects recommendation time."""
    items = generate_catalog(5000)  # Fixed catalog size
    
    for slate_size in [5, 10, 20]:
        def _recommend():
            return engine.recommend(
                user_state=test_user,
                context=test_context,
                items=items,
                session_minutes=60,
                slate_size=slate_size
            )
            
        # Run benchmark
        result = benchmark.pedantic(
            _recommend,
            rounds=10,
            iterations=1,
            warmup_rounds=2
        )
        
        # Log results - Fixed attribute access
        stats = benchmark.stats.stats
        print(f"\nSlate size: {slate_size}")
        print(f"  Mean time: {stats.mean:.4f}s ± {stats.stddev:.4f}s")  # Fixed: stddev not stdev
