"""
Intégration avec l'API Spotify pour MoodPlae.

Ce module fournit une interface pour interagir avec l'API Spotify et récupérer
des données utilisateur, des pistes et des fonctionnalités audio.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

# Configuration du logger
logger = logging.getLogger(__name__)

@dataclass
class SpotifyTrack:
    """Représente une piste Spotify avec ses métadonnées."""
    id: str
    name: str
    artists: List[Dict[str, str]]  # Liste de dictionnaires avec 'id' et 'name'
    album: Dict[str, str]  # Dictionnaire avec 'id', 'name', 'images', etc.
    duration_ms: int
    popularity: int
    external_urls: Dict[str, str]
    uri: str
    features: Dict[str, float]  # Caractéristiques audio
    
    @property
    def artist_names(self) -> List[str]:
        """Retourne la liste des noms d'artistes."""
        return [artist['name'] for artist in self.artists]
    
    @property
    def main_artist(self) -> str:
        """Retourne le nom du premier artiste."""
        return self.artists[0]['name'] if self.artists else "Inconnu"

class SpotifyClient:
    """Client pour interagir avec l'API Spotify."""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        """Initialise le client Spotify.
        
        Args:
            client_id: ID client de l'application Spotify
            client_secret: Clé secrète de l'application Spotify
            redirect_uri: URI de redirection OAuth
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expires: Optional[datetime] = None
    
    def authenticate(self, authorization_code: str) -> bool:
        """Authentifie l'utilisateur avec un code d'autorisation.
        
        Args:
            authorization_code: Code d'autorisation OAuth
            
        Returns:
            True si l'authentification a réussi, False sinon
        """
        try:
            # TODO: Implémenter l'authentification OAuth avec Spotify
            # - Échanger le code d'autorisation contre un token d'accès
            # - Stocker le token d'accès et le refresh token
            # - Définir la date d'expiration du token
            logger.info("Authentification Spotify en cours...")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'authentification Spotify: {e}")
            return False
    
    def refresh_access_token(self) -> bool:
        """Rafraîchit le token d'accès avec le refresh token."""
        try:
            # TODO: Implémenter le rafraîchissement du token
            logger.info("Rafraîchissement du token d'accès...")
            return True
        except Exception as e:
            logger.error(f"Erreur lors du rafraîchissement du token: {e}")
            return False
    
    def get_user_profile(self) -> Optional[Dict]:
        """Récupère le profil de l'utilisateur connecté.
        
        Returns:
            Dictionnaire contenant les informations du profil utilisateur
        """
        try:
            # TODO: Implémenter la récupération du profil utilisateur
            logger.info("Récupération du profil utilisateur...")
            return {
                'id': 'user_123',
                'display_name': 'Utilisateur de test',
                'email': 'test@example.com',
                'country': 'FR',
                'product': 'premium',
                'images': []
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du profil: {e}")
            return None
    
    def get_recently_played(self, limit: int = 50) -> List[SpotifyTrack]:
        """Récupère les titres récemment écoutés par l'utilisateur.
        
        Args:
            limit: Nombre maximum de titres à récupérer (1-50)
            
        Returns:
            Liste des pistes récemment écoutées
        """
        try:
            # TODO: Implémenter la récupération de l'historique
            logger.info(f"Récupération des {limit} titres récemment écoutés...")
            return []
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'historique: {e}")
            return []
    
    def get_audio_features(self, track_ids: List[str]) -> List[Dict[str, float]]:
        """Récupère les caractéristiques audio d'une liste de pistes.
        
        Args:
            track_ids: Liste des IDs des pistes
            
        Returns:
            Liste des caractéristiques audio pour chaque piste
        """
        try:
            # TODO: Implémenter la récupération des caractéristiques audio
            logger.info(f"Récupération des caractéristiques audio pour {len(track_ids)} pistes...")
            return []
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des caractéristiques audio: {e}")
            return []
    
    def get_recommendations(self, seed_tracks: List[str] = None,
                          seed_artists: List[str] = None,
                          seed_genres: List[str] = None,
                          limit: int = 20) -> List[SpotifyTrack]:
        """Récupère des recommandations basées sur des critères donnés.
        
        Args:
            seed_tracks: Liste d'IDs de pistes de départ
            seed_artists: Liste d'IDs d'artistes de départ
            seed_genres: Liste de genres de départ
            limit: Nombre de recommandations à retourner (1-100)
            
        Returns:
            Liste des pistes recommandées
        """
        try:
            # TODO: Implémenter la récupération de recommandations
            logger.info("Récupération de recommandations...")
            return []
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des recommandations: {e}")
            return []
    
    def create_playlist(self, user_id: str, name: str, description: str = "") -> Optional[Dict]:
        """Crée une nouvelle playlist pour l'utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            name: Nom de la playlist
            description: Description de la playlist
            
        Returns:
            Dictionnaire contenant les informations de la playlist créée
        """
        try:
            # TODO: Implémenter la création de playlist
            logger.info(f"Création de la playlist '{name}'...")
            return {
                'id': 'playlist_123',
                'name': name,
                'description': description,
                'external_urls': {},
                'tracks': {'total': 0}
            }
        except Exception as e:
            logger.error(f"Erreur lors de la création de la playlist: {e}")
            return None
    
    def add_tracks_to_playlist(self, playlist_id: str, track_uris: List[str]) -> bool:
        """Ajoute des pistes à une playlist.
        
        Args:
            playlist_id: ID de la playlist
            track_uris: Liste des URIs des pistes à ajouter
            
        Returns:
            True si l'ajout a réussi, False sinon
        """
        try:
            # TODO: Implémenter l'ajout de pistes à une playlist
            logger.info(f"Ajout de {len(track_uris)} pistes à la playlist {playlist_id}...")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout des pistes à la playlist: {e}")
            return False

# Exemple d'utilisation
if __name__ == "__main__":
    # Configuration du logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialisation du client (remplacer par vos identifiants)
    client = SpotifyClient(
        client_id="votre_client_id",
        client_secret="votre_client_secret",
        redirect_uri="votre_redirect_uri"
    )
    
    # Simulation d'authentification (à remplacer par le flux OAuth réel)
    if client.authenticate("code_autorisation"):
        print("Authentification réussie!")
        
        # Récupération du profil utilisateur
        profile = client.get_user_profile()
        if profile:
            print(f"Profil utilisateur: {profile['display_name']}")
        
        # Récupération des titres récemment écoutés
        recent_tracks = client.get_recently_played(limit=5)
        print(f"Derniers titres écoutés: {len(recent_tracks)}")
        
        # Création d'une playlist de test
        playlist = client.create_playlist(
            user_id=profile['id'],
            name="Ma playlist MoodPlae",
            description="Playlist générée automatiquement par MoodPlae"
        )
        
        if playlist:
            print(f"Playlist créée: {playlist['name']}")
