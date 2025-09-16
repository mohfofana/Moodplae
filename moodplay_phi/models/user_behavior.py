"""
Modèle pour le suivi et l'analyse du comportement d'écoute utilisateur.

Ce module gère la collecte et l'analyse des données d'écoute pour améliorer
les recommandations musicales.
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
import numpy as np
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)

@dataclass
class TrackInteraction:
    """Représente une interaction utilisateur avec une piste."""
    track_id: str
    timestamp: datetime
    duration_played: float  # en secondes
    duration_total: float   # en secondes
    skipped: bool = False
    liked: bool = False
    context: Dict = field(default_factory=dict)  # humeur, activité, etc.

@dataclass
class UserBehavior:
    """Classe pour suivre et analyser le comportement d'écoute d'un utilisateur."""
    user_id: str
    track_interactions: List[TrackInteraction] = field(default_factory=list)
    # Cache pour des accès rapides
    _track_stats: Dict[str, Dict] = field(init=False, default_factory=lambda: defaultdict(dict))
    _recent_tracks: deque = field(init=False, default_factory=lambda: deque(maxlen=50))
    
    def __post_init__(self):
        self._update_caches()
    
    def add_interaction(self, interaction: TrackInteraction):
        """Ajoute une nouvelle interaction à l'historique."""
        self.track_interactions.append(interaction)
        self._recent_tracks.append(interaction.track_id)
        self._update_track_stats(interaction)
        logger.debug(f"Nouvelle interaction enregistrée pour la piste {interaction.track_id}")
    
    def _update_track_stats(self, interaction: TrackInteraction):
        """Met à jour les statistiques pour une piste."""
        track_id = interaction.track_id
        
        if track_id not in self._track_stats:
            self._track_stats[track_id] = {
                'play_count': 0,
                'total_duration': 0,
                'skip_count': 0,
                'like_count': 0,
                'completion_rates': [],
                'last_played': None,
                'contexts': []
            }
        
        stats = self._track_stats[track_id]
        stats['play_count'] += 1
        stats['total_duration'] += interaction.duration_played
        stats['skip_count'] += int(interaction.skipped)
        stats['like_count'] += int(interaction.liked)
        stats['completion_rates'].append(interaction.duration_played / interaction.duration_total)
        stats['last_played'] = interaction.timestamp
        stats['contexts'].append(interaction.context)
    
    def _update_caches(self):
        """Met à jour les caches internes."""
        for interaction in self.track_interactions:
            self._update_track_stats(interaction)
            self._recent_tracks.append(interaction.track_id)
    
    def get_track_affinity(self, track_id: str) -> float:
        """Calcule l'affinité pour une piste spécifique (0-1)."""
        if track_id not in self._track_stats:
            return 0.0
            
        stats = self._track_stats[track_id]
        completion_rate = np.mean(stats['completion_rates'])
        like_score = stats['like_count'] / stats['play_count'] if stats['play_count'] > 0 else 0
        
        # Poids pour chaque facteur
        weights = {
            'completion': 0.5,
            'likes': 0.3,
            'recency': 0.2
        }
        
        # Score de récence (décroît avec le temps)
        if stats['last_played']:
            days_since_played = (datetime.now() - stats['last_played']).days
            recency_score = max(0, 1 - (days_since_played / 30))  # Décroît sur 30 jours
        else:
            recency_score = 0
        
        # Calcul du score total
        score = (
            weights['completion'] * completion_rate +
            weights['likes'] * like_score +
            weights['recency'] * recency_score
        )
        
        return min(1.0, max(0.0, score))
    
    def get_preferred_genres(self, top_n: int = 5) -> List[tuple]:
        """Retourne les genres préférés de l'utilisateur."""
        genre_counter = defaultdict(int)
        
        for interaction in self.track_interactions:
            if 'genres' in interaction.context:
                for genre in interaction.context['genres']:
                    genre_counter[genre] += 1
        
        return sorted(genre_counter.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    def get_optimal_track_length(self) -> float:
        """Calcule la durée optimale des pistes pour cet utilisateur."""
        if not self.track_interactions:
            return 180.0  # Valeur par défaut : 3 minutes
            
        durations = [
            i.duration_played 
            for i in self.track_interactions 
            if not i.skipped
        ]
        
        return np.median(durations) if durations else 180.0
    
    def get_skip_patterns(self) -> Dict:
        """Identifie les motifs de saut (quand l'utilisateur saute des pistes)."""
        skip_contexts = []
        
        for interaction in self.track_interactions:
            if interaction.skipped:
                skip_contexts.append({
                    'track_features': interaction.context.get('audio_features', {}),
                    'time_of_day': interaction.context.get('time_of_day'),
                    'activity': interaction.context.get('activity'),
                    'mood': interaction.context.get('mood')
                })
        
        return {
            'total_skips': len(skip_contexts),
            'skip_contexts': skip_contexts
        }
    
    def get_listening_habits(self, days: int = 30) -> Dict:
        """Analyse les habitudes d'écoute sur une période donnée."""
        recent_interactions = [
            i for i in self.track_interactions
            if i.timestamp > datetime.now() - timedelta(days=days)
        ]
        
        if not recent_interactions:
            return {}
        
        # Temps d'écoute par jour de la semaine (0 = lundi, 6 = dimanche)
        daily_pattern = defaultdict(float)
        # Temps d'écoute par heure de la journée
        hourly_pattern = defaultdict(float)
        # Temps d'écoute par humeur
        mood_pattern = defaultdict(float)
        # Temps d'écoute par activité
        activity_pattern = defaultdict(float)
        
        for interaction in recent_interactions:
            day = interaction.timestamp.weekday()
            hour = interaction.timestamp.hour
            
            daily_pattern[day] += interaction.duration_played
            hourly_pattern[hour] += interaction.duration_played
            
            if 'mood' in interaction.context:
                mood_pattern[interaction.context['mood']] += interaction.duration_played
            if 'activity' in interaction.context:
                activity_pattern[interaction.context['activity']] += interaction.duration_played
        
        return {
            'daily_pattern': dict(sorted(daily_pattern.items())),
            'hourly_pattern': dict(sorted(hourly_pattern.items())),
            'mood_pattern': dict(mood_pattern),
            'activity_pattern': dict(activity_pattern),
            'total_listening_time': sum(i.duration_played for i in recent_interactions)
        }

# Exemple d'utilisation
if __name__ == "__main__":
    # Configuration du logging
    logging.basicConfig(level=logging.INFO)
    
    # Création d'un utilisateur
    user_id = "user_123"
    behavior = UserBehavior(user_id=user_id)
    
    # Ajout d'interactions factices
    from datetime import datetime, timedelta
    now = datetime.now()
    
    interactions = [
        TrackInteraction(
            track_id="track_1",
            timestamp=now - timedelta(days=1),
            duration_played=180,
            duration_total=200,
            skipped=False,
            liked=True,
            context={
                'mood': 'happy',
                'activity': 'working',
                'genres': ['pop', 'electronic'],
                'time_of_day': 'afternoon'
            }
        ),
        TrackInteraction(
            track_id="track_2",
            timestamp=now - timedelta(hours=2),
            duration_played=30,
            duration_total=210,
            skipped=True,
            liked=False,
            context={
                'mood': 'tired',
                'activity': 'commuting',
                'genres': ['rock'],
                'time_of_day': 'evening'
            }
        )
    ]
    
    for interaction in interactions:
        behavior.add_interaction(interaction)
    
    # Analyse
    print(f"Affinité pour track_1: {behavior.get_track_affinity('track_1'):.2f}")
    print(f"Affinité pour track_2: {behavior.get_track_affinity('track_2'):.2f}")
    print(f"Genres préférés: {behavior.get_preferred_genres()}")
    print(f"Durée optimale: {behavior.get_optimal_track_length():.1f} secondes")
    print("\nHabitudes d'écoute (30 derniers jours):")
    habits = behavior.get_listening_habits(30)
    print(f"- Temps total d'écoute: {habits['total_listening_time'] / 60:.1f} minutes")
    print(f"- Modèle journalier: {habits['daily_pattern']}")
    print(f"- Modèle horaire: {habits['hourly_pattern']}")
    print(f"- Par humeur: {habits['mood_pattern']}")
    print(f"- Par activité: {habits['activity_pattern']}")
