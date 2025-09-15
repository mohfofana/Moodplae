"""
Unit tests for basic components.
"""
import numpy as np
import pytest
from datetime import datetime

from moodplay_phi.models.context import ContextField, ContextSignals
from moodplay_phi.models.user_state import UserState, UserStateUpdate, UpdateType

def test_context_field_validation():
    """Test context field validation."""
    # Test context field initialization
    context_field = ContextField(d=64)
    
    # Test encoding of context signals
    signals = ContextSignals(
        hour=14,
        day_of_week=2,  # Wednesday
        weather="sunny",
        city="Paris",
        with_friends=False,
        device="mobile"
    )
    
    # Test encoding works
    encoded = context_field.encode_signals(signals)
    assert encoded.shape == (64,)
    
    # Test state update
    initial_state = np.zeros(64)
    new_state = context_field.step(initial_state, signals)
    assert new_state.shape == (64,)
    assert not np.array_equal(new_state, initial_state)

def test_user_state_update():
    """Test user state updates."""
    # Create initial state with required fields
    user_state = UserState(
        g=np.random.rand(64),  # Random taste vector
        R=np.eye(12)/12,       # Uniform transition matrix
        C=0.5,                 # Comfort account
        N=0.5,                 # Novelty account
        exposure={},           # No exposure yet
        last_facet=0,          # Start with first facet
        z=None                 # No context yet
    )
    
    # Test initial state
    assert user_state.C == 0.5
    assert user_state.N == 0.5
    assert user_state.last_facet == 0
    
    # Create and apply update to preferences
    update = UserStateUpdate(
        update_type=UpdateType.PREFERENCE,
        data={"theme": "dark"}
    )
    
    updated_state = update.apply(user_state)
    
    # Test updated state
    assert updated_state.preferences == {"theme": "dark"}
    assert updated_state.last_updated is not None

def test_user_state_metadata():
    """Test user state metadata handling."""
    # Create initial state
    user_state = UserState(
        g=np.random.rand(64),
        R=np.eye(12)/12,
        C=0.5,
        N=0.5,
        exposure={},
        last_facet=0,
        z=None
    )
    
    # Create and apply preferences update
    update = UserStateUpdate(
        update_type=UpdateType.PREFERENCE,
        data={
            "new_feature_seen": True,
            "last_notification": "2023-01-01T12:00:00"
        }
    )
    
    updated_state = update.apply(user_state)
    
    # Test preferences were updated
    assert updated_state.preferences == {
        "new_feature_seen": True,
        "last_notification": "2023-01-01T12:00:00"
    }
