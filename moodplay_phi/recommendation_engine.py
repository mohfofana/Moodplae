"""
Moteur de recommandation pour MoodPlae.

Ce module gère la génération de recommandations musicales personnalisées
en fonction du contexte utilisateur, de ses préférences et de son historique.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple
import numpy as np
from .models.context import UserContext, AudioPreferences, ActivityType, MoodType

class RecommendationStrategy(Enum):
    """Stratégies de recommandation disponibles."""
    DISCOVERY = "discovery"  # Pour découvrir de nouvelles musiques
    COMFORT = "comfort"      # Pour écouter des musiques familières
    MIXED = "mixed"         # Un mélange de découverte et de confort

@dataclass
class Track:
    """Représente une piste musicale avec ses caractéristiques."""
    id: str
    title: str
    artists: List[str]
    features: Dict[str, float]  # BPM, énergie, valence, etc.
    popularity: float = 0.0
    genre: str = ""

class RecommendationEngine:
    """Moteur de recommandation principal pour MoodPlae."""
    
    def __init__(self, user_context: UserContext):
        """Initialise le moteur avec le contexte utilisateur."""
        self.context = user_context
        self.strategy = self._select_strategy()
    
    def _select_strategy(self) -> RecommendationStrategy:
        """Sélectionne la stratégie de recommandation en fonction du contexte."""
        # Ici, on pourrait implémenter une logique plus sophistiquée
        # basée sur l'historique et les préférences
        return RecommendationStrategy.MIXED
    
    def generate_recommendations(self, candidate_tracks: List[Track], n: int = 10) -> List[Track]:
        """Génère une liste de recommandations.
        
        Args:
            candidate_tracks: Liste des pistes candidates
            n: Nombre de recommandations à générer
            
        Returns:
            Liste des pistes recommandées
        """
        # Calcul des scores pour chaque piste candidate
        scored_tracks = []
        for track in candidate_tracks:
            score = self._calculate_track_score(track)
            scored_tracks.append((track, score))
        
        # Tri par score décroissant
        scored_tracks.sort(key=lambda x: x[1], reverse=True)
        
        # Retourne les n meilleures pistes
        return [track for track, _ in scored_tracks[:n]]
    
    def _calculate_track_score(self, track: Track) -> float:
        """Calcule un score de pertinence pour une piste donnée."""
        score = 0.0
        
        # Score basé sur les caractéristiques audio
        audio_score = self._calculate_audio_score(track.features)
        
        # Score basé sur l'humeur
        mood_score = self._calculate_mood_score(track)
        
        # Score basé sur l'activité
        activity_score = self._calculate_activity_score(track)
        
        # Combinaison pondérée des scores
        score = (
            0.4 * audio_score +
            0.3 * mood_score +
            0.3 * activity_score
        )
        
        return score
    
    def _calculate_audio_score(self, features: Dict[str, float]) -> float:
        """Calcule un score basé sur les caractéristiques audio."""
        score = 0.0
        prefs = self.context.audio_prefs
        
        # Vérification de la plage de BPM
        bpm = features.get('tempo', 100)
        min_bpm, max_bpm = prefs.preferred_bpm_range
        if min_bpm <= bpm <= max_bpm:
            score += 0.3
            
        # Énergie
        energy = features.get('energy', 0.5)
        energy_diff = 1 - abs(energy - prefs.preferred_energy)
        score += 0.3 * energy_diff
        
        # Valence (positivité de la musique)
        valence = features.get('valence', 0.5)
        valence_diff = 1 - abs(valence - prefs.preferred_valence)
        score += 0.2 * valence_diff
        
        # Popularité (peut être pondérée différemment selon la stratégie)
        popularity = features.get('popularity', 50) / 100
        if self.strategy == RecommendationStrategy.COMFORT:
            score += 0.2 * popularity
        
        return min(max(score, 0.0), 1.0)
    
    def _calculate_mood_score(self, track: Track) -> float:
        """Calcule un score basé sur l'humeur de l'utilisateur."""
        # À implémenter : logique de correspondance d'humeur
        return 0.7  # Valeur par défaut
    
    def _calculate_activity_score(self, track: Track) -> float:
        """Calcule un score basé sur l'activité en cours."""
        # À implémenter : logique de correspondance d'activité
        return 0.7  # Valeur par défaut

# Exemple d'utilisation
if __name__ == "__main__":
    # Création d'un contexte utilisateur factice pour les tests
    from .models.context import UserMood, ActivityContext, AudioPreferences, ActivityType, MoodType
    
    # Initialisation du contexte utilisateur
    user_mood = UserMood(mood_type=MoodType.HAPPY, intensity=0.8)
    activity = ActivityContext(
        activity_type=ActivityType.WORKING,
        start_time=datetime.now(),
        device="desktop"
    )
    audio_prefs = AudioPreferences()
    
    context = UserContext(
        user_id="test_user",
        current_mood=user_mood,
        current_activity=activity,
        audio_prefs=audio_prefs
    )
    
    # Création du moteur de recommandation
    engine = RecommendationEngine(context)
    
    # Génération de recommandations (avec des pistes factices)
    test_tracks = [
        Track(
            id=f"track_{i}",
            title=f"Track {i}",
            artists=[f"Artist {i}"],
            features={
                'tempo': 120 + i * 5,
                'energy': 0.7 + i * 0.05,
                'valence': 0.6 + i * 0.02,
                'popularity': 70 + i
            }
        )
        for i in range(10)
    ]
    
    recommendations = engine.generate_recommendations(test_tracks, n=5)
    print("Recommandations :")
    for i, track in enumerate(recommendations, 1):
        print(f"{i}. {track.title} - {', '.join(track.artists)}")
