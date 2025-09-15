"""
Unit tests for the core recommendation engine.
"""
import pytest
import numpy as np
from moodplay_phi.core import MoodPlayEngine, Item, ContextSignals
from moodplay_phi.models.user_state import UserState

def test_moodplay_engine_initialization():
    """Test that the engine initializes correctly."""
    engine = MoodPlayEngine(embedding_dim=64)
    assert not engine.initialized
    
    engine.initialize()
    assert engine.initialized

def test_recommendation_with_invalid_state():
    """Test that recommendation fails with uninitialized engine."""
    engine = MoodPlayEngine(embedding_dim=64)
    user = UserState(
        g=np.random.rand(64),
        R=np.ones((12, 12)) / 12,  # 12 facets (3 formats * 4 moods)
        C=0.5,
        N=0.2,
        exposure={},
        last_facet=0,
        z=np.zeros(64)
    )
    context = ContextSignals(
        hour=14,
        day_of_week=2,
        weather="sunny",
        city="Paris",
        with_friends=False,
        device="mobile"
    )
    
    with pytest.raises(RuntimeError):
        engine.recommend(user, context, [])

def test_online_update():
    """Test that user state updates correctly after interaction."""
    engine = MoodPlayEngine(embedding_dim=64)
    engine.initialize()
    
    # Create a test item
    test_item = Item(
        id="test_item_1",
        title="Test Track",
        type="track",
        genres=["pop", "dance"],
        moods=["happy", "energetic"],
        duration_min=3.5,
        region_tags=["global"],
        embedding=np.random.rand(64),
        facet=(0, 0)  # format_bucket=0, mood_bucket=0
    )
    
    # Initial user state
    user = UserState(
        g=np.random.rand(64),
        R=np.ones((12, 12)) / 12,
        C=0.5,
        N=0.2,
        exposure={},
        last_facet=0,
        z=np.zeros(64)
    )
    
    # Simulate watching the item
    watched = [("test_item_1", 0.8, True)]  # (item_id, watch_ratio, liked)
    items_by_id = {"test_item_1": test_item}
    
    # Update user state
    engine.update_user_state(user, watched, items_by_id)
    
    # Verify updates
    assert "test_item_1" in user.exposure
    assert user.exposure["test_item_1"] > 0
    assert user.C > 0.5  # Comfort should increase after a like
    assert len(user.history) == 1
    assert user.history[0]["item_id"] == "test_item_1"
