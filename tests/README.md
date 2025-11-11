# Jynco Test Suite

Unit and integration tests for the Jynco video generation system.

## Running Tests

### All Tests
```bash
pytest tests/ -v
```

### Specific Test File
```bash
pytest tests/test_agents.py -v
```

### With Coverage
```bash
pytest tests/ --cov=src --cov-report=html
```

## Test Structure

- `test_agents.py` - Agent functionality tests
- `test_infrastructure.py` - Cache and queue tests (TODO)
- `test_schemas.py` - Schema validation tests (TODO)
- `test_integration.py` - End-to-end workflow tests (TODO)

## Test Categories

### Unit Tests
Test individual agent methods and functionality in isolation.

### Integration Tests
Test complete workflows with multiple agents working together.

### Performance Tests
Measure parallel execution performance and resource usage.

## Writing Tests

Example test structure:
```python
@pytest.mark.asyncio
async def test_my_feature(temp_dir):
    agent = MyAgent(config={...})
    result = await agent.execute({...})
    assert result["success"] is True
```

## Fixtures

- `temp_dir` - Provides temporary directory for test files
- More fixtures coming soon...
