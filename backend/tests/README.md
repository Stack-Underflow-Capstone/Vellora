# Tests

This directory contains comprehensive tests for the Vellora backend application.

## Test Structure

```
tests/
├── modules/           # Unit tests (mocked dependencies, fast)
│   ├── expenses/
│   │   ├── test_schemas.py
│   │   ├── test_service.py
│   │   ├── test_repository.py
│   │   └── test_router.py
│   ├── rate_categories/
│   ├── rate_customizations/
│   └── trips/
│       ├── test_schemas.py
│       ├── test_service.py
│       ├── test_repository.py
│       ├── test_router.py
│       ├── test_distance.py 
│       └── test_crypto.py 
├── integration/       # Integration tests (real database, slower)
│   ├── conftest.py   # Test database fixtures (SQLite in-memory)
│   └── test_trip_repository.py
└── conftest.py       # Shared test fixtures
```

## Running Tests

### Install Test Dependencies

```bash
# Install dependencies
pip install -r requirements.txt

```

### Run Unit Tests Only (Fast, Default)

```bash
# Run all unit tests
pytest tests/modules/ -v

# Run specific module unit tests
pytest tests/modules/trips/ -v

# Run with coverage
pytest tests/modules/trips/ --cov=app.modules.trips --cov-report=term-missing
```

### Run Integration Tests (Slower, Requires DB)

```bash
# Run all integration tests
pytest tests/integration/ -v -m integration

# Run specific integration test file
pytest tests/integration/test_trip_repository.py -v

# Skip integration tests when running all tests
pytest -v -m "not integration"
```

### Run All Tests (Unit + Integration)

```bash
# Run everything
pytest -v

# Run with coverage for all modules
pytest --cov=app.modules --cov-report=term-missing

# Run and stop on first failure
pytest -x

# Run with verbose output and show print statements
pytest -v -s
```

## Maintenance

### Adding New Tests
1. Follow existing test structure and naming conventions
2. Use appropriate fixtures from `conftest.py`
3. Mock external dependencies in unit tests
4. Add integration tests for complex database operations
5. Run tests locally before committing