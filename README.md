# MoodPlay Phi

MoodPlay Phi is a sophisticated recommendation system designed to provide personalized content suggestions based on user mood, preferences, and contextual information. The system uses a combination of collaborative filtering, content-based filtering, and contextual bandits to deliver highly relevant recommendations.

## Features

- **Mood-based Recommendations**: Tailors suggestions based on the user's current mood
- **Context-Aware**: Considers time of day, location, and device context
- **Personalization**: Learns from user interactions to improve recommendations
- **Scalable Architecture**: Designed to handle large numbers of users and items
- **Comprehensive Testing**: Includes unit, integration, performance, and behavioral tests

## Project Structure

```
moodplay_phi/
├── moodplay_phi/               # Main package
│   ├── __init__.py             # Package initialization
│   ├── core.py                 # Main recommendation algorithm
│   ├── models/                 # Data models
│   │   ├── __init__.py
│   │   ├── context.py          # Context field definitions
│   │   ├── user_state.py       # User state management
│   │   └── scoring.py          # Scoring functions
│   └── utils/                  # Utility functions
│       ├── __init__.py
│       ├── data_gen.py         # Synthetic data generation
│       └── metrics.py          # Evaluation metrics
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── conftest.py             # Test configuration
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   ├── performance/            # Performance tests
│   └── behavioral/             # Behavioral tests
├── data/                       # Data files
│   └── .gitkeep
├── scripts/                    # Utility scripts
│   ├── generate_test_data.py   # Generate test data
│   ├── run_benchmarks.py       # Run performance benchmarks
│   └── simulate_users.py       # Simulate user interactions
├── requirements.txt            # Production dependencies
├── requirements-test.txt       # Development dependencies
├── pytest.ini                 # Pytest configuration
└── README.md                  # This file
```

## Getting Started

### Prerequisites

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
