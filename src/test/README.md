# Test Organization

This directory contains all test files for the WebAutomation framework.

## Structure

- **unit/** - Unit tests for individual components
  - `test_server.py` - API server endpoint tests
  - `test_auth.py` - Authentication tests
  - `minimal_test.py` - Minimal test cases

- **integration/** - Integration tests
  - `test_browser_conversion.py` - Browser automation conversion tests
  - `demo_direct.py` - Direct browser integration demos

## Running Tests

### Run all tests:
```bash
pytest tests/
```

### Run unit tests only:
```bash
pytest tests/unit/
```

### Run integration tests only:
```bash
pytest tests/integration/
```

### Run specific test file:
```bash
pytest tests/unit/test_server.py
```

## Test Requirements

Make sure you have the required testing dependencies:
```bash
pip install pytest pytest-cov
```
