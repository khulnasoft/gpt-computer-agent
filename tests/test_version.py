"""Unit tests for Aideck version module"""

# Add src to path for testing
import sys
from pathlib import Path
from unittest.mock import mock_open, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aideck.version import get_version


class TestVersion:
    """Test cases for version module"""

    def test_get_version_from_init(self):
        """Test getting version from __init__.py file"""
        mock_init_content = "__version__ = '1.2.3'  # fmt: skip\n"

        with patch("builtins.open", mock_open(read_data=mock_init_content)):
            version = get_version()
            assert version == "1.2.3"

    def test_get_version_no_version_line(self):
        """Test get_version when no version line exists"""
        mock_init_content = "# No version here\nsome_other_code = 'test'\n"

        with patch("builtins.open", mock_open(read_data=mock_init_content)):
            version = get_version()
            assert version is None

    def test_get_version_malformed_line(self):
        """Test get_version with malformed version line"""
        mock_init_content = "__version__ = \n"

        with patch("builtins.open", mock_open(read_data=mock_init_content)):
            version = get_version()
            assert version is None

    def test_get_version_with_comment(self):
        """Test get_version with version line containing comment"""
        mock_init_content = "__version__ = '2.0.0'  # fmt: skip\n"

        with patch("builtins.open", mock_open(read_data=mock_init_content)):
            version = get_version()
            assert version == "2.0.0"

    def test_get_version_empty_file(self):
        """Test get_version with empty file"""
        mock_init_content = ""

        with patch("builtins.open", mock_open(read_data=mock_init_content)):
            version = get_version()
            assert version is None

    def test_get_version_multiple_lines(self):
        """Test get_version with multiple lines in file"""
        mock_init_content = """# This is a comment
import os
__version__ = '3.1.0'  # fmt: skip
# Another comment
"""

        with patch("builtins.open", mock_open(read_data=mock_init_content)):
            version = get_version()
            assert version == "3.1.0"
