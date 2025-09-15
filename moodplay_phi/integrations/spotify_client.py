"""
Client pour l'API Spotify.
"""
import os
import base64
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

class SpotifyClient:
    """Client pour interagir avec l'API Spotify."""
    
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
        """Génère l'URL d'autorisation OAuth."""
        scope = ' '.join([
            'user-read-private',
            'user-read-email',
            'user-read-recently-played',
            'user-top-read',
            'user-read-playback-state',
            'user-modify-playback-state',
            'user-read-currently-playing',
            'app-remote-control',
            'streaming',
            'user-read-playback-position',
            'user-library-read'
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
            if 'refresh_token' in kwargs:
                self.refresh_token(kwargs.pop('refresh_token'))
            else:
                raise ValueError("No valid access token or refresh token provided")
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        if 'headers' in kwargs:
            headers.update(kwargs.pop('headers'))
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        
        return response.json()
    
    def get_user_profile(self) -> Dict:
        """Récupère le profil de l'utilisateur."""
        return self._make_request('GET', 'me')
    
    def get_recently_played(self, limit: int = 50) -> List[Dict]:
        """Récupère les titres récemment écoutés."""
        params = {'limit': limit}
        response = self._make_request('GET', 'me/player/recently-played', params=params)
        return response.get('items', [])
    
    def get_top_artists(self, limit: int = 20, time_range: str = 'medium_term') -> List[Dict]:
        """Récupère les artistes les plus écoutés."""
        params = {
            'limit': limit,
            'time_range': time_range  # short_term, medium_term, long_term
        }
        response = self._make_request('GET', 'me/top/artists', params=params)
        return response.get('items', [])
    
    def get_top_tracks(self, limit: int = 20, time_range: str = 'medium_term') -> List[Dict]:
        """Récupère les titres les plus écoutés."""
        params = {
            'limit': limit,
            'time_range': time_range
        }
        response = self._make_request('GET', 'me/top/tracks', params=params)
        return response.get('items', [])
    
    def get_audio_features(self, track_ids: List[str]) -> List[Dict]:
        """Récupère les caractéristiques audio des titres."""
        if not track_ids:
            return []
            
        # L'API Spotify limite à 100 IDs par requête
        chunks = [track_ids[i:i + 100] for i in range(0, len(track_ids), 100)]
        all_features = []
        
        for chunk in chunks:
            params = {'ids': ','.join(chunk)}
            response = self._make_request('GET', 'audio-features', params=params)
            all_features.extend(response.get('audio_features', []))
        
        return all_features
    
    def get_user_playlists(self, limit: int = 50) -> List[Dict]:
        """Récupère les playlists de l'utilisateur."""
        params = {'limit': limit}
        response = self._make_request('GET', 'me/playlists', params=params)
        return response.get('items', [])
    
    def get_current_playback(self) -> Optional[Dict]:
        """Récupère l'état de lecture actuel."""
        try:
            return self._make_request('GET', 'me/player/currently-playing')
        except requests.HTTPError as e:
            if e.response.status_code == 204:  # Pas de lecture en cours
                return None
            raise
    
    def start_playback(self, context_uri: str = None, uris: List[str] = None, offset: Dict = None) -> None:
        """Démarre la lecture d'une playlist ou d'une liste de titres."""
        data = {}
        if context_uri:
            data['context_uri'] = context_uri
        if uris:
            data['uris'] = uris
        if offset:
            data['offset'] = offset
            
        self._make_request('PUT', 'me/player/play', json=data)
    
    def pause_playback(self) -> None:
        """Met en pause la lecture en cours."""
        self._make_request('PUT', 'me/player/pause')
    
    def skip_to_next(self) -> None:
        """Passe au titre suivant."""
        self._make_request('POST', 'me/player/next')
    
    def skip_to_previous(self) -> None:
        """Revient au titre précédent."""
        self._make_request('POST', 'me/player/previous')
    
    def set_volume(self, volume_percent: int) -> None:
        """Définit le volume de lecture."""
        if not 0 <= volume_percent <= 100:
            raise ValueError("Volume must be between 0 and 100")
        
        params = {'volume_percent': volume_percent}
        self._make_request('PUT', 'me/player/volume', params=params)
    
    def transfer_playback(self, device_id: str, play: bool = False) -> None:
        """Transfère la lecture vers un autre appareil."""
        data = {
            'device_ids': [device_id],
            'play': play
        }
        self._make_request('PUT', 'me/player', json=data)
    
    def get_available_devices(self) -> List[Dict]:
        """Récupère la liste des appareils disponibles."""
        response = self._make_request('GET', 'me/player/devices')
        return response.get('devices', [])
    
    def get_recommendations(
        self, 
        seed_artists: List[str] = None,
        seed_genres: List[str] = None,
        seed_tracks: List[str] = None,
        limit: int = 20,
        **audio_features
    ) -> List[Dict]:
        """Récupère des recommandations basées sur des seeds et des critères audio."""
        if not any([seed_artists, seed_genres, seed_tracks]):
            raise ValueError("At least one seed type must be provided")
        
        params = {'limit': limit}
        
        if seed_artists:
            params['seed_artists'] = ','.join(seed_artists)
        if seed_genres:
            params['seed_genres'] = ','.join(seed_genres)
        if seed_tracks:
            params['seed_tracks'] = ','.join(seed_tracks)
        
        # Ajoute les caractéristiques audio si fournies
        for feature, value in audio_features.items():
            if value is not None:
                params[feature] = value
        
        response = self._make_request('GET', 'recommendations', params=params)
        return response.get('tracks', [])
