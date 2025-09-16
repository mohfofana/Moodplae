"""
Exemples de données pour les tests et les démonstrations.
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta

# Exemples d'humeurs avec intensité
SAMPLE_MOODS = [
    {"mood_type": "HAPPY", "intensity": 0.9, "source": "user_input"},
    {"mood_type": "SAD", "intensity": 0.7, "source": "user_input"},
    {"mood_type": "ENERGETIC", "intensity": 0.8, "source": "user_input"},
    {"mood_type": "CALM", "intensity": 0.6, "source": "user_input"},
    {"mood_type": "FOCUSED", "intensity": 0.85, "source": "user_input"}
]

# Exemples d'activités
SAMPLE_ACTIVITIES = [
    {"activity_type": "WORKING", "device": "desktop", "is_moving": False},
    {"activity_type": "EXERCISING", "device": "mobile", "is_moving": True},
    {"activity_type": "COMMUTING", "device": "mobile", "is_moving": True},
    {"activity_type": "SOCIALIZING", "device": "mobile", "is_moving": False},
    {"activity_type": "RELAXING", "device": "desktop", "is_moving": False}
]

# Exemples de pistes musicales avec caractéristiques audio
SAMPLE_TRACKS = [
    {
        "id": "track_1",
        "title": "Happy Vibes",
        "artists": [{"id": "artist_1", "name": "Sunny Beats"}],
        "album": {"id": "album_1", "name": "Summer Hits"},
        "features": {
            "danceability": 0.8,
            "energy": 0.9,
            "valence": 0.95,
            "tempo": 120,
            "loudness": -5.2,
            "mode": 1,
            "key": 5,
            "speechiness": 0.05,
            "acousticness": 0.3,
            "instrumentalness": 0.1,
            "liveness": 0.2,
            "duration_ms": 210000
        }
    },
    # Ajoutez d'autres pistes de démonstration ici
]

def get_sample_tracks(count: int = 10) -> List[Dict[str, Any]]:
    """Retourne un nombre spécifié de pistes d'exemple."""
    return SAMPLE_TRACKS[:min(count, len(SAMPLE_TRACKS))]

def get_sample_context() -> Dict[str, Any]:
    """Retourne un contexte utilisateur d'exemple."""
    from ..models.context import UserMood, ActivityContext, UserContext, AudioPreferences
    
    mood = UserMood(
        mood_type="HAPPY",
        intensity=0.8,
        source="user_input",
        timestamp=datetime.utcnow()
    )
    
    activity = ActivityContext(
        activity_type="WORKING",
        start_time=datetime.utcnow() - timedelta(minutes=30),
        device="desktop",
        is_moving=False
    )
    
    return {
        "user_id": "sample_user_123",
        "current_mood": mood,
        "current_activity": activity,
        "audio_prefs": AudioPreferences()
    }
