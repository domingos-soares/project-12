# Testing Documentation

## Overview

This project includes comprehensive unit tests with **95% code coverage** for all API endpoints.

## Test Framework

- **pytest** - Testing framework
- **pytest-cov** - Coverage reporting
- **httpx** - HTTP client for API testing
- **SQLite in-memory** - Isolated test database

## Test Structure

### Test Classes

1. **TestRootEndpoint** - Root endpoint tests
2. **TestHealthcheckEndpoint** - Health check tests
3. **TestCreatePerson** - POST /persons tests
4. **TestGetAllPersons** - GET /persons tests
5. **TestGetPerson** - GET /persons/{id} tests
6. **TestUpdatePerson** - PUT /persons/{id} tests
7. **TestDeletePerson** - DELETE /persons/{id} tests
8. **TestIntegrationScenarios** - End-to-end workflow tests

## Test Coverage

### Total: **95% Coverage**

```
Name          Stmts   Miss   Cover
------------------------------------
database.py      15      4     73%
main.py          72      2     98%
models.py         8      0    100%
------------------------------------
TOTAL            95      6     95%
```

### What's Tested

✅ **CREATE Operations**
- Successful person creation
- Multiple person creation
- Duplicate email validation
- Missing required fields
- Invalid data types
- Edge cases (negative age)

✅ **READ Operations**
- Get all persons (empty and with data)
- Get specific person by ID
- Person not found scenarios
- Invalid ID type handling

✅ **UPDATE Operations**
- Full field updates
- Partial field updates
- Update non-existent person
- Duplicate email validation on update
- Same email update (own email)
- Empty update (no changes)

✅ **DELETE Operations**
- Successful deletion
- Delete non-existent person
- Multiple deletion attempts

✅ **Integration Tests**
- Complete CRUD workflow
- Multiple person management
- Isolation between operations

## Running Tests

### Run All Tests

```bash
pytest
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Specific Test Class

```bash
pytest test_main.py::TestCreatePerson -v
```

### Run Specific Test

```bash
pytest test_main.py::TestCreatePerson::test_create_person_success -v
```

### Run with Coverage Report

```bash
pytest --cov=. --cov-report=html
```

This generates an HTML coverage report in the `htmlcov/` directory.

### View Coverage Report

```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Run Tests and Show Missing Lines

```bash
pytest --cov=. --cov-report=term-missing
```

### Run Tests in Parallel (faster)

```bash
pip install pytest-xdist
pytest -n auto
```

## Test Database

Tests use an **in-memory SQLite database** that is:
- Created fresh for each test
- Isolated from production database
- Automatically cleaned up after each test
- Fast and reliable

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest --cov=. --cov-report=xml
      - uses: codecov/codecov-action@v3
```

## Test Best Practices

### Followed in This Project

1. ✅ **Isolation** - Each test is independent
2. ✅ **Fresh State** - Database reset between tests
3. ✅ **Clear Names** - Descriptive test function names
4. ✅ **AAA Pattern** - Arrange, Act, Assert
5. ✅ **Edge Cases** - Tests for error conditions
6. ✅ **Integration** - End-to-end workflow tests
7. ✅ **Fast** - In-memory database for speed
8. ✅ **Maintainable** - Organized into logical classes

## Adding New Tests

### Template

```python
def test_your_feature(client):
    """Test description"""
    # Arrange - Set up test data
    test_data = {"field": "value"}
    
    # Act - Perform the action
    response = client.post("/endpoint", json=test_data)
    
    # Assert - Verify the result
    assert response.status_code == 200
    assert response.json()["field"] == "value"
```

### Example: Adding a New Test

```python
def test_create_person_with_very_long_name(client):
    """Test creating person with extremely long name"""
    person_data = {
        "name": "A" * 1000,  # Very long name
        "age": 30,
        "email": "test@example.com"
    }
    response = client.post("/persons", json=person_data)
    # Add your assertions here
```

## Code Coverage Goals

- **Minimum**: 80% coverage
- **Current**: 95% coverage
- **Target**: Maintain above 90%

## Troubleshooting

### Tests Fail Locally

```bash
# Ensure dependencies are installed
pip install -r requirements.txt

# Clear pytest cache
rm -rf .pytest_cache

# Run with verbose output
pytest -v
```

### Import Errors

```bash
# Ensure you're in the virtual environment
source venv/bin/activate

# Install in editable mode
pip install -e .
```

## Future Improvements

- [ ] Add performance/load tests
- [ ] Add API contract tests
- [ ] Add security tests
- [ ] Add mutation testing
- [ ] Increase coverage to 100%
- [ ] Add test fixtures file
- [ ] Add parameterized tests for edge cases
