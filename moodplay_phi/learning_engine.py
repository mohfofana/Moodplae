"""
Moteur d'apprentissage pour MoodPlae.

Ce module gère l'apprentissage des préférences utilisateur à partir
de leurs interactions avec la plateforme.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np
from .models.context import UserContext, AudioPreferences, UserMood, ActivityContext

class LearningEngine:
    """Moteur d'apprentissage des préférences utilisateur."""
    
    def __init__(self, decay_rate: float = 0.95):
        """Initialise le moteur d'apprentissage.
        
        Args:
            decay_rate: Taux de dégradation des préférences (0.0-1.0)
        """
        self.decay_rate = decay_rate
    
    def update_from_interaction(self, 
                             context: UserContext,
                             track_id: str,
                             track_features: Dict[str, float],
                             interaction_type: str,
                             interaction_time: Optional[datetime] = None) -> None:
        """Met à jour les préférences utilisateur à partir d'une interaction.
        
        Args:
            context: Contexte utilisateur à mettre à jour
            track_id: ID de la piste concernée
            track_features: Caractéristiques de la piste
            interaction_type: Type d'interaction ('play', 'skip', 'like', 'dislike')
            interaction_time: Horodatage de l'interaction (par défaut: maintenant)
        """
        if interaction_time is None:
            interaction_time = datetime.utcnow()
        
        # Appliquer la dégradation temporelle
        self._apply_time_decay(context, interaction_time)
        
        # Mettre à jour en fonction du type d'interaction
        if interaction_type == 'like':
            self._process_like(context, track_features)
        elif interaction_type == 'dislike':
            self._process_dislike(context, track_features)
        elif interaction_type == 'skip':
            self._process_skip(context, track_features)
        elif interaction_type == 'play':
            self._process_play(context, track_features)
    
    def _apply_time_decay(self, context: UserContext, current_time: datetime) -> None:
        """Applique une dégradation temporelle aux préférences."""
        # Temps écoulé depuis la dernière mise à jour (en heures)
        time_diff = (current_time - context.last_updated).total_seconds() / 3600
        decay = self.decay_rate ** time_diff
        
        # Dégradation des préférences audio
        prefs = context.audio_prefs
        for key in prefs.liked_genres:
            prefs.liked_genres[key] *= decay
        for key in prefs.liked_artists:
            prefs.liked_artists[key] *= decay
        
        # Mise à jour de l'horodatage
        context.last_updated = current_time
    
    def _process_like(self, context: UserContext, features: Dict[str, float]) -> None:
        """Traitement d'un like sur une piste."""
        prefs = context.audio_prefs
        
        # Mise à jour des préférences de genre
        genre = features.get('genre')
        if genre:
            prefs.liked_genres[genre] = prefs.liked_genres.get(genre, 0) + 1.0
        
        # Mise à jour des préférences d'artiste
        artist_id = features.get('artist_id')
        if artist_id:
            prefs.liked_artists[artist_id] = prefs.liked_artists.get(artist_id, 0) + 1.0
        
        # Ajustement des préférences audio
        self._update_audio_preferences(prefs, features, positive=True)
    
    def _process_dislike(self, context: UserContext, features: Dict[str, float]) -> None:
        """Traitement d'un dislike sur une piste."""
        # Réduire le score des caractéristiques non appréciées
        self._update_audio_preferences(context.audio_prefs, features, positive=False)
    
    def _process_skip(self, context: UserContext, features: Dict[str, float]) -> None:
        """Traitement d'un skip sur une piste."""
        # Moins pénalisant qu'un dislike, mais tout de même pris en compte
        self._update_audio_preferences(
            context.audio_prefs, 
            features, 
            positive=False, 
            weight=0.5
        )
    
    def _process_play(self, context: UserContext, features: Dict[str, float]) -> None:
        """Traitement d'une lecture complète d'une piste."""
        # Renforcer légèrement les préférences
        self._update_audio_preferences(
            context.audio_prefs,
            features,
            positive=True,
            weight=0.3
        )
    
    def _update_audio_preferences(self, 
                                prefs: AudioPreferences, 
                                features: Dict[str, float], 
                                positive: bool,
                                weight: float = 1.0) -> None:
        """Met à jour les préférences audio en fonction d'une interaction.
        
        Args:
            prefs: Préférences audio à mettre à jour
            features: Caractéristiques de la piste
            positive: Si l'interaction est positive (like/lecture) ou négative (dislike/skip)
            weight: Poids de la mise à jour (0.0-1.0)
        """
        # Mise à jour des préférences de BPM
        if 'tempo' in features:
            bpm = features['tempo']
            current_min, current_max = prefs.preferred_bpm_range
            
            if positive:
                # Élargir légèrement la plage préférée
                new_min = min(current_min, bpm * 0.9)
                new_max = max(current_max, bpm * 1.1)
            else:
                # Réduire la plage préférée
                if bpm < current_min or bpm > current_max:
                    # La peste est déjà en dehors de la plage, rien à faire
                    pass
                else:
                    # Ajuster la borne la plus proche
                    if bpm - current_min < current_max - bpm:
                        new_min = current_min + (bpm - current_min) * 0.5
                        new_max = current_max
                    else:
                        new_min = current_min
                        new_max = current_max - (current_max - bpm) * 0.5
            
            prefs.preferred_bpm_range = (new_min, new_max)
        
        # Mise à jour des préférences d'énergie et de valence
        for feature in ['energy', 'valence']:
            if feature in features:
                current_val = getattr(prefs, f'preferred_{feature}')
                feature_val = features[feature]
                
                if positive:
                    # Se rapprocher de la valeur actuelle
                    new_val = current_val * 0.9 + feature_val * 0.1 * weight
                else:
                    # S'éloigner de la valeur actuelle
                    delta = (feature_val - current_val) * 0.1 * weight
                    new_val = current_val - delta
                
                # Maintenir la valeur dans la plage [0, 1]
                new_val = max(0.0, min(1.0, new_val))
                setattr(prefs, f'preferred_{feature}', new_val)

# Fonction utilitaire pour créer un contexte utilisateur de test
def create_test_context() -> UserContext:
    """Crée un contexte utilisateur de test."""
    from .models.context import UserMood, ActivityContext, AudioPreferences, ActivityType, MoodType
    
    user_mood = UserMood(
        mood_type=MoodType.HAPPY,
        intensity=0.8,
        source='voice',
        timestamp=datetime.utcnow()
    )
    
    activity = ActivityContext(
        activity_type=ActivityType.WORKING,
        start_time=datetime.utcnow(),
        device='desktop',
        is_moving=False
    )
    
    audio_prefs = AudioPreferences()
    
    return UserContext(
        user_id='test_user',
        current_mood=user_mood,
        current_activity=activity,
        audio_prefs=audio_prefs
    )

# Exemple d'utilisation
if __name__ == "__main__":
    # Création d'un contexte utilisateur de test
    context = create_test_context()
    
    # Création du moteur d'apprentissage
    learner = LearningEngine()
    
    # Simulation d'interactions
    test_track = {
        'tempo': 120,
        'energy': 0.8,
        'valence': 0.7,
        'genre': 'pop',
        'artist_id': 'artist_123'
    }
    
    print("Avant like:", context.audio_prefs)
    
    # L'utilisateur aime une piste
    learner.update_from_interaction(
        context=context,
        track_id='track_123',
        track_features=test_track,
        interaction_type='like'
    )
    
    print("Après like:", context.audio_prefs)
