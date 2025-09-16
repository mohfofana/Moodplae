"""
Point d'entrée principal pour MoodPlae.

Gère le flux utilisateur et coordonne les composants du système.
"""
import logging
import sys
from datetime import datetime

from .user_interaction import UserInteraction
from .recommendation_engine import RecommendationEngine
from .learning_engine import LearningEngine
from .context_detector import ContextDetector
from .config import Config

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('moodplae.log')
    ]
)
logger = logging.getLogger(__name__)

class MoodPlaeApp:
    """Classe principale de l'application."""
    
    def __init__(self):
        self.config = Config()
        self.user_interaction = UserInteraction()
        self.learning_engine = LearningEngine()
        self.context_detector = ContextDetector(self.config)
        self.user_context = None
        logger.info("Application MoodPlae initialisée")
    
    def _collect_context(self) -> dict:
        """Collecte le contexte complet de l'utilisateur."""
        print("\n" + "="*50)
        print("🎵  BIENVENUE SUR MOODPLAE  🎵")
        print("="*50 + "\n")
        
        # 1. Collecter les informations de base
        print("Pour mieux vous connaître et vous proposer des recommandations personnalisées...")
        
        # 2. Détection du contexte
        print("\nDétection de votre contexte...")
        context = self.context_detector.get_context_summary({
            'user_agent': ' '.join(sys.argv),
            'location': input("Dans quelle ville vous trouvez-vous actuellement ? ").strip()
        })
        
        # 3. Interaction utilisateur
        print("\nParlons un peu de vous...")
        self.user_context = self.user_interaction.collect_context()
        
        # Fusionner les contextes
        if context:
            self.user_context.update(context)
            
        return self.user_context
    
    def _generate_recommendations(self) -> list:
        """Génère des recommandations basées sur le contexte."""
        print("\nAnalyse de vos préférences...")
        
        # 1. Initialiser le moteur de recommandation
        engine = RecommendationEngine(self.user_context)
        
        # 2. Générer des recommandations
        print("Génération de vos recommandations personnalisées...")
        
        # Pour l'instant, on retourne des exemples
        recommendations = [
            "Playlist 'Énergie positive'",
            "Playlist 'Concentration maximale'",
            "Découverte de la semaine"
        ]
        
        # Si on a des données météo, on peut personnaliser davantage
        if 'weather' in self.user_context:
            weather = self.user_context['weather']
            if 'rain' in weather['weather_description'].lower():
                recommendations.append("Ambiance pluie et détente")
            elif weather['temperature'] > 25:
                recommendations.append("Chill d'été")
                
        return recommendations
    
    def run(self):
        """Lance l'application."""
        try:
            # 1. Collecter le contexte
            self._collect_context()
            
            # 2. Générer des recommandations
            recommendations = self._generate_recommendations()
            
            # 3. Afficher les recommandations
            print("\n🎧  Recommandations personnalisées :")
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec}")
            
            # 4. Demander un retour
            feedback = input("\nCes recommandations vous conviennent-elles ? (Oui/Non) ").lower()
            if 'n' in feedback:
                print("Merci pour votre retour. Nous en tiendrons compte pour la prochaine fois !")
            
            print("\nMerci d'avoir utilisé MoodPlae !")
            
        except KeyboardInterrupt:
            print("\n\nAu revoir ! À bientôt sur MoodPlae :)")
        except Exception as e:
            logger.error(f"Erreur : {e}", exc_info=True)
            print(f"\nUne erreur est survenue : {e}")
            print("Veuillez réessayer ou consulter les logs pour plus de détails.")

def main():
    """Point d'entrée principal de l'application."""
    try:
        app = MoodPlaeApp()
        app.run()
    except Exception as e:
        logger.critical(f"Erreur critique : {e}", exc_info=True)
        print("\nUne erreur critique est survenue. L'application va se terminer.")
        sys.exit(1)

if __name__ == "__main__":
    main()
