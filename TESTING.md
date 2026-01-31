# Aideck Unit Testing Guide

## 🧪 Unit Testing Setup Complete!

I've successfully set up a comprehensive unit testing framework for the Aideck project with the following components:

### ✅ **Test Structure Created:**

#### **1. Test Configuration:**
- **`tests/conftest.py`** - Test fixtures and configuration
- **`pytest.ini`** - Pytest configuration with markers and settings
- **`tests/data/`** - Test data files (JSON, YAML, text files)
- **`tests/fixtures/`** - Test fixtures directory

#### **2. Unit Test Files:**
- **`tests/test_classes.py`** - Tests for core classes (BaseClass, BaseVerifier, TypeVerifier, Task)
- **`tests/test_version.py`** - Tests for version module
- **`tests/test_common.py`** - Tests for utility functions (config loading, timestamps, URLs, checksums, etc.)
- **`tests/test_api.py`** - Tests for API endpoints
- **`tests/test_folder.py`** - Tests for folder utilities

#### **3. Test Runner:**
- **`run_tests.py`** - Comprehensive test runner script with options for:
  - Coverage reporting
  - Test filtering
  - Debug mode
  - Different output formats

### 🏃‍♂️ **How to Run Tests:**

#### **Run All Tests:**
```bash
python run_tests.py
```

#### **Run Specific Test Files:**
```bash
python run_tests.py tests/test_version.py tests/test_common.py
```

#### **Run with Coverage:**
```bash
python run_tests.py --coverage --cov-report html
```

#### **Run Specific Test Types:**
```bash
# Run only unit tests
python run_tests.py -m unit

# Run only API tests
python run_tests.py -m api

# Run only slow tests
python run_tests.py -m slow
```

#### **Run with Filtering:**
```bash
# Run tests containing "config" in the name
python run_tests.py -k config

# Run tests in a specific file
python run_tests.py tests/test_api.py
```

### 🏗️ **Test Categories:**

#### **Unit Tests** (Fast, Isolated):
- Core classes functionality
- Utility functions
- Version module
- Folder utilities
- Configuration loading/saving

#### **API Tests** (Integration):
- Endpoint functionality
- Request/response handling
- Error handling
- CORS headers
- JSON validation

#### **Test Markers Available:**
```python
@pytest.mark.unit        # Unit tests
@pytest.mark.integration # Integration tests
@pytest.mark.api         # API tests
@pytest.mark.slow        # Slow running tests
```

### 📊 **Test Coverage:**

The test suite covers:
- ✅ **Core Classes** - BaseClass, BaseVerifier, TypeVerifier, Task
- ✅ **Utilities** - Common functions, config handling, file operations
- ✅ **Version Module** - Version extraction and parsing
- ✅ **API Endpoints** - REST API functionality
- ✅ **Error Handling** - Exception cases and edge conditions
- ✅ **Data Validation** - Input validation and type checking

### 🔧 **Test Data:**

#### **Sample Files Created:**
- `tests/data/sample_config.json` - JSON configuration test data
- `tests/data/sample_config.yaml` - YAML configuration test data
- `tests/data/test_checksum.txt` - File for checksum testing

#### **Test Fixtures:**
- Temporary directories and files
- Sample configuration objects
- Mock data for API testing
- Environment information fixtures

### 📈 **Test Configuration:**

#### **Pytest Settings:**
- AsyncIO mode: strict
- Verbose output with colors
- Short traceback format
- Warning filters
- Custom test markers

#### **Coverage Settings:**
- Source code coverage tracking
- HTML, XML, and JSON report formats
- Branch and line coverage

### 🚀 **Next Steps:**

1. **Install test dependencies** (if needed):
   ```bash
   .venv/bin/pip install pytest pytest-asyncio pytest-cov
   ```

2. **Run the test suite**:
   ```bash
   python run_tests.py
   ```

3. **Add tests for new features** using the established patterns

4. **Set up CI/CD integration** with the GitHub workflows

### 📝 **Writing New Tests:**

#### **Example Test Structure:**
```python
import pytest
from pathlib import Path

# Add src to path for testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aideck.module import function_to_test

class TestNewFeature:
    """Test cases for new feature"""

    def test_basic_functionality(self):
        """Test basic functionality"""
        result = function_to_test()
        assert result is not None

    def test_edge_cases(self):
        """Test edge cases and error conditions"""
        with pytest.raises(ValueError):
            function_to_test(invalid_input)
```

### 🎯 **Test Best Practices:**

- **Use descriptive test names** that explain what is being tested
- **Test both positive and negative cases**
- **Use fixtures** for reusable test data
- **Mock external dependencies** for unit tests
- **Keep tests focused** on single functionality
- **Use appropriate markers** for test categorization

The unit testing framework is now ready for comprehensive testing of the Aideck project! 🎉
