# Testing MoodPlay Phi

This document provides instructions for running tests and simulations for the MoodPlay Phi recommendation system.

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-test.txt
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

## Running Tests

### Unit Tests
Run all unit tests:
```bash
pytest tests/unit/ -v
```

### Integration Tests
Run all integration tests:
```bash
pytest tests/integration/ -v
```

### Performance Tests
Run performance benchmarks:
```bash
pytest tests/performance/ -v --benchmark-only
```

### Test Coverage
Generate a coverage report:
```bash
pytest --cov=moodplay_phi --cov-report=html
open htmlcov/index.html  # View the coverage report
```

## Generating Test Data

1. Generate synthetic data:
   ```bash
   python scripts/generate_test_data.py --output-dir data/synthetic --num-items 1000 --num-users 100
   ```

2. This will create:
   - `data/synthetic/items_<timestamp>.json`
   - `data/synthetic/users_<timestamp>.json`

## Running Simulations

Simulate user interactions with the recommendation system:

```bash
python scripts/simulate_user_interactions.py \
  --items-file data/synthetic/items_<timestamp>.json \
  --output-dir data/simulations \
  --num-users 100 \
  --sessions-per-user 10
```

This will generate a simulation results file in the specified output directory.

## Test Organization

- `tests/unit/`: Unit tests for individual components
- `tests/integration/`: Tests for component interactions
- `tests/performance/`: Performance benchmarks
- `tests/behavioral/`: Tests for system behavior
- `tests/conftest.py`: Shared test fixtures

## Writing Tests

When adding new features, please add corresponding tests following these guidelines:

1. Test files should be named `test_*.py`
2. Test functions should start with `test_`
3. Use fixtures for common test data
4. Include docstrings explaining what each test verifies
5. Use parameterized tests for testing multiple inputs

## Continuous Integration

Tests are automatically run on pull requests via GitHub Actions. The CI pipeline includes:

- Unit tests
- Integration tests
- Code coverage reporting
- Type checking
- Linting

## Debugging Tests

To debug a specific test:

```bash
pytest tests/unit/test_example.py::test_specific -v --pdb
```

This will drop into the Python debugger when a test fails.
