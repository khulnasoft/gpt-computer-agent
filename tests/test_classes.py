"""Unit tests for Aideck core classes"""

# Add src to path for testing
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aideck.classes import BaseClass, BaseVerifier, Task, TypeVerifier


class TestBaseClass:
    """Test cases for BaseClass"""

    def test_base_class_initialization(self):
        """Test BaseClass can be initialized"""
        base = BaseClass()
        assert base is not None

    def test_base_class_inheritance(self):
        """Test BaseClass inheritance works"""

        class TestClass(BaseClass):
            def __init__(self):
                super().__init__()

        test_instance = TestClass()
        assert test_instance is not None


class TestBaseVerifier:
    """Test cases for BaseVerifier"""

    def test_base_verifier_initialization(self):
        """Test BaseVerifier can be initialized"""
        verifier = BaseVerifier()
        assert verifier is not None

    def test_verifier_inheritance(self):
        """Test BaseVerifier inheritance works"""

        class TestVerifier(BaseVerifier):
            def verify(self, data):
                return True

        test_verifier = TestVerifier()
        assert test_verifier.verify("test") is True


class TestTypeVerifier:
    """Test cases for TypeVerifier"""

    def test_type_verifier_initialization(self):
        """Test TypeVerifier can be initialized"""
        verifier = TypeVerifier()
        assert verifier is not None

    def test_type_verification(self):
        """Test type verification functionality"""

        class TestTypeVerifier(TypeVerifier):
            def verify_type(self, value, expected_type):
                return isinstance(value, expected_type)

        test_verifier = TestTypeVerifier()
        assert test_verifier.verify_type("string", str) is True
        assert test_verifier.verify_type(123, int) is True
        assert test_verifier.verify_type(123, str) is False


class TestTask:
    """Test cases for Task class"""

    def test_task_initialization(self):
        """Test Task can be initialized"""
        task = Task()
        assert task is not None

    def test_task_with_function(self):
        """Test Task with function assignment"""

        def sample_function():
            return "result"

        task = Task()
        task.function = sample_function
        assert task.function is sample_function

    def test_task_execution(self):
        """Test Task execution"""

        def sample_function():
            return "success"

        task = Task()
        task.function = sample_function
        result = task.execute()
        assert result == "success"

    def test_task_with_parameters(self):
        """Test Task with parameters"""

        def add_numbers(a, b):
            return a + b

        task = Task()
        task.function = add_numbers
        result = task.execute(3, 4)
        assert result == 7
