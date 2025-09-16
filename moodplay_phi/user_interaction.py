"""
Gestion des interactions avec l'utilisateur pour MoodPlae.

Ce module gère la collecte des informations utilisateur via des questions
et transforme ces informations en contexte utilisable par le moteur de recommandation.
"""
from datetime import datetime
from typing import Dict, Optional, Tuple
import logging

from .models.context import UserMood, ActivityContext, ActivityType, MoodType, UserContext, AudioPreferences

# Configuration du logger
logger = logging.getLogger(__name__)

class UserInteraction:
    """Gère les interactions avec l'utilisateur pour collecter des informations contextuelles."""
    
    def __init__(self):
        """Initialise le gestionnaire d'interactions utilisateur."""
        self.mood_mapping = {
            "heureux": MoodType.HAPPY,
            "content": MoodType.HAPPY,
            "joyeux": MoodType.HAPPY,
            "triste": MoodType.SAD,
            "énervé": MoodType.ENERGETIC,
            "énervée": MoodType.ENERGETIC,
            "énervé": MoodType.ENERGETIC,
            "calme": MoodType.CALM,
            "détendu": MoodType.CALM,
            "détendue": MoodType.CALM,
            "concentré": MoodType.FOCUSED,
            "concentrée": MoodType.FOCUSED,
            "fatigué": MoodType.TIRED,
            "fatiguée": MoodType.TIRED,
            "neutre": MoodType.NEUTRAL,
        }
        
        self.activity_mapping = {
            "travail": ActivityType.WORKING,
            "travailler": ActivityType.WORKING,
            "boulot": ActivityType.WORKING,
            "sport": ActivityType.EXERCISING,
            "courir": ActivityType.EXERCISING,
            "marche": ActivityType.EXERCISING,
            "marche à pied": ActivityType.EXERCISING,
            "vélo": ActivityType.EXERCISING,
            "voiture": ActivityType.COMMUTING,
            "conduire": ActivityType.COMMUTING,
            "transport": ActivityType.COMMUTING,
            "transports": ActivityType.COMMUTING,
            "métro": ActivityType.COMMUTING,
            "bus": ActivityType.COMMUTING,
            "amis": ActivityType.SOCIALIZING,
            "ami": ActivityType.SOCIALIZING,
            "amie": ActivityType.SOCIALIZING,
            "soirée": ActivityType.SOCIALIZING,
            "fête": ActivityType.SOCIALIZING,
            "détente": ActivityType.RELAXING,
            "repos": ActivityType.RELAXING,
            "dormir": ActivityType.RELAXING,
            "sommeil": ActivityType.RELAXING,
        }
    
    def ask_mood(self) -> Tuple[MoodType, float]:
        """Demande à l'utilisateur comment il se sent.
        
        Returns:
            Un tuple contenant le type d'humeur et son intensité (0.0-1.0)
        """
        print("\n=== Humeur actuelle ===")
        print("Salut ! Comment te sens-tu en ce moment ?")
        print("Exemples: heureux, triste, énergique, calme, fatigué, concentré, etc.")
        
        while True:
            try:
                mood_input = input("\n> ").strip().lower()
                
                # Détection de l'humeur
                mood_type = self._detect_mood(mood_input)
                
                # Demande d'intensité si l'humeur est reconnue
                if mood_type != MoodType.NEUTRAL:
                    intensity = self._ask_intensity()
                else:
                    intensity = 0.5  # Intensité neutre par défaut
                
                return mood_type, intensity
                
            except ValueError as e:
                print(f"Je n'ai pas bien compris. {e} Réessaye :)")
    
    def ask_activity(self) -> ActivityType:
        """Demande à l'utilisateur ce qu'il est en train de faire.
        
        Returns:
            Le type d'activité détecté
        """
        print("\n=== Activité actuelle ===")
        print("Qu'est-ce que tu es en train de faire en ce moment ?")
        print("Exemples: travailler, faire du sport, me déplacer, me détendre, etc.")
        
        while True:
            try:
                activity_input = input("\n> ").strip().lower()
                return self._detect_activity(activity_input)
            except ValueError as e:
                print(f"Je n'ai pas bien compris. {e} Réessaye :)")
    
    def _detect_mood(self, text: str) -> MoodType:
        """Détecte l'humeur à partir du texte saisi par l'utilisateur."""
        text = text.lower()
        
        # Vérifie les correspondances directes
        for keyword, mood in self.mood_mapping.items():
            if keyword in text:
                return mood
        
        # Détection par mots-clés plus avancée
        positive_words = ["bien", "super", "génial", "excellent", "bien"]
        negative_words = ["mal", "pas bien", "mauvais", "nul", "déprimé"]
        
        if any(word in text for word in positive_words):
            return MoodType.HAPPY
        elif any(word in text for word in negative_words):
            return MoodType.SAD
        
        # Si on ne peut pas déterminer, on retourne neutre
        return MoodType.NEUTRAL
    
    def _detect_activity(self, text: str) -> ActivityType:
        """Détecte l'activité à partir du texte saisi par l'utilisateur."""
        text = text.lower()
        
        # Vérifie les correspondances directes
        for keyword, activity in self.activity_mapping.items():
            if keyword in text:
                return activity
        
        # Détection par mots-clés plus avancée
        if any(word in text for word in ["travail", "bureau", "réunion", "ordinateur"]):
            return ActivityType.WORKING
        elif any(word in text for word in ["sport", "courir", "vélo", "nager", "muscu"]):
            return ActivityType.EXERCISING
        elif any(word in text for word in ["voiture", "métro", "bus", "train", "marcher", "route"]):
            return ActivityType.COMMUTING
        elif any(word in text for word in ["ami", "copain", "copine", "fête", "soirée"]):
            return ActivityType.SOCIALIZING
        
        # Par défaut, on considère que l'utilisateur se détend
        return ActivityType.RELAXING
    
    def _ask_intensity(self, prompt: str = "Sur une échelle de 1 à 10, à quel point ? ") -> float:
        """Demande à l'utilisateur d'évaluer l'intensité de son humeur."""
        while True:
            try:
                value = input(prompt)
                intensity = int(value.strip())
                
                if 1 <= intensity <= 10:
                    # Normalisation entre 0.1 et 1.0
                    return min(max(intensity / 10, 0.1), 1.0)
                else:
                    print("Veuillez entrer un nombre entre 1 et 10.")
            except ValueError:
                print("Veuillez entrer un nombre valide.")
    
    def collect_context(self) -> UserContext:
        """Collecte les informations contextuelles auprès de l'utilisateur."""
        print("\n" + "="*50)
        print("Bienvenue sur MoodPlae !")
        print("Je vais te poser quelques questions pour mieux te connaître.")
        print("="*50 + "\n")
        
        # 1. Demander l'humeur
        mood_type, intensity = self.ask_mood()
        
        # 2. Demander l'activité
        activity_type = self.ask_activity()
        
        # 3. Créer le contexte utilisateur
        user_mood = UserMood(
            mood_type=mood_type,
            intensity=intensity,
            source='user_input',
            timestamp=datetime.utcnow()
        )
        
        activity = ActivityContext(
            activity_type=activity_type,
            start_time=datetime.utcnow(),
            device=self._detect_device(),
            is_moving=activity_type in [ActivityType.EXERCISING, ActivityType.COMMUTING]
        )
        
        # Création du contexte utilisateur
        context = UserContext(
            user_id="temporary_user",  # À remplacer par un ID utilisateur réel
            current_mood=user_mood,
            current_activity=activity,
            audio_prefs=AudioPreferences()
        )
        
        # Mise à jour de l'heure du jour
        context.update_time_of_day()
        
        print("\n" + "="*50)
        print("Merci pour ces informations ! Je prépare tes recommandations...")
        print("="*50 + "\n")
        
        return context
    
    def _detect_device(self) -> str:
        """Détecte le type d'appareil (simplifié)."""
        # Dans une vraie application, on pourrait détecter l'appareil réellement
        # Pour l'instant, on suppose que c'est un ordinateur
        return "desktop"

# Exemple d'utilisation
if __name__ == "__main__":
    # Configuration du logging
    logging.basicConfig(level=logging.INFO)
    
    # Création de l'interface utilisateur
    ui = UserInteraction()
    
    # Collecte du contexte
    context = ui.collect_context()
    
    # Affichage du résumé
    print("\nContexte utilisateur collecté :")
    print(f"- Humeur : {context.current_mood.mood_type.value} (intensité: {context.current_mood.intensity:.1f})")
    print(f"- Activité : {context.current_activity.activity_type.value}")
    print(f"- Période de la journée : {context.time_of_day.value}")
