"""
Configuration de l'application MoodPlae.
"""
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

class Config:
    """Classe de configuration principale."""
    
    # Configuration de base
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    ENV: str = os.getenv('ENV', 'development')
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Base de données
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///./moodplae.db')
    TEST_DATABASE_URL: str = os.getenv('TEST_DATABASE_URL', 'sqlite:///./test_moodplae.db')
    
    # Configuration Spotify
    SPOTIFY_CLIENT_ID: str = os.getenv('SPOTIFY_CLIENT_ID', '')
    SPOTIFY_CLIENT_SECRET: str = os.getenv('SPOTIFY_CLIENT_SECRET', '')
    SPOTIFY_REDIRECT_URI: str = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:8000/auth/callback')
    
    # Cache
    CACHE_TTL: int = int(os.getenv('CACHE_TTL', '300'))  # 5 minutes par défaut
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # Paramètres de l'algorithme
    RECOMMENDATION_LIMIT: int = 50
    DEFAULT_SESSION_MINUTES: int = 60
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Retourne la configuration sous forme de dictionnaire."""
        return {
            key: value for key, value in cls.__dict__.items()
            if not key.startswith('_') and not callable(value)
        }

# Instance de configuration
global_config = Config()

# Exemple d'utilisation:
# from config import global_config as config
# print(config.DEBUG)
