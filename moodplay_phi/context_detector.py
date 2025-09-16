"""
Détection du contexte pour MoodPlae.

Ce module gère la détection et la mise à jour du contexte utilisateur,
y compris la météo, la localisation, et d'autres facteurs environnementaux.
"""
import logging
from datetime import datetime, time
from typing import Dict, Optional, Tuple

import requests
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz

from .config import Config

logger = logging.getLogger(__name__)

class ContextDetector:
    """Classe pour détecter et mettre à jour le contexte utilisateur."""
    
    def __init__(self, config: Config):
        """Initialise le détecteur de contexte avec la configuration."""
        self.config = config
        self.geolocator = Nominatim(user_agent="moodplae_context")
        self.tf = TimezoneFinder()
        self.weather_api_key = config.WEATHER_API_KEY
        
    def detect_location(self, city_name: str) -> Optional[Dict]:
        """Détecte les coordonnées géographiques à partir d'un nom de ville.
        
        Args:
            city_name: Nom de la ville (ex: "Rennes, FR")
            
        Returns:
            Dictionnaire avec 'latitude', 'longitude' et 'timezone' ou None en cas d'erreur
        """
        try:
            location = self.geolocator.geocode(city_name)
            if not location:
                logger.warning(f"Impossible de localiser : {city_name}")
                return None
                
            timezone_str = self.tf.timezone_at(lat=location.latitude, lng=location.longitude)
            
            return {
                'latitude': location.latitude,
                'longitude': location.longitude,
                'timezone': timezone_str,
                'address': location.address
            }
        except Exception as e:
            logger.error(f"Erreur lors de la détection de localisation : {e}")
            return None
    
    def get_weather(self, latitude: float, longitude: float) -> Optional[Dict]:
        """Récupère les données météo actuelles pour une position donnée.
        
        Args:
            latitude: Latitude de la position
            longitude: Longitude de la position
            
        Returns:
            Dictionnaire avec les données météo ou None en cas d'erreur
        """
        if not self.weather_api_key:
            logger.warning("Aucune clé API météo configurée")
            return None
            
        try:
            url = (
                f"https://api.openweathermap.org/data/2.5/weather?"
                f"lat={latitude}&lon={longitude}&appid={self.weather_api_key}&units=metric&lang=fr"
            )
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'weather': data['weather'][0]['main'],
                'weather_description': data['weather'][0]['description'],
                'wind_speed': data['wind'].get('speed', 0),
                'clouds': data.get('clouds', {}).get('all', 0),
                'sunrise': datetime.fromtimestamp(data['sys']['sunrise']).time(),
                'sunset': datetime.fromtimestamp(data['sys']['sunset']).time()
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la météo : {e}")
            return None
    
    def get_time_context(self, timezone_str: str) -> Dict:
        """Détermine le contexte temporel.
        
        Args:
            timezone_str: Fuseau horaire (ex: "Europe/Paris")
            
        Returns:
            Dictionnaire avec les informations temporelles
        """
        try:
            tz = pytz.timezone(timezone_str)
            now = datetime.now(tz)
            
            # Déterminer la période de la journée
            hour = now.hour
            if 5 <= hour < 12:
                time_of_day = "morning"
            elif 12 <= hour < 17:
                time_of_day = "afternoon"
            elif 17 <= hour < 22:
                time_of_day = "evening"
            else:
                time_of_day = "night"
            
            # Déterminer le type de jour
            day_type = "weekend" if now.weekday() >= 5 else "weekday"
            
            return {
                'current_time': now,
                'time_of_day': time_of_day,
                'day_type': day_type,
                'is_work_hours': 9 <= hour < 18 and day_type == "weekday",
                'season': self._get_season(now.month)
            }
        except Exception as e:
            logger.error(f"Erreur lors de la détermination du contexte temporel : {e}")
            return {}
    
    def _get_season(self, month: int) -> str:
        """Détermine la saison en fonction du mois."""
        if 3 <= month <= 5:
            return "spring"
        elif 6 <= month <= 8:
            return "summer"
        elif 9 <= month <= 11:
            return "autumn"
        else:
            return "winter"
    
    def detect_device_type(self, user_agent: str) -> str:
        """Détecte le type d'appareil à partir du user agent.
        
        Args:
            user_agent: Chaîne User-Agent de la requête
            
        Returns:
            Type d'appareil ("mobile", "tablet", "desktop")
        """
        if not user_agent:
            return "desktop"
            
        user_agent = user_agent.lower()
        
        if any(device in user_agent for device in ["mobile", "android", "iphone"]):
            return "mobile"
        elif any(device in user_agent for device in ["tablet", "ipad"]):
            return "tablet"
        else:
            return "desktop"
    
    def get_context_summary(self, user_input: Dict) -> Dict:
        """Génère un résumé du contexte à partir des entrées utilisateur.
        
        Args:
            user_input: Dictionnaire contenant les entrées utilisateur
                - location: Nom de la ville (optionnel)
                - user_agent: User-Agent HTTP (optionnel)
                - current_time: Heure actuelle (optionnel, par défaut maintenant)
                
        Returns:
            Dictionnaire avec le contexte détecté
        """
        context = {}
        
        # Détection de la localisation
        if 'location' in user_input:
            location = self.detect_location(user_input['location'])
            if location:
                context['location'] = location
                
                # Récupération de la météo si la localisation est connue
                weather = self.get_weather(location['latitude'], location['longitude'])
                if weather:
                    context['weather'] = weather
        
        # Contexte temporel
        timezone = context.get('location', {}).get('timezone', 'UTC')
        context.update(self.get_time_context(timezone))
        
        # Type d'appareil
        if 'user_agent' in user_input:
            context['device_type'] = self.detect_device_type(user_input['user_agent'])
        
        return context

# Exemple d'utilisation
if __name__ == "__main__":
    # Configuration de base pour les tests
    class TestConfig:
        WEATHER_API_KEY = ""  # À remplacer par une vraie clé API pour les tests
    
    config = TestConfig()
    detector = ContextDetector(config)
    
    # Test avec une ville
    test_location = "Rennes, FR"
    print(f"\nTest de détection pour : {test_location}")
    
    # Détection de la localisation
    location = detector.detect_location(test_location)
    if location:
        print(f"\nLocalisation détectée :")
        print(f"- Adresse : {location['address']}")
        print(f"- Coordonnées : {location['latitude']}, {location['longitude']}")
        print(f"- Fuseau horaire : {location['timezone']}")
        
        # Contexte temporel
        time_context = detector.get_time_context(location['timezone'])
        print(f"\nContexte temporel :")
        print(f"- Heure actuelle : {time_context['current_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"- Période de la journée : {time_context['time_of_day']}")
        print(f"- Type de jour : {time_context['day_type']}")
        print(f"- Saison : {time_context['season']}")
        
        # Météo (si clé API configurée)
        if detector.weather_api_key:
            weather = detector.get_weather(location['latitude'], location['longitude'])
            if weather:
                print(f"\nMétéo actuelle :")
                print(f"- Température : {weather['temperature']}°C (ressentie {weather['feels_like']}°C)")
                print(f"- Temps : {weather['weather_description']}")
                print(f"- Humidité : {weather['humidity']}%")
                print(f"- Vent : {weather['wind_speed']} m/s")
    else:
        print("Impossible de détecter la localisation.")
    
    # Test de détection d'appareil
    test_user_agents = [
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15",
        "Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) AppleWebKit/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    ]
    
    print("\nTest de détection d'appareil :")
    for ua in test_user_agents:
        device_type = detector.detect_device_type(ua)
        print(f"- {device_type.upper()}: {ua[:60]}...")
