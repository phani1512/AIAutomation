# Test Execution Guide

## Quick Start

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories

**Unit Tests Only:**
```bash
pytest src/test/unit/
```

**Integration Tests Only:**
```bash
pytest src/test/integration/
```

**Specific Test File:**
```bash
pytest src/test/unit/test_server.py
```

### Run Tests with Verbose Output
```bash
pytest -v
```

### Run Tests with Coverage
```bash
pytest --cov=src/main/python --cov-report=html
```

## PowerShell Integration Test

The integration test script validates all API endpoints:
```powershell
.\test_integration.ps1
```

This tests:
- API Server health check
- Code generation
- Locator suggestion
- Action suggestion

## Test Structure

```
src/
├── main/
│   └── python/         # Application code
└── test/               # Test files
    ├── __init__.py
    ├── README.md
    ├── unit/           # Unit tests
    │   ├── test_server.py
    │   ├── test_auth.py
    │   └── minimal_test.py
    └── integration/    # Integration tests
        ├── test_browser_conversion.py
        └── demo_direct.py
```

## Adding New Tests

1. Create test file in appropriate directory (unit/ or integration/)
2. Name file with `test_` prefix (e.g., `test_my_feature.py`)
3. Use pytest conventions:
   - Test functions: `def test_something():`
   - Test classes: `class TestSomething:`
   - Assertions: Use standard `assert` statements

Example test:
```python
def test_example():
    result = 2 + 2
    assert result == 4, "Math is broken!"
```

## Continuous Integration

Tests are automatically run in CI/CD pipeline. Ensure all tests pass before committing:
```bash
pytest --tb=short
```
