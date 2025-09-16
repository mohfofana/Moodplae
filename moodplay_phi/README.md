# MoodPlae - Moteur de recommandation musicale

MoodPlae est un moteur de recommandation musicale intelligent qui s'adapte à l'humeur, au contexte et aux préférences de l'utilisateur.

## Fonctionnalités clés

- **Analyse d'humeur** : Pose des questions pour comprendre comment vous vous sentez
- **Détection d'activité** : S'adapte à ce que vous êtes en train de faire
- **Recommandations personnalisées** : Propose de la musique adaptée à votre état d'esprit
- **Apprentissage continu** : S'améliore avec le temps en apprenant de vos retours

## Structure du projet

### Fichiers principaux
- `__main__.py` - Point d'entrée de l'application
- `recommendation_engine.py` - Générateur de recommandations musicales
- `learning_engine.py` - Système d'apprentissage des préférences utilisateur
- `models/context.py` - Modèles de données pour le contexte utilisateur
- `user_interaction.py` - Gestion des interactions avec l'utilisateur

### Utilitaires
- `utils/sample_data.py` - Données d'exemple pour les tests et démonstrations

### Intégrations
- `integrations/spotify_integration.py` - Client pour l'API Spotify (à implémenter par le 2e développeur)

## Modèle de données

### UserContext
Représente le contexte complet d'un utilisateur, incluant :
- Humeur actuelle (UserMood)
- Activité en cours (ActivityContext)
- Préférences audio (AudioPreferences)
- Contexte temporel et environnemental

### SpotifyTrack
Représente une piste musicale avec ses métadonnées complètes.

## Utilisation

### Lancement de l'application

```bash
# Depuis le répertoire racine
python -m moodplay_phi
```

L'application vous posera alors deux questions clés :
1. Comment vous sentez-vous en ce moment ?
2. Qu'êtes-vous en train de faire ?

### Initialisation du moteur
```python
from moodplay_phi.models.context import UserContext, UserMood, ActivityContext, ActivityType, MoodType
from moodplay_phi.recommendation_engine import RecommendationEngine

# Création d'un contexte utilisateur
user_mood = UserMood(mood_type=MoodType.HAPPY, intensity=0.8)
activity = ActivityContext(activity_type=ActivityType.WORKING, start_time=datetime.utcnow(), device="desktop")
context = UserContext(user_id="user_123", current_mood=user_mood, current_activity=activity)

# Initialisation du moteur de recommandation
engine = RecommendationEngine(context)
```

### Génération de recommandations
```python
# Liste de pistes candidates (à remplacer par des données réelles)
candidate_tracks = [...]

# Génération de recommandations
recommendations = engine.generate_recommendations(candidate_tracks, n=10)
```

### Apprentissage des préférences
```python
from moodplay_phi.learning_engine import LearningEngine

# Initialisation du moteur d'apprentissage
learner = LearningEngine()

# Mise à jour des préférences suite à une interaction
learner.update_from_interaction(
    context=context,
    track_id="track_123",
    track_features={"tempo": 120, "energy": 0.8, "valence": 0.7},
    interaction_type="like"
)
```

## Développement

### Configuration requise
- Python 3.8+
- Bibliothèques listées dans `requirements.txt`

### Structure du flux utilisateur

1. **Collecte du contexte** :
   - L'utilisateur est interrogé sur son humeur et son activité
   - Les réponses sont analysées et transformées en contexte structuré

2. **Génération de recommandations** :
   - Le moteur utilise le contexte pour filtrer et scorer les pistes
   - Les recommandations sont classées par pertinence

3. **Apprentissage** :
   - Les interactions utilisateur sont enregistrées
   - Le modèle de préférences est mis à jour en temps réel

### Installation
1. Cloner le dépôt
2. Créer un environnement virtuel : `python -m venv venv`
3. Activer l'environnement : `source venv/bin/activate` (Linux/Mac) ou `.\venv\Scripts\activate` (Windows)
4. Installer les dépendances : `pip install -r requirements.txt`

### Tests
Pour exécuter les tests :
```bash
pytest tests/
```

## Contribution

### Règles de développement
- Suivre les conventions PEP 8
- Écrire des docstrings complètes
- Ajouter des tests unitaires pour les nouvelles fonctionnalités
- Utiliser des commits atomiques avec des messages clairs

### Workflow Git
1. Créer une branche pour chaque fonctionnalité : `feature/nom-de-la-fonctionnalite`
2. Soumettre une pull request pour réviser le code
3. S'assurer que tous les tests passent avant de merger

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.
