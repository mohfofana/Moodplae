"""
Unit tests for user state updates.
"""
import pytest
from datetime import datetime, timedelta

from moodplay_phi.models.user_state import UserState, UserStateUpdate, UpdateType

def test_user_state_initialization():
    user_state = UserState(user_id="test_user")
    assert user_state.user_id == "test_user"
    assert user_state.mood == "neutral"
    assert user_state.preferences == {}
    assert user_state.history == []
    assert isinstance(user_state.last_updated, datetime)
    assert user_state.metadata == {}

def test_user_state_update_application():
    old_time = datetime.utcnow() - timedelta(days=1)
    user_state = UserState(
        user_id="test_user",
        mood="sad",
        preferences={"theme": "light"},
        last_updated=old_time
    )

    # Update mood
    update_mood = UserStateUpdate(
        update_type=UpdateType.MOOD,
        data={"mood": "happy"}
    )
    update_mood.apply(user_state)

    # Update preferences
    update_pref = UserStateUpdate(
        update_type=UpdateType.PREFERENCE,
        data={"theme": "dark"}
    )
    update_pref.apply(user_state)

    # Update metadata
    update_meta = UserStateUpdate(
        update_type=UpdateType.METADATA,
        data={"new_field": "value"}
    )
    update_meta.apply(user_state)

    assert user_state.mood == "happy"
    assert user_state.preferences == {"theme": "dark"}
    assert user_state.metadata == {"new_field": "value"}
    assert user_state.last_updated > old_time

def test_user_state_update_with_history():
    user_state = UserState(user_id="test_user")

    history_entry = {
        "item_id": "track_001",
        "timestamp": datetime.utcnow().isoformat(),
        "action": "play",
        "duration_seconds": 180
    }

    update_history = UserStateUpdate(
        update_type=UpdateType.HISTORY,
        data=history_entry
    )
    update_history.apply(user_state)

    update_mood = UserStateUpdate(
        update_type=UpdateType.MOOD,
        data={"mood": "happy"}
    )
    update_mood.apply(user_state)

    assert len(user_state.history) == 1
    assert user_state.history[0]["item_id"] == "track_001"
    assert user_state.mood == "happy"
