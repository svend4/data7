# Testing Guide - Meta-Orchestrator Switchboard

**Version**: 1.0
**Last Updated**: 2026-02-05

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Test Types](#test-types)
3. [Running Tests](#running-tests)
4. [Test Coverage](#test-coverage)
5. [Writing Tests](#writing-tests)
6. [Load Testing](#load-testing)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

```bash
# Install test dependencies
cd backend
pip install -r requirements-test.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

---

## 🧪 Test Types

### Unit Tests (`tests/unit/`)

Test individual components in isolation.

**Coverage**: 65+ tests, 85-90% coverage

**Files**:
- `test_graph_optimizer.py` - GraphOptimizer service (30+ tests)
- `test_alert_manager.py` - AlertManager service (35+ tests)

**Run**:
```bash
pytest tests/unit/ -v
```

### Integration Tests (`tests/integration/`)

Test API endpoints and component interactions.

**Coverage**: 80+ tests

**Files**:
- `test_api_agents.py` - Agents API
- `test_api_analytics.py` - Analytics API
- `test_api_alerts.py` - Alerts API

**Run**:
```bash
pytest tests/integration/ -v
```

### Load Tests (`tests/load/`)

Performance and stress testing with Locust.

**Scenarios**:
- `MetaOrchestratorUser` - Normal user behavior
- `ReadOnlyUser` - Dashboard viewers
- `HeavyOptimizationUser` - Graph optimization

**Run**:
```bash
locust -f tests/load/locustfile.py --host=http://localhost:8000
# Open http://localhost:8089 in browser
```

---

## 🏃 Running Tests

### Run All Tests

```bash
# All tests with coverage
pytest --cov=app --cov-report=term-missing

# Only unit tests
pytest tests/unit/

# Only integration tests
pytest tests/integration/

# Specific test file
pytest tests/unit/test_graph_optimizer.py

# Specific test
pytest tests/unit/test_graph_optimizer.py::TestGraphAnalysis::test_analyze_linear_graph
```

### Test Options

```bash
# Verbose output
pytest -v

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Run failed tests only
pytest --lf

# Run tests in parallel (faster)
pytest -n auto

# Generate HTML coverage report
pytest --cov=app --cov-report=html

# Generate XML coverage (for CI/CD)
pytest --cov=app --cov-report=xml
```

### Test Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only slow tests
pytest -m slow

# Skip slow tests
pytest -m "not slow"
```

---

## 📊 Test Coverage

### Current Coverage

```
Module                          Coverage
────────────────────────────────────────
app/services/graph_optimizer.py    90%
app/services/alert_manager.py      85%
app/services/metrics_collector.py  80%
app/services/report_generator.py   75%
app/api/                           85%
────────────────────────────────────────
TOTAL                              85%
```

### Coverage Targets

- **Overall**: >80% ✅
- **Services**: >85%
- **APIs**: >80%
- **Critical paths**: 100%

### View Coverage Report

```bash
# Generate HTML report
pytest --cov=app --cov-report=html

# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

# Terminal report
pytest --cov=app --cov-report=term-missing
```

---

## ✍️ Writing Tests

### Unit Test Template

```python
"""
Unit tests for MyService

Tests cover:
- Feature 1
- Feature 2
- Edge cases
"""

import pytest
from app.services.my_service import MyService


class TestMyService:
    """Test MyService functionality."""

    def test_basic_operation(self):
        """Test basic operation."""
        service = MyService()
        result = service.do_something()

        assert result is not None
        assert result.status == "success"

    def test_edge_case(self):
        """Test edge case handling."""
        service = MyService()

        with pytest.raises(ValueError):
            service.do_something_invalid()
```

### Integration Test Template

```python
"""
Integration tests for My API
"""

import pytest
from httpx import AsyncClient


class TestMyAPI:
    """Test My API endpoints."""

    @pytest.mark.asyncio
    async def test_create_resource(self, async_client: AsyncClient):
        """Test creating a resource."""
        response = await async_client.post("/api/resources", json={
            "name": "Test Resource"
        })

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Resource"
        assert "id" in data
```

### Using Fixtures

```python
@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return {"key": "value"}


def test_with_fixture(sample_data):
    """Test using fixture."""
    assert sample_data["key"] == "value"
```

### Async Tests

```python
@pytest.mark.asyncio
async def test_async_operation(async_client):
    """Test async operation."""
    response = await async_client.get("/api/endpoint")
    assert response.status_code == 200
```

---

## 🔥 Load Testing

### Quick Start

```bash
# Install Locust
pip install locust

# Run load test
locust -f tests/load/locustfile.py --host=http://localhost:8000

# Open web UI
open http://localhost:8089
```

### Web UI Configuration

1. Navigate to http://localhost:8089
2. Enter number of users (e.g., 100)
3. Enter spawn rate (e.g., 10 users/second)
4. Click "Start swarming"

### Headless Mode

```bash
# Run without web UI
locust -f tests/load/locustfile.py \
    --host=http://localhost:8000 \
    --users 100 \
    --spawn-rate 10 \
    --run-time 5m \
    --headless

# With HTML report
locust -f tests/load/locustfile.py \
    --host=http://localhost:8000 \
    --users 100 \
    --spawn-rate 10 \
    --run-time 5m \
    --headless \
    --html report.html
```

### Performance Targets

- **Response Time (p95)**: <500ms ✅
- **Response Time (p99)**: <1000ms ✅
- **Throughput**: >100 req/s ✅
- **Error Rate**: <1% ✅

### User Classes

**MetaOrchestratorUser** (Normal operations):
- List agents (weight: 5)
- Create tasks (weight: 4)
- Get analytics (weight: 4)

**ReadOnlyUser** (Dashboard viewers):
- View system health (weight: 10)
- View performance (weight: 5)
- View alerts (weight: 2)

**HeavyOptimizationUser** (Optimization):
- Analyze graph (weight: 5)
- Optimize graph (weight: 3)
- Predict execution (weight: 2)

---

## 🔧 Troubleshooting

### Common Issues

#### Tests Fail Due to Database

```bash
# Ensure test database is clean
pytest --create-db

# Drop and recreate test database
pytest --drop-db --create-db
```

#### Import Errors

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt

# Verify Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### Async Tests Fail

```bash
# Ensure pytest-asyncio is installed
pip install pytest-asyncio

# Check pytest.ini has asyncio_mode = auto
cat pytest.ini | grep asyncio_mode
```

#### Coverage Not Working

```bash
# Install coverage tools
pip install pytest-cov coverage

# Run with coverage
pytest --cov=app --cov-report=term
```

### Debug Mode

```bash
# Run with debugger
pytest --pdb

# Drop into debugger on failure
pytest --pdb -x

# Print output
pytest -s

# Very verbose
pytest -vv
```

### Performance Issues

```bash
# Run tests in parallel
pytest -n auto

# Disable coverage for faster tests
pytest --no-cov

# Run specific slow tests
pytest -m slow --durations=10
```

---

## 📚 Additional Resources

- **pytest documentation**: https://docs.pytest.org/
- **pytest-asyncio**: https://pytest-asyncio.readthedocs.io/
- **Locust documentation**: https://docs.locust.io/
- **httpx documentation**: https://www.python-httpx.org/

---

## 🎯 Best Practices

1. **Test Naming**: Use descriptive names (`test_what_when_expected`)
2. **Arrange-Act-Assert**: Structure tests clearly
3. **Isolation**: Tests should not depend on each other
4. **Fixtures**: Use fixtures for common setup
5. **Mocking**: Mock external services
6. **Coverage**: Aim for >80% overall coverage
7. **Fast Tests**: Keep unit tests fast (<1s each)
8. **Clean Up**: Always clean up resources

---

**Last Updated**: 2026-02-05
**Test Framework**: pytest 7.4.3
**Coverage Target**: >80% ✅
**Current Coverage**: 85% ✅
