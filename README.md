# MoodPlae

MoodPlae est un système de recommandation musicale intelligent qui s'adapte à l'humeur et au contexte de l'utilisateur. En utilisant des techniques avancées d'apprentissage automatique et l'API Spotify, MoodPlae crée des playlists personnalisées en temps réel.

## 🌟 Fonctionnalités

- **Recommandations basées sur l'humeur** : Analyse les émotions pour proposer une sélection adaptée
- **Contexte intelligent** : Prend en compte l'heure, la localisation et l'activité
- **Apprentissage continu** : S'améliore avec chaque interaction utilisateur
- **Intégration Spotify** : Synchronisation complète avec votre bibliothèque musicale
- **Architecture performante** : Conçue pour une expérience fluide et réactive

## 🏗️ Structure du Projet

```
moodplae/
├── moodplay_phi/              # Package principal
│   ├── core/                  # Cœur du système de recommandation
│   ├── models/                # Modèles de données
│   ├── services/              # Services métier
│   ├── integrations/          # Intégrations externes
│   │   └── spotify_client.py  # Client Spotify
│   ├── api/                   # Points d'entrée API
│   └── config.py              # Configuration
├── tests/                     # Tests automatisés
│   ├── unit/                  # Tests unitaires
│   ├── integration/           # Tests d'intégration
│   └── performance/           # Tests de performance
├── scripts/                   # Scripts utilitaires
├── .env.example              # Exemple de configuration
├── requirements.txt          # Dépendances
└── README.md                 # Ce fichier
```

## 🚀 Installation

### Prérequis
- Python 3.8+
- Compte développeur Spotify
- Clés d'API Spotify

- Python 3.8+
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/moodplay-phi.git
   cd moodplay-phi
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-test.txt  # For development
   ```

## Usage

### Running Tests

To run all tests:
```bash
pytest
```

To run specific test categories:
```bash
pytest tests/unit/            # Unit tests
pytest tests/integration/     # Integration tests
pytest tests/performance/     # Performance tests
pytest tests/behavioral/      # Behavioral tests
```

### Generating Test Data

```bash
python scripts/generate_test_data.py --num-users 1000 --num-items 10000
```

### Running Simulations

```bash
python scripts/simulate_users.py --num-users 100 --num-sessions 1000
```

### Running Benchmarks

```bash
python scripts/run_benchmarks.py --num-users 1000 --num-items 10000
```

## Development

### Code Style

This project uses:
- **Black** for code formatting
- **isort** for import sorting
- **Flake8** for linting
- **mypy** for static type checking

Run the following commands before committing:
```bash
black .
isort .
flake8
mypy .
```

### Adding New Features

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and write tests

3. Run tests and checks:
   ```bash
   pytest
   black .
   isort .
   flake8
   mypy .
   ```

4. Commit your changes with a descriptive message

5. Push to the branch and create a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all contributors who have helped with this project
- Inspired by modern recommendation system architectures

