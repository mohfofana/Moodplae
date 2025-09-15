"""
User state management for MoodPlay Phi.
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set
import numpy as np

# ------------------------
# Update management
# ------------------------
class UpdateType(Enum):
    PREFERENCE = "preference"
    HISTORY = "history"
    MOOD = "mood"
    METADATA = "metadata"


@dataclass
class UserStateUpdate:
    """Represents an update to the user's state."""
    update_type: UpdateType
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def apply(self, user_state: 'UserState') -> 'UserState':
        """Apply this update to a user state."""
        if self.update_type == UpdateType.PREFERENCE:
            user_state.preferences.update(self.data)
        elif self.update_type == UpdateType.HISTORY:
            user_state.history.append(self.data)
        elif self.update_type == UpdateType.MOOD:
            user_state.mood = self.data.get('mood', user_state.mood)
        elif self.update_type == UpdateType.METADATA:
            user_state.metadata.update(self.data)
        user_state.last_updated = self.timestamp
        return user_state


# ------------------------
# Core user state
# ------------------------
@dataclass
class UserState:
    """
    Tracks the current state of a user in the recommendation system.
    """
    # User identification and metadata
    user_id: str = ""
    mood: str = "neutral"
    preferences: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_updated: Optional[datetime] = field(default_factory=datetime.utcnow)

    # Core recommendation state
    g: np.ndarray = field(default_factory=lambda: np.array([]))  # Taste vector in R^d
    R: np.ndarray = field(default_factory=lambda: np.array([]))  # KxK rhythm transition matrix
    C: float = 0.5              # Comfort account (0 to 1)
    N: float = 0.5              # Novelty debt (0 to 1)
    exposure: Dict[str, float] = field(default_factory=dict)  # item_id -> exposure weight
    last_facet: int = 0         # Last consumed facet index
    last_facet_consumed: Optional[int] = None  # Explicitly declared
    z: Optional[np.ndarray] = None  # Current context latent vector

    # History tracking
    history: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        """Initialize the user state with default values if needed."""
        if self.z is None and self.g.size > 0:
            self.z = np.zeros_like(self.g)

    def update_after_interaction(self, item_id: str, item_embedding: np.ndarray,
                                 facet_idx: int, watch_ratio: float, liked: bool,
                                 timestamp: Optional[datetime] = None) -> None:
        """
        Update user state after an interaction with an item.
        """
        if timestamp is None:
            timestamp = datetime.utcnow()

        # Update exposure (keep max between previous and new watch_ratio)
        self.exposure[item_id] = max(self.exposure.get(item_id, 0.0), watch_ratio)

        # Update last facet
        self.last_facet = facet_idx

        # Update rhythm transition matrix (count-based with normalization)
        if self.last_facet_consumed is not None and self.R.size > 0:
            i, j = self.last_facet_consumed, facet_idx
            self.R[i, j] += 1.0
            row_sum = self.R[i].sum()
            if row_sum > 0:
                self.R[i] /= row_sum

        # Update comfort/novelty accounts
        if liked:
            self.C = min(1.0, self.C + 0.1)
        elif watch_ratio > 0.8:
            self.N = min(1.0, self.N + 0.1)

        # Update taste vector (g) -- stronger update on explicit likes
        if item_embedding is not None and item_embedding.size > 0:
            # make learning more responsive on likes to be visible in small tests
            if liked or watch_ratio > 0.7:
                alpha = 0.20 if liked else 0.05 * watch_ratio  # <-- increased when liked
                # simple gradient-like update toward item_embedding
                self.g = self.g + alpha * (item_embedding - self.g)
                norm = np.linalg.norm(self.g)
                if norm > 1e-8:
                    self.g /= norm

        # Update history
        self.history.append({
            'item_id': item_id,
            'facet': facet_idx,
            'watch_ratio': watch_ratio,
            'liked': liked,
            'timestamp': timestamp,
            'state': {
                'C': self.C,
                'N': self.N,
                'g_norm': np.linalg.norm(self.g),
                'last_facet': self.last_facet
            }
        })

        # Keep history manageable
        if len(self.history) > 1000:
            self.history = self.history[-1000:]

        self.last_updated = timestamp
        self.last_facet_consumed = facet_idx


    def decay_accounts(self, lamC: float = 0.97, lamN: float = 0.97) -> None:
        """Apply decay to comfort and novelty accounts."""
        self.C = max(0.0, self.C * lamC)
        self.N = max(0.0, self.N * lamN)

    def decay_exposure(self, gamma: float = 0.9) -> None:
        """Apply decay to exposure counts."""
        for k in list(self.exposure.keys()):
            self.exposure[k] *= gamma
            if self.exposure[k] <= 0.01:
                del self.exposure[k]

    def get_recent_items(self, lookback_days: int = 7) -> Set[str]:
        """Get set of recently consumed item IDs."""
        cutoff = datetime.utcnow() - timedelta(days=lookback_days)
        return {h['item_id'] for h in self.history if h['timestamp'] >= cutoff}

    def to_dict(self) -> Dict[str, Any]:
        """Convert user state to a dictionary for serialization."""
        return {
            'user_id': self.user_id,
            'mood': self.mood,
            'preferences': self.preferences,
            'metadata': self.metadata,
            'g': self.g.tolist(),
            'R': self.R.tolist(),
            'C': self.C,
            'N': self.N,
            'exposure': self.exposure,
            'last_facet': self.last_facet,
            'last_facet_consumed': self.last_facet_consumed,
            'z': self.z.tolist() if self.z is not None else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'history': self.history
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserState':
        """Create a UserState from a dictionary."""
        return cls(
            user_id=data.get('user_id', ""),
            mood=data.get('mood', "neutral"),
            preferences=data.get('preferences', {}),
            metadata=data.get('metadata', {}),
            g=np.array(data.get('g', [])),
            R=np.array(data.get('R', [])),
            C=data.get('C', 0.5),
            N=data.get('N', 0.5),
            exposure=data.get('exposure', {}),
            last_facet=data.get('last_facet', 0),
            last_facet_consumed=data.get('last_facet_consumed', None),
            z=np.array(data['z']) if data.get('z') is not None else None,
            history=data.get('history', []),
            last_updated=datetime.fromisoformat(data['last_updated']) if data.get('last_updated') else None
        )

    def clone(self) -> 'UserState':
        """Create a deep copy of the user state."""
        return UserState.from_dict(self.to_dict())

    def __repr__(self) -> str:
        return (f"<UserState id={self.user_id} mood={self.mood} "
                f"C={self.C:.2f} N={self.N:.2f} "
                f"history={len(self.history)} items>")


# ------------------------
# Helper
# ------------------------
def create_new_user(embedding_dim: int, num_facets: int) -> UserState:
    """Create a new user with default state."""
    g = np.random.randn(embedding_dim)
    g = g / (np.linalg.norm(g) + 1e-8)
    R = np.ones((num_facets, num_facets)) / num_facets
    return UserState(
        g=g,
        R=R,
        C=1.0,
        N=0.0,
        exposure={},
        last_facet=0,
        last_facet_consumed=None,
        z=np.zeros(embedding_dim)
    )
