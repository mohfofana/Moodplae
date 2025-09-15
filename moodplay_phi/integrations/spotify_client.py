"""
Client Spotify optimisé pour MoodPlae.
Récupère les données essentielles pour les recommandations basées sur mood + contexte.
"""
import os
import base64
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

class SpotifyClient:
    """Client Spotify pour MoodPlae - Focus sur goûts utilisateur et tracking engagement."""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        """Initialise le client Spotify.
        
        Args:
            client_id: ID client de l'application Spotify
            client_secret: Secret client de l'application Spotify
            redirect_uri: URI de redirection après authentification
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.base_url = "https://api.spotify.com/v1"
        self.token_url = "https://accounts.spotify.com/api/token"
        self.access_token = None
        self.token_expiry = None
    
    def get_auth_url(self) -> str:
        """Génère l'URL d'autorisation OAuth avec tous les scopes nécessaires."""
        scope = ' '.join([
            'user-read-private',           # Profil utilisateur
            'user-read-email',             # Email utilisateur
            'user-top-read',               # Top tracks/artists
            'user-read-recently-played',   # Historique récent
            'user-read-currently-playing', # Écoute actuelle
            'user-library-read',           # Liked songs/albums
            'playlist-modify-public',      # Créer playlists publiques
            'playlist-modify-private',     # Créer playlists privées
            'playlist-read-private',       # Lire playlists privées
            'user-modify-playback-state'   # Contrôler la lecture
        ])
        
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': scope,
            'show_dialog': 'true'
        }
        
        url = "https://accounts.spotify.com/authorize?"
        url += "&".join([f"{k}={v}" for k, v in params.items()])
        return url
    
    def get_access_token(self, code: str) -> Dict:
        """Échange le code d'autorisation contre un token d'accès."""
        auth_header = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        
        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri
        }
        
        response = requests.post(self.token_url, headers=headers, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        self.access_token = token_data['access_token']
        self.token_expiry = datetime.now() + timedelta(seconds=token_data['expires_in'])
        
        return token_data
    
    def refresh_token(self, refresh_token: str) -> Dict:
        """Rafraîchit le token d'accès."""
        auth_header = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        
        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        
        response = requests.post(self.token_url, headers=headers, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        self.access_token = token_data['access_token']
        if 'refresh_token' in token_data:
            refresh_token = token_data['refresh_token']
        self.token_expiry = datetime.now() + timedelta(seconds=token_data['expires_in'])
        
        return token_data
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Effectue une requête vers l'API Spotify."""
        if not self.access_token or (self.token_expiry and datetime.now() >= self.token_expiry):
            raise ValueError("No valid access token. Please authenticate first.")
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        if 'headers' in kwargs:
            headers.update(kwargs.pop('headers'))
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        
        # Handle empty responses (204 No Content)
        if response.status_code == 204:
            return {}
        
        return response.json()

    # ========================================
    # 1. PROFIL UTILISATEUR
    # ========================================
    
    def get_user_profile(self) -> Dict:
        """Récupère le profil complet de l'utilisateur.
        
        Returns:
            Dict contenant: email, display_name, id, images, country, followers
        """
        return self._make_request('GET', 'me')

    # ========================================
    # 2. GOÛTS MUSICAUX DE BASE
    # ========================================
    
    def get_user_top_tracks(self, time_range: str = 'medium_term', limit: int = 20) -> List[Dict]:
        """Récupère les titres les plus écoutés de l'utilisateur.
        
        Args:
            time_range: 'short_term' (4 weeks), 'medium_term' (6 months), 'long_term' (years)
            limit: Nombre de tracks à récupérer (max 50)
        """
        params = {'limit': limit, 'time_range': time_range}
        response = self._make_request('GET', 'me/top/tracks', params=params)
        return response.get('items', [])
    
    def get_user_top_artists(self, time_range: str = 'medium_term', limit: int = 20) -> List[Dict]:
        """Récupère les artistes les plus écoutés de l'utilisateur."""
        params = {'limit': limit, 'time_range': time_range}
        response = self._make_request('GET', 'me/top/artists', params=params)
        return response.get('items', [])
    
    def get_user_liked_songs(self, limit: int = 50) -> List[Dict]:
        """Récupère les morceaux likés par l'utilisateur."""
        params = {'limit': limit}
        response = self._make_request('GET', 'me/tracks', params=params)
        return response.get('items', [])
    
    def get_user_saved_albums(self, limit: int = 20) -> List[Dict]:
        """Récupère les albums sauvegardés par l'utilisateur."""
        params = {'limit': limit}
        response = self._make_request('GET', 'me/albums', params=params)
        return response.get('items', [])

    # ========================================
    # 3. ÉCOUTE ACTUELLE/RÉCENTE
    # ========================================
    
    def get_currently_playing(self) -> Optional[Dict]:
        """Récupère ce que l'utilisateur écoute actuellement."""
        try:
            return self._make_request('GET', 'me/player/currently-playing')
        except requests.HTTPError as e:
            if e.response.status_code == 204:  # Pas de lecture en cours
                return None
            raise
    
    def get_recently_played(self, limit: int = 20) -> List[Dict]:
        """Récupère l'historique récent d'écoute.
        
        CRUCIAL pour détecter les skips et l'engagement sur nos playlists.
        """
        params = {'limit': limit}
        response = self._make_request('GET', 'me/player/recently-played', params=params)
        return response.get('items', [])

    # ========================================
    # 4. AUDIO FEATURES (pour matching mood)
    # ========================================
    
    def get_audio_features(self, track_ids: List[str]) -> List[Dict]:
        """Récupère les caractéristiques audio des titres.
        
        Returns audio features: energy, valence, tempo, danceability, acousticness
        """
        if not track_ids:
            return []
            
        # L'API Spotify limite à 100 IDs par requête
        chunks = [track_ids[i:i + 100] for i in range(0, len(track_ids), 100)]
        all_features = []
        
        for chunk in chunks:
            params = {'ids': ','.join(chunk)}
            response = self._make_request('GET', 'audio-features', params=params)
            features = response.get('audio_features', [])
            # Filtrer les None (tracks sans audio features)
            all_features.extend([f for f in features if f is not None])
        
        return all_features
    
    def get_audio_features_for_user_tracks(self, tracks: List[Dict]) -> List[Dict]:
        """Helper pour récupérer les audio features des tracks utilisateur."""
        track_ids = []
        for track in tracks:
            # Gère différents formats de réponse Spotify
            if 'track' in track:  # Format liked songs
                track_ids.append(track['track']['id'])
            elif 'id' in track:  # Format direct
                track_ids.append(track['id'])
        
        return self.get_audio_features(track_ids)

    # ========================================
    # 5. RECOMMANDATIONS SPOTIFY (brutes)
    # ========================================
    
    def get_recommendations(
        self,
        seed_tracks: List[str] = None,
        seed_artists: List[str] = None,
        seed_genres: List[str] = None,
        limit: int = 20,
        **audio_features_targets
    ) -> List[Dict]:
        """Récupère des recommandations Spotify avec seeds et targets.
        
        Args:
            seed_tracks: IDs des tracks comme seeds
            seed_artists: IDs des artistes comme seeds  
            seed_genres: Genres comme seeds
            limit: Nombre de recommendations
            **audio_features_targets: target_energy, target_valence, etc.
        """
        if not any([seed_tracks, seed_artists, seed_genres]):
            raise ValueError("Au moins un type de seed requis")
        
        params = {'limit': limit}
        
        if seed_tracks:
            params['seed_tracks'] = ','.join(seed_tracks[:5])  # Max 5
        if seed_artists:
            params['seed_artists'] = ','.join(seed_artists[:5])  # Max 5
        if seed_genres:
            params['seed_genres'] = ','.join(seed_genres[:5])  # Max 5
        
        # Ajoute les targets audio features si fournis
        for feature, value in audio_features_targets.items():
            if value is not None:
                params[feature] = value
        
        response = self._make_request('GET', 'recommendations', params=params)
        return response.get('tracks', [])
    
    def get_available_genre_seeds(self) -> List[str]:
        """Récupère la liste des genres disponibles pour les seeds."""
        response = self._make_request('GET', 'recommendations/available-genre-seeds')
        return response.get('genres', [])

    # ========================================
    # 6. GESTION DES PLAYLISTS MOODPLAE
    # ========================================
    
    def create_moodplae_playlist(self, user_id: str, name: str, description: str = "") -> Dict:
        """Crée une nouvelle playlist MoodPlae."""
        data = {
            'name': name,
            'description': description,
            'public': False  # Playlists privées par défaut
        }
        return self._make_request('POST', f'users/{user_id}/playlists', json=data)
    
    def add_tracks_to_playlist(self, playlist_id: str, track_uris: List[str]) -> Dict:
        """Ajoute des tracks à une playlist."""
        data = {'uris': track_uris}
        return self._make_request('POST', f'playlists/{playlist_id}/tracks', json=data)
    
    def get_playlist_tracks(self, playlist_id: str) -> List[Dict]:
        """Récupère les tracks d'une playlist."""
        response = self._make_request('GET', f'playlists/{playlist_id}/tracks')
        return response.get('items', [])

    # ========================================
    # 7. TRACKING DES DONNÉES D'ENGAGEMENT
    # ========================================
    
    def get_playlist_tracks(self, playlist_id: str) -> List[Dict]:
        """Récupère les tracks d'une playlist."""
        response = self._make_request('GET', f'playlists/{playlist_id}/tracks')
        return response.get('items', [])
    
    def get_playlist_info(self, playlist_id: str) -> Dict:
        """Récupère les infos d'une playlist."""
        return self._make_request('GET', f'playlists/{playlist_id}')

    # ========================================
    # UTILS & HELPERS
    # ========================================
    
    def get_full_user_music_profile(self) -> Dict:
        """Récupère le profil musical complet de l'utilisateur pour MoodPlae."""
        profile = {
            'user_info': self.get_user_profile(),
            'top_tracks_short': self.get_user_top_tracks('short_term', 10),
            'top_tracks_medium': self.get_user_top_tracks('medium_term', 20),
            'top_artists': self.get_user_top_artists('medium_term', 15),
            'liked_songs': self.get_user_liked_songs(30),
            'current_playing': self.get_currently_playing(),
            'recent_plays': self.get_recently_played(20)
        }
        
        # Récupère les audio features pour les top tracks
        if profile['top_tracks_medium']:
            track_ids = [t['id'] for t in profile['top_tracks_medium']]
            profile['top_tracks_audio_features'] = self.get_audio_features(track_ids)
        
        return profile
