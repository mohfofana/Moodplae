"""
Context field and state management for MoodPlay Phi.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import numpy as np

class ContextFieldType(Enum):
    """Types of context fields supported."""
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    BOOLEAN = "boolean"
    EMBEDDING = "embedding"

@dataclass
class UserMood:
    mood_label: str  # heureux, triste, énergique, etc.
    confidence: float  # 0.0 à 1.0
    source: str  # 'voice', 'text', 'behavioral_analysis'

@dataclass
class ActivityContext:
    activity_type: str  # travail, sport, détente, etc.
    start_time: datetime
    device: str  # mobile, desktop, tablette
    is_moving: bool = False

@dataclass
class AudioPreferences:
    current_track_bpm: Optional[float] = None
    current_track_energy: Optional[float] = None
    current_track_valence: Optional[float] = None
    recent_genres: List[str] = field(default_factory=list)
    recent_artists: List[str] = field(default_factory=list)

@dataclass
class ContextSignals:
    """
    Conteneur pour tous les signaux contextuels.
    
    Attributes:
        timestamp: Horodatage actuel
        location: Position géographique (lat, lon)
        activity: Activité détectée (marcher, conduire, être assis, etc.)
        mood: Humeur détectée (texte libre)
        spotify_data: Données brutes de l'API Spotify
        recent_tracks: Historique récent des titres écoutés
        top_artists: Artistes les plus écoutés
        top_genres: Genres musicaux préférés
        current_weather: Données météorologiques actuelles
        is_moving: Si l'utilisateur est en déplacement
        transportation_mode: Mode de transport (à pied, voiture, transports en commun)
    """
    # Données temporelles
    timestamp: datetime = field(default_factory=datetime.now)
    day_type: str = 'weekday'  # 'weekday', 'weekend', 'holiday'
    
    # Localisation et activité
    location: Optional[Tuple[float, float]] = None
    activity: Optional[str] = None
    is_moving: bool = False
    transportation_mode: Optional[str] = None
    
    # Humeur et contexte
    mood: Optional[str] = None
    mood_confidence: float = 0.0
    
    # Données Spotify
    spotify_data: Optional[dict] = None
    recent_tracks: List[dict] = field(default_factory=list)
    top_artists: List[dict] = field(default_factory=list)
    top_genres: List[str] = field(default_factory=list)
    
    # Contexte environnemental
    current_weather: Optional[dict] = None
    noise_level: Optional[float] = None  # Niveau de bruit ambiant
    
    # Métadonnées de l'appareil
    device_type: str = 'mobile'  # mobile, desktop, speaker, etc.
    headphones_connected: bool = False
    audio_context: AudioPreferences = field(default_factory=AudioPreferences)
    
    # Données environnementales
    weather: Optional[Dict[str, float]] = None  # temp, condition, humidity
    location: Optional[Dict[str, float]] = None  # lat, long, place_type
    
    # Métadonnées techniques
    device_type: str = 'unknown'  # mobile, desktop, tablet
    connection_type: str = 'unknown'  # wifi, cellular, wired
    
    # Métriques d'engagement
    session_duration: float = 0.0  # en secondes
    skip_rate: float = 0.0  # taux de saut moyen
    
    def update_from_voice_input(self, mood: str, activity: str):
        """Met à jour le contexte à partir d'une entrée vocale"""
        self.user_mood = UserMood(
            mood_label=mood.lower(),
            confidence=0.9,  # haute confiance pour entrée directe
            source='voice'
        )
        
        if activity:
            self.current_activity = ActivityContext(
                activity_type=activity.lower(),
                start_time=datetime.now(),
                device=self.device_type
            )

class ContextManager:
    """Gestionnaire de contexte pour MoodPlae."""
    
    def __init__(self):
        self.current_context = ContextSignals()
        self.context_history = []
    
    def update_from_spotify(self, spotify_data: dict):
        """Met à jour le contexte avec les données de l'API Spotify."""
        if 'currently_playing' in spotify_data:
            track = spotify_data['currently_playing']
            self.current_context.audio_context.current_track_bpm = track.get('tempo')
            self.current_context.audio_context.current_track_energy = track.get('energy')
            self.current_context.audio_context.current_track_valence = track.get('valence')
            
            # Mise à jour des genres/artistes récents
            artists = track.get('artists', [])
            if artists:
                self.current_context.audio_context.recent_artists = [a['name'] for a in artists[:3]]
    
    def update_weather(self, weather_data: dict):
        """Met à jour les données météo."""
        self.current_context.weather = {
            'temp': weather_data.get('temp'),
            'condition': weather_data.get('condition'),
            'humidity': weather_data.get('humidity')
        }
    
    def process_voice_input(self, mood: str, activity: str = None):
        """Traite une entrée vocale utilisateur."""
        self.current_context.update_from_voice_input(mood, activity)
        self._update_day_type()
    
    def _update_day_type(self):
        """Met à jour le type de jour (weekend, semaine, férié)."""
        weekday = self.current_context.timestamp.weekday()
        if weekday >= 5:  # Samedi ou dimanche
            self.current_context.day_type = 'weekend'
        # TODO: Ajouter la détection des jours fériés
    
    def get_context_summary(self) -> dict:
        """Retourne un résumé du contexte actuel."""
        return {
            'mood': self.current_context.user_mood.mood_label if self.current_context.user_mood else 'unknown',
            'activity': self.current_context.current_activity.activity_type if self.current_context.current_activity else 'unknown',
            'time_of_day': self.current_context.timestamp.hour,
            'weather': self.current_context.weather.get('condition') if self.current_context.weather else 'unknown',
            'device': self.current_context.device_type
        }

