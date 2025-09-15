"""
Service d'analyse d'humeur et de contexte pour MoodPlae.
"""
from typing import Dict, List, Optional, Tuple
import random

class MoodAnalyzer:
    """Analyse l'humeur et le contexte de l'utilisateur."""
    
    # Mots-clés associés à différentes humeurs
    MOOD_KEYWORDS = {
        'energique': ['énergique', 'dynamique', 'motivé', 'excité', 'pétillant', 'vif'],
        'calme': ['calme', 'détendu', 'serein', 'paisible', 'tranquille'],
        'triste': ['triste', 'mélancolique', 'déprimé', 'battu', 'morose'],
        'heureux': ['heureux', 'joyeux', 'content', 'gai', 'épanoui'],
        'stressé': ['stressé', 'tendu', 'anxieux', 'pressé', 'sous pression'],
        'fatigué': ['fatigué', 'épuisé', 'lessivé', 'crevé', 'à plat']
    }
    
    # Correspondance entre humeurs et caractéristiques audio
    MOOD_TO_AUDIO_FEATURES = {
        'energique': {
            'energy': (0.7, 1.0),
            'valence': (0.6, 1.0),
            'danceability': (0.6, 1.0),
            'tempo': (100, 200)
        },
        'calme': {
            'energy': (0.0, 0.4),
            'valence': (0.3, 0.8),
            'acousticness': (0.5, 1.0),
            'instrumentalness': (0.3, 1.0),
            'tempo': (60, 100)
        },
        'triste': {
            'energy': (0.0, 0.5),
            'valence': (0.0, 0.4),
            'tempo': (50, 90)
        },
        'heureux': {
            'energy': (0.5, 1.0),
            'valence': (0.7, 1.0),
            'danceability': (0.5, 1.0),
            'tempo': (90, 160)
        },
        'stressé': {
            'energy': (0.3, 0.8),
            'valence': (0.2, 0.7),
            'tempo': (80, 140),
            'instrumentalness': (0.3, 1.0)
        },
        'fatigué': {
            'energy': (0.0, 0.5),
            'valence': (0.3, 0.8),
            'tempo': (60, 100),
            'acousticness': (0.4, 1.0)
        }
    }
    
    # Correspondance entre activités et types de musique
    ACTIVITY_TO_GENRES = {
        'courir': ['pop', 'dance', 'electronic', 'hip-hop', 'work-out'],
        'travailler': ['classical', 'jazz', 'lofi', 'ambient', 'focus'],
        'se détendre': ['ambient', 'chill', 'acoustic', 'piano', 'classical'],
        'faire la fête': ['pop', 'dance', 'electronic', 'hip-hop', 'party'],
        'voyager': ['pop', 'indie', 'rock', 'world'],
        'cuisiner': ['jazz', 'soul', 'funk', 'disco']
    }
    
    def __init__(self):
        """Initialise l'analyseur d'humeur."""
        self.detected_mood = None
        self.detected_activity = None
        self.confidence = 0.0
    
    def analyze_mood(self, text: str) -> Tuple[str, float]:
        """Analyse le texte pour détecter l'humeur.
        
        Args:
            text: Texte décrivant l'humeur de l'utilisateur
            
        Returns:
            Tuple (humeur détectée, niveau de confiance)
        """
        if not text:
            return None, 0.0
            
        text = text.lower()
        mood_scores = {mood: 0 for mood in self.MOOD_KEYWORDS}
        
        # Compte les occurrences des mots-clés
        for mood, keywords in self.MOOD_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    mood_scores[mood] += 1
        
        # Trouve l'humeur avec le score le plus élevé
        max_score = max(mood_scores.values())
        if max_score == 0:
            # Aucun mot-clé détecté, on essaie une approche plus simple
            for mood in self.MOOD_KEYWORDS:
                if mood in text:
                    return mood, 0.7  # Confiance moyenne
            return None, 0.0
        
        # Calcule la confiance (normalisée entre 0 et 1)
        total_keywords = sum(len(keywords) for keywords in self.MOOD_KEYWORDS.values())
        confidence = min(max_score / 3, 1.0)  # Au maximum 3 mots-clés par humeur
        
        # Récupère toutes les humeurs avec le score maximum
        top_moods = [mood for mood, score in mood_scores.items() if score == max_score]
        
        # Si plusieurs humeurs ont le même score, on en choisit une au hasard
        detected_mood = random.choice(top_moods)
        
        self.detected_mood = detected_mood
        self.confidence = confidence
        
        return detected_mood, confidence
    
    def analyze_activity(self, text: str) -> Tuple[str, float]:
        """Analyse le texte pour détecter l'activité.
        
        Args:
            text: Texte décrivant l'activité de l'utilisateur
            
        Returns:
            Tuple (activité détectée, niveau de confiance)
        """
        if not text:
            return None, 0.0
            
        text = text.lower()
        
        # Liste des activités possibles avec leurs variations
        activity_variations = {
            'courir': ['courir', 'course', 'jogging', 'running'],
            'travailler': ['travailler', 'boulot', 'travail', 'bureau'],
            'se détendre': ['détente', 'détendre', 'repos', 'reposer', 'relaxer'],
            'faire la fête': ['fête', 'fêter', 'soirée', 'party'],
            'voyager': ['voyage', 'voyager', 'train', 'avion', 'voiture', 'métro', 'bus'],
            'cuisiner': ['cuisine', 'cuisiner', 'repas', 'cuisson', 'cuire']
        }
        
        # Recherche des activités dans le texte
        detected_activities = []
        
        for activity, variations in activity_variations.items():
            for variation in variations:
                if variation in text:
                    detected_activities.append(activity)
                    break  # Pas besoin de vérifier les autres variations
        
        if not detected_activities:
            # Aucune activité détectée, on essaie une détection plus simple
            for activity in activity_variations:
                if activity in text:
                    return activity, 0.7  # Confiance moyenne
            return None, 0.0
        
        # Si plusieurs activités détectées, on choisit la première
        detected_activity = detected_activities[0]
        confidence = min(0.7 + (len(detected_activities) * 0.1), 1.0)  # Plus il y a de correspondances, plus on est confiant
        
        self.detected_activity = detected_activity
        self.confidence = confidence
        
        return detected_activity, confidence
    
    def get_audio_features_for_context(self, mood: str, activity: str) -> Dict[str, tuple]:
        """Retourne les caractéristiques audio recommandées pour le contexte donné.
        
        Args:
            mood: Humeur détectée
            activity: Activité détectée
            
        Returns:
            Dictionnaire des caractéristiques audio avec leurs plages de valeurs
        """
        features = {}
        
        # Ajoute les caractéristiques liées à l'humeur
        if mood in self.MOOD_TO_AUDIO_FEATURES:
            features.update(self.MOOD_TO_AUDIO_FEATURES[mood])
        
        # Ajuste en fonction de l'activité
        if activity == 'courir':
            features.update({
                'energy': (0.7, 1.0),
                'tempo': (120, 180),  # BPM plus élevé pour la course
                'danceability': (0.6, 1.0)
            })
        elif activity == 'travailler':
            features.update({
                'energy': (0.3, 0.7),  # Ni trop calme, ni trop énergique
                'instrumentalness': (0.5, 1.0),  # Moins de paroles pour moins distraire
                'speechiness': (0.0, 0.2)  # Évite les podcasts/musiques avec beaucoup de paroles
            })
        elif activity == 'se détendre':
            features.update({
                'energy': (0.0, 0.4),
                'tempo': (60, 100),
                'acousticness': (0.5, 1.0)
            })
        elif activity == 'voyager':
            # Pour les voyages, on garde une certaine énergie mais on varie plus
            if 'energy' in features:
                features['energy'] = (
                    max(0.4, features['energy'][0]),  # Au moins 0.4
                    min(0.9, features['energy'][1])   # Pas plus de 0.9
                )
            else:
                features['energy'] = (0.4, 0.9)
        
        return features
    
    def get_recommendation_parameters(self, mood: str, activity: str) -> Dict:
        """Retourne les paramètres pour les recommandations Spotify.
        
        Args:
            mood: Humeur détectée
            activity: Activité détectée
            
        Returns:
            Dictionnaire des paramètres pour l'API de recommandation Spotify
        """
        # Obtient les caractéristiques audio de base
        audio_features = self.get_audio_features_for_context(mood, activity)
        
        # Convertit les plages de valeurs en cibles uniques pour l'API Spotify
        params = {}
        
        for feature, (min_val, max_val) in audio_features.items():
            # Pour les paramètres numériques, on prend le milieu de la plage comme cible
            if feature in ['tempo', 'duration_ms']:
                target = (min_val + max_val) / 2
                params[f'target_{feature}'] = target
            else:
                # Pour les autres paramètres (normalisés entre 0 et 1)
                target = (min_val + max_val) / 2
                params[f'target_{feature}'] = round(target, 2)
        
        # Ajoute des genres recommandés en fonction de l'activité
        if activity in self.ACTIVITY_TO_GENRES:
            params['seed_genres'] = ','.join(self.ACTIVITY_TO_GENRES[activity][:2])
        
        return params
    
    def get_playlist_name_for_context(self, mood: str, activity: str) -> str:
        """Génère un nom de playlist adapté au contexte."""
        mood_names = {
            'energique': 'Énergique',
            'calme': 'Calme',
            'triste': 'Mélancolie',
            'heureux': 'Bonne Humeur',
            'stressé': 'Décompression',
            'fatigué': 'Détente'
        }
        
        activity_names = {
            'courir': 'Running',
            'travailler': 'Travail',
            'se détendre': 'Détente',
            'faire la fête': 'Fête',
            'voyager': 'Voyage',
            'cuisiner': 'Cuisine'
        }
        
        mood_name = mood_names.get(mood, 'Ambiance')
        activity_name = activity_names.get(activity, 'Temps Libre')
        
        return f"{mood_name} - {activity_name}"
