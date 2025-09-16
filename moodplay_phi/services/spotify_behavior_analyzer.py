"""
Service d'analyse du comportement utilisateur via l'API Spotify.

Ce service se connecte à l'API Spotify pour récupérer les données d'écoute
et les intégrer dans notre modèle de comportement utilisateur.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import time

from ..models.user_behavior import UserBehavior, TrackInteraction
from ..config import Config

logger = logging.getLogger(__name__)

class SpotifyBehaviorAnalyzer:
    """Classe pour analyser le comportement utilisateur via Spotify."""
    
    def __init__(self, spotify_client: Any, config: Config):
        """
        Initialise l'analyseur avec un client Spotify configuré.
        
        Args:
            spotify_client: Client Spotify authentifié
            config: Configuration de l'application
        """
        self.spotify = spotify_client
        self.config = config
        self.max_retries = 3
        self.retry_delay = 2  # secondes
    
    def get_recently_played(self, limit: int = 50) -> List[Dict]:
        """Récupère les pistes récemment écoutées."""
        for attempt in range(self.max_retries):
            try:
                results = self.spotify.current_user_recently_played(limit=limit)
                return results.get('items', [])
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Erreur lors de la récupération de l'historique: {e}")
                    return []
                time.sleep(self.retry_delay * (attempt + 1))
    
    def get_audio_features(self, track_ids: List[str]) -> Dict[str, Any]:
        """Récupère les caractéristiques audio pour une liste de pistes."""
        if not track_ids:
            return {}
            
        for attempt in range(self.max_retries):
            try:
                # L'API a une limite de 100 IDs par requête
                features = {}
                for i in range(0, len(track_ids), 100):
                    batch = track_ids[i:i+100]
                    results = self.spotify.audio_features(batch)
                    features.update({
                        track_id: feature 
                        for track_id, feature in zip(batch, results)
                        if feature is not None
                    })
                return features
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Erreur lors de la récupération des features audio: {e}")
                    return {}
                time.sleep(self.retry_delay * (attempt + 1))
    
    def get_track_details(self, track_ids: List[str]) -> Dict[str, Any]:
        """Récupère les détails complets des pistes."""
        if not track_ids:
            return {}
            
        for attempt in range(self.max_retries):
            try:
                # L'API a une limite de 50 IDs par requête
                details = {}
                for i in range(0, len(track_ids), 50):
                    batch = track_ids[i:i+50]
                    results = self.spotify.tracks(batch)
                    details.update({
                        track['id']: track 
                        for track in results.get('tracks', [])
                        if track is not None
                    })
                return details
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Erreur lors de la récupération des détails des pistes: {e}")
                    return {}
                time.sleep(self.retry_delay * (attempt + 1))
    
    def analyze_recent_behavior(
        self, 
        user_behavior: UserBehavior,
        context: Optional[Dict] = None
    ) -> UserBehavior:
        """
        Analyse le comportement récent de l'utilisateur.
        
        Args:
            user_behavior: Instance de UserBehavior à mettre à jour
            context: Contexte supplémentaire (humeur, activité, etc.)
            
        Returns:
            UserBehavior mis à jour avec les nouvelles interactions
        """
        if context is None:
            context = {}
            
        # 1. Récupérer l'historique récent
        recent_tracks = self.get_recently_played(limit=50)
        if not recent_tracks:
            logger.warning("Aucune piste récente trouvée")
            return user_behavior
        
        # 2. Extraire les IDs des pistes
        track_ids = [item['track']['id'] for item in recent_tracks if item['track']]
        
        # 3. Récupérer les détails et caractéristiques audio
        track_details = self.get_track_details(track_ids)
        audio_features = self.get_audio_features(track_ids)
        
        # 4. Traiter chaque piste écoutée
        for item in recent_tracks:
            track = item['track']
            if not track or not track['id']:
                continue
                
            # Créer le contexte d'interaction
            interaction_context = {
                'track_name': track['name'],
                'artists': [artist['name'] for artist in track['artists']],
                'genres': self._extract_genres(track, track_details),
                'audio_features': audio_features.get(track['id'], {}),
                'played_at': item.get('played_at'),
                'context_type': item.get('context', {}).get('type'),
                **context
            }
            
            # Créer l'interaction
            interaction = TrackInteraction(
                track_id=track['id'],
                timestamp=datetime.fromisoformat(item['played_at'].replace('Z', '+00:00')),
                duration_played=track['duration_ms'] / 1000,  # ms -> secondes
                duration_total=track['duration_ms'] / 1000,
                skipped=self._was_skipped(item, track['duration_ms']),
                liked=self._is_liked(track['id']),  # À implémenter avec l'API des titres likés
                context=interaction_context
            )
            
            # Ajouter l'interaction au comportement utilisateur
            user_behavior.add_interaction(interaction)
        
        return user_behavior
    
    def _extract_genres(self, track: Dict, track_details: Dict) -> List[str]:
        """Extrait les genres d'une piste à partir des artistes."""
        genres = set()
        
        for artist in track['artists']:
            artist_id = artist['id']
            if artist_id in track_details:
                genres.update(track_details[artist_id].get('genres', []))
        
        return list(genres)
    
    def _was_skipped(self, track_item: Dict, track_duration_ms: int) -> bool:
        """Détermine si une piste a été sautée."""
        # Si la piste a été écoutée pendant moins de 30 secondes, considérée comme sautée
        return track_item.get('played_duration_ms', 0) < min(30000, track_duration_ms * 0.5)
    
    def _is_liked(self, track_id: str) -> bool:
        """Vérifie si une piste est dans les titres likés de l'utilisateur."""
        for attempt in range(self.max_retries):
            try:
                return self.spotify.current_user_saved_tracks_contains([track_id])[0]
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Erreur lors de la vérification des titres likés: {e}")
                    return False
                time.sleep(self.retry_delay * (attempt + 1))
    
    def get_recommendations(
        self, 
        user_behavior: UserBehavior,
        limit: int = 20,
        **filters
    ) -> List[Dict]:
        """
        Obtient des recommandations basées sur le comportement utilisateur.
        
        Args:
            user_behavior: Comportement utilisateur analysé
            limit: Nombre de recommandations à retourner
            **filters: Filtres supplémentaires (genre, popularité, etc.)
            
        Returns:
            Liste des pistes recommandées
        """
        try:
            # 1. Analyser les préférences de l'utilisateur
            top_tracks = sorted(
                user_behavior.track_interactions,
                key=lambda x: user_behavior.get_track_affinity(x.track_id),
                reverse=True
            )[:5]  # Top 5 pistes préférées
            
            if not top_tracks:
                logger.warning("Pas assez de données pour des recommandations personnalisées")
                return []
            
            # 2. Préparer les paramètres de recommandation
            seed_tracks = [t.track_id for t in top_tracks]
            seed_genres = [g[0] for g in user_behavior.get_preferred_genres(3)]
            
            # 3. Obtenir des recommandations
            recommendations = self.spotify.recommendations(
                seed_tracks=seed_tracks[:5],  # Max 5 seed tracks
                seed_genres=seed_genres[:2],  # Max 2 seed genres
                limit=limit,
                **filters
            )
            
            return recommendations.get('tracks', [])
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des recommandations: {e}")
            return []