class ContextField:
    """
    Manages context encoding and state transitions.
    
    This class handles the encoding of raw context signals into a latent
    representation that captures the user's current situation and preferences.
    It uses a simple GRU-like update mechanism to model how the context
    evolves over time.
    """
    
    def __init__(self, d: int):
        """
        Initialize the context field.
        
        Args:
            d: Dimensionality of the context vector
        """
        self.d = d
        self.z0 = np.zeros(d)  # Initial context state
        
    def encode_signals(self, x: ContextSignals) -> np.ndarray:
        """
        Encode raw context signals into a feature vector.
        
        Args:
            x: ContextSignals object containing raw signals
            
        Returns:
            Feature vector representing the context
        """
        v = np.zeros(self.d)
        
        # Time of day encoding (circular)
        hour_rad = 2 * np.pi * x.hour / 24
        v[0] = np.sin(hour_rad)
        v[1] = np.cos(hour_rad)
        
        # Day of week (circular)
        day_rad = 2 * np.pi * x.day_of_week / 7
        v[2] = np.sin(day_rad)
        v[3] = np.cos(day_rad)
        
        # Weather (one-hot like)
        weather_map = {
            'sunny': 0.9,
            'cloudy': 0.5,
            'rainy': 0.1,
            'snowy': 0.0,
            'stormy': -0.5
        }
        v[4] = weather_map.get(x.weather.lower(), 0.0)
        
        # Social context
        v[5] = 1.0 if x.with_friends else 0.0
        
        # Device (one-hot like)
        device_map = {
            'mobile': [0.9, 0.0, 0.0],
            'tv': [0.0, 0.9, 0.0],
            'desktop': [0.0, 0.0, 0.9]
        }
        v[6:9] = device_map.get(x.device.lower(), [0.0, 0.0, 0.0])
        
        # Add more signal encodings as needed
        
        return v
    
    def step(self, z_prev: np.ndarray, x: ContextSignals) -> np.ndarray:
        """
        Update the context state based on previous state and new signals.
        
        Implements a simple GRU-like update:
            z_t = tanh(Wz * z_{t-1} + Wx * x_t + b)
            
        Args:
            z_prev: Previous context state (d-dimensional vector)
            x: New context signals
            
        Returns:
            Updated context state (d-dimensional vector)
        """
        # Initialize weights if not already done
        if not hasattr(self, 'Wz'):
            # Fixed weights for MVP - could be learned parameters in production
            self.Wz = np.eye(self.d) * 0.8  # State transition weights
            self.Wx = np.eye(self.d) * 0.5  # Input weights
            self.b = np.zeros(self.d)        # Bias
        
        # Encode the raw signals
        x_encoded = self.encode_signals(x)
        
        # Apply the GRU-like update
        z_next = np.tanh(
            self.Wz @ z_prev + 
            self.Wx @ x_encoded + 
            self.b
        )
        
        return z_next
    
    def reset(self) -> None:
        """Reset the context state to initial values."""
        self.z = self.z0.copy()
    
    def get_state(self) -> np.ndarray:
        """Get the current context state."""
        if not hasattr(self, 'z'):
            self.reset()
        return self.z
    
    def set_state(self, z: np.ndarray) -> None:
        """
        Set the current context state.
        
        Args:
            z: New context state (must match dimensionality d)
        """
        if z.shape != (self.d,):
            raise ValueError(f"Expected state shape {(self.d,)}, got {z.shape}")
        self.z = z.copy()

# Example usage:
# context = ContextField(d=64)
# signals = ContextSignals(
#     hour=14,  # 2 PM
#     day_of_week=2,  # Wednesday
#     weather="sunny",
#     city="Paris",
#     with_friends=False,
#     device="mobile"
# )
# z_next = context.step(np.zeros(64), signals)
