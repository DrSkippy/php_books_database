# Unit Tests for bookdbtool

This directory contains comprehensive unit tests for the bookdbtool package.

> **For comprehensive testing workflows and Makefile integration**, see:
> `../README.md#testing` - Main documentation with complete testing procedures

## Test Coverage

The test suite covers all major modules in the bookdbtool package:

- **test_book_db_tools.py** - Tests for BCTool class (book database operations)
- **test_ai_tools.py** - Tests for OllamaAgent class (AI chat agent)
- **test_estimate_tools.py** - Tests for ESTTool class (reading estimates)
- **test_isbn_lookup_tools.py** - Tests for ISBNLookup class (ISBN lookups)
- **test_visualization_tools.py** - Tests for visualization functions

## Running the Tests

### Run all tests

```bash
poetry run python -m unittest discover -s test -p "test_*.py" -v
```

### Run a specific test file

```bash
poetry run python -m unittest test.test_book_db_tools -v
```

### Run a specific test class

```bash
poetry run python -m unittest test.test_book_db_tools.TestBCTool -v
```

### Run a specific test method

```bash
poetry run python -m unittest test.test_book_db_tools.TestBCTool.test_init -v
```

## Test Statistics

- Total test methods: 124+
- Test coverage includes:
  - Unit tests for all public methods
  - Tests for method aliases
  - Integration tests
  - Edge case tests
  - Error handling tests

## Dependencies

Tests use the following:
- `unittest` - Python's built-in testing framework
- `unittest.mock` - For mocking HTTP requests and external dependencies
- `pandas`, `numpy` - For data manipulation testing
- `matplotlib` - For visualization testing

All dependencies are managed via Poetry and defined in `pyproject.toml`.

## Test Structure

Each test file follows this pattern:

1. **Setup** - Initialize test fixtures and mock data
2. **Unit Tests** - Test individual methods in isolation
3. **Integration Tests** - Test interactions between components
4. **Edge Cases** - Test boundary conditions and error scenarios
5. **Aliases** - Test method shortcuts/aliases

## Notes

- Tests use mocking extensively to avoid making actual HTTP requests
- Visualization tests mock `plt.show()` to prevent display windows
- Some tests verify print output using `StringIO`
- All tests are designed to run independently without external dependencies
