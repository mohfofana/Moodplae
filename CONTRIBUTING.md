# Guide de Contribution pour MoodPlae

Merci de contribuer à MoodPlae ! Voici comment vous pouvez vous impliquer.

## Environnement de Développement

### Prérequis
- Python 3.8+
- Poetry (gestion des dépendances)
- Git

### Installation

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/votre-utilisateur/moodplae.git
   cd moodplae
   ```

2. **Configurer l'environnement virtuel**
   ```bash
   poetry install
   ```

3. **Configurer les variables d'environnement**
   ```bash
   cp .env.example .env
   # Éditer .env avec vos configurations
   ```

## Flux de Travail Git

1. **Créer une branche**
   ```bash
   git checkout -b feature/nom-de-la-fonctionnalite
   ```

2. **Faire des commits atomiques**
   ```bash
   git add .
   git commit -m "feat: ajouter une nouvelle fonctionnalité"
   ```

3. **Pousser les changements**
   ```bash
   git push origin feature/nom-de-la-fonctionnalite
   ```

4. **Créer une Pull Request**
   - Aller sur GitHub
   - Créer une PR depuis votre branche vers `develop`
   - Ajouter une description claire
   - Assigner un relecteur

## Standards de Code

### Formatage
- Utiliser Black pour le formatage
- Maximum 120 caractères par ligne
- Docstrings en Google style

### Tests
- Écrire des tests pour le nouveau code
- Exécuter les tests avant de pousser :
  ```bash
  poetry run pytest
  ```

### Documentation
- Documenter toute nouvelle fonctionnalité
- Mettre à jour le README si nécessaire

## Structure du Projet

```
moodplay_phi/
├── core/                  # Cœur du système de recommandation
├── models/               # Modèles de données
├── services/             # Services métier
├── integrations/         # Intégrations externes (Spotify, etc.)
├── api/                  # Points d'entrée API
└── tests/                # Tests automatisés
```

## Bonnes Pratiques

1. **Branches**
   - `main` : Version stable
   - `develop` : Branche d'intégration
   - `feature/*` : Nouvelles fonctionnalités
   - `bugfix/*` : Corrections de bugs

2. **Messages de Commit**
   - Utiliser le format conventionnel :
     - `feat:` pour les nouvelles fonctionnalités
     - `fix:` pour les corrections de bugs
     - `docs:` pour la documentation
     - `refactor:` pour les refactorisations
     - `test:` pour les tests
     - `chore:` pour les tâches de maintenance

3. **Revues de Code**
   - Toujours faire relire son code
   - Être constructif dans les commentaires
   - Résoudre les discussions avant de merger

## Questions ?

Pour toute question, ouvrez une issue ou contactez l'équipe de développement.
