"""Unit tests for Aideck folder utilities"""

import os

# Add src to path for testing
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aideck.utils.folder import artifacts_dir, currently_dir, media_dir


class TestFolderUtils:
    """Test cases for folder utilities"""

    def test_currently_dir_type(self):
        """Test currently_dir is a string"""
        assert isinstance(currently_dir, str)
        assert len(currently_dir) > 0

    def test_artifacts_dir_type(self):
        """Test artifacts_dir is a string"""
        assert isinstance(artifacts_dir, str)
        assert len(artifacts_dir) > 0

    def test_media_dir_type(self):
        """Test media_dir is a string"""
        assert isinstance(media_dir, str)
        assert len(media_dir) > 0

    def test_directories_exist(self):
        """Test that the directories exist"""
        assert os.path.exists(artifacts_dir)
        assert os.path.exists(media_dir)

    def test_directories_are_absolute(self):
        """Test that directory paths are absolute"""
        assert os.path.isabs(artifacts_dir)
        assert os.path.isabs(media_dir)

    def test_artifacts_dir_contains_currently_dir(self):
        """Test artifacts_dir contains currently_dir"""
        assert currently_dir in artifacts_dir

    def test_media_dir_contains_currently_dir(self):
        """Test media_dir contains currently_dir"""
        assert currently_dir in media_dir

    def test_artifacts_dir_structure(self):
        """Test artifacts_dir has correct structure"""
        expected_suffix = os.path.join("utils", "artifacts")
        assert artifacts_dir.endswith(expected_suffix)

    def test_media_dir_structure(self):
        """Test media_dir has correct structure"""
        expected_suffix = os.path.join("utils", "media")
        assert media_dir.endswith(expected_suffix)
