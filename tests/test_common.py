"""Unit tests for Aideck common utilities"""

import json
import os

# Add src to path for testing
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aideck.utils.common import (
    calculate_checksum,
    ensure_directory,
    format_bytes,
    get_environment_info,
    get_file_extension,
    get_timestamp,
    is_url,
    load_config,
    save_config,
)


class TestLoadConfig:
    """Test cases for load_config function"""

    def test_load_json_config(self):
        """Test loading JSON configuration"""
        test_config = {"key": "value", "number": 42}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(test_config, f)
            temp_file = f.name

        try:
            result = load_config(temp_file)
            assert result == test_config
        finally:
            os.unlink(temp_file)

    def test_load_yaml_config(self):
        """Test loading YAML configuration"""
        test_config = {"key": "value", "number": 42}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_config, f)
            temp_file = f.name

        try:
            result = load_config(temp_file)
            assert result == test_config
        finally:
            os.unlink(temp_file)

    def test_load_nonexistent_file(self):
        """Test loading non-existent file raises error"""
        with pytest.raises(FileNotFoundError):
            load_config("nonexistent_file.json")

    def test_load_unsupported_format(self):
        """Test loading unsupported file format"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("some text")
            temp_file = f.name

        try:
            with pytest.raises(ValueError, match="Unsupported config file format"):
                load_config(temp_file)
        finally:
            os.unlink(temp_file)


class TestSaveConfig:
    """Test cases for save_config function"""

    def test_save_json_config(self):
        """Test saving JSON configuration"""
        test_config = {"key": "value", "number": 42}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_file = f.name

        try:
            save_config(test_config, temp_file)

            with open(temp_file) as f:
                saved_config = json.load(f)

            assert saved_config == test_config
        finally:
            os.unlink(temp_file)

    def test_save_yaml_config(self):
        """Test saving YAML configuration"""
        test_config = {"key": "value", "number": 42}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            temp_file = f.name

        try:
            save_config(test_config, temp_file)

            with open(temp_file) as f:
                saved_config = yaml.safe_load(f)

            assert saved_config == test_config
        finally:
            os.unlink(temp_file)


class TestGetTimestamp:
    """Test cases for get_timestamp function"""

    def test_get_timestamp_default_format(self):
        """Test get_timestamp with default format"""
        timestamp = get_timestamp()
        # Should be in YYYYMMDD_HHMMSS format
        assert len(timestamp) == 15
        assert timestamp[8] == "_"

    def test_get_timestamp_custom_format(self):
        """Test get_timestamp with custom format"""
        custom_format = "%Y-%m-%d %H:%M:%S"
        timestamp = get_timestamp(custom_format)

        # Try to parse it back
        parsed = datetime.strptime(timestamp, custom_format)
        assert isinstance(parsed, datetime)


class TestIsUrl:
    """Test cases for is_url function"""

    def test_valid_https_url(self):
        """Test valid HTTPS URL"""
        assert is_url("https://www.example.com") is True

    def test_valid_http_url(self):
        """Test valid HTTP URL"""
        assert is_url("http://example.com") is True

    def test_invalid_url_no_scheme(self):
        """Test URL without scheme"""
        assert is_url("www.example.com") is False

    def test_invalid_url_no_netloc(self):
        """Test URL without netloc"""
        assert is_url("https://") is False

    def test_invalid_url_malformed(self):
        """Test malformed URL"""
        assert is_url("not-a-url") is False

    def test_empty_string(self):
        """Test empty string"""
        assert is_url("") is False


class TestCalculateChecksum:
    """Test cases for calculate_checksum function"""

    def test_calculate_checksum_sha256(self):
        """Test checksum calculation with SHA256"""
        # Create a test file
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as f:
            test_data = b"Hello, World!"
            f.write(test_data)
            temp_file = f.name

        try:
            checksum = calculate_checksum(temp_file, "sha256")
            assert len(checksum) == 64  # SHA256 produces 64 character hex string
            assert checksum.isalnum()
        finally:
            os.unlink(temp_file)

    def test_calculate_checksum_md5(self):
        """Test checksum calculation with MD5"""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as f:
            test_data = b"Hello, World!"
            f.write(test_data)
            temp_file = f.name

        try:
            checksum = calculate_checksum(temp_file, "md5")
            assert len(checksum) == 32  # MD5 produces 32 character hex string
            assert checksum.isalnum()
        finally:
            os.unlink(temp_file)

    def test_calculate_checksum_nonexistent_file(self):
        """Test checksum calculation with non-existent file"""
        with pytest.raises(FileNotFoundError):
            calculate_checksum("nonexistent_file.txt")

    def test_calculate_checksum_unsupported_algorithm(self):
        """Test checksum calculation with unsupported algorithm"""
        with tempfile.NamedTemporaryFile() as f:
            temp_file = f.name

        with pytest.raises(ValueError, match="Unsupported hash algorithm"):
            calculate_checksum(temp_file, "unsupported_algorithm")


class TestEnsureDirectory:
    """Test cases for ensure_directory function"""

    def test_ensure_existing_directory(self):
        """Test ensure_directory with existing directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = ensure_directory(temp_dir)
            assert result == Path(temp_dir)
            assert result.exists()
            assert result.is_dir()

    def test_ensure_new_directory(self):
        """Test ensure_directory with new directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = Path(temp_dir) / "new_directory"
            result = ensure_directory(new_dir)
            assert result == new_dir
            assert result.exists()
            assert result.is_dir()

    def test_ensure_nested_directories(self):
        """Test ensure_directory with nested directories"""
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_dir = Path(temp_dir) / "level1" / "level2" / "level3"
            result = ensure_directory(nested_dir)
            assert result == nested_dir
            assert result.exists()
            assert result.is_dir()


class TestGetFileExtension:
    """Test cases for get_file_extension function"""

    def test_get_extension_with_dot(self):
        """Test get_file_extension with dotted extension"""
        assert get_file_extension("file.txt") == "txt"

    def test_get_extension_without_dot(self):
        """Test get_file_extension without dot"""
        assert get_file_extension("file") == ""

    def test_get_extension_multiple_dots(self):
        """Test get_file_extension with multiple dots"""
        assert get_file_extension("file.tar.gz") == "gz"

    def test_get_extension_case_insensitive(self):
        """Test get_file_extension is case insensitive"""
        assert get_file_extension("file.TXT") == "txt"

    def test_get_extension_empty_string(self):
        """Test get_file_extension with empty string"""
        assert get_file_extension("") == ""


class TestFormatBytes:
    """Test cases for format_bytes function"""

    def test_format_bytes_zero(self):
        """Test format_bytes with zero bytes"""
        assert format_bytes(0) == "0.0 B"

    def test_format_bytes_bytes(self):
        """Test format_bytes with bytes"""
        assert format_bytes(512) == "512.0 B"

    def test_format_bytes_kilobytes(self):
        """Test format_bytes with kilobytes"""
        assert format_bytes(1536) == "1.5 KB"

    def test_format_bytes_megabytes(self):
        """Test format_bytes with megabytes"""
        assert format_bytes(1048576) == "1.0 MB"

    def test_format_bytes_gigabytes(self):
        """Test format_bytes with gigabytes"""
        assert format_bytes(1073741824) == "1.0 GB"

    def test_format_bytes_terabytes(self):
        """Test format_bytes with terabytes"""
        assert format_bytes(1099511627776) == "1.0 TB"

    def test_format_bytes_petabytes(self):
        """Test format_bytes with petabytes"""
        assert format_bytes(1125899906842624) == "1.0 PB"


class TestGetEnvironmentInfo:
    """Test cases for get_environment_info function"""

    def test_get_environment_info_structure(self):
        """Test get_environment_info returns expected structure"""
        info = get_environment_info()

        expected_keys = [
            "platform",
            "platform_release",
            "platform_version",
            "architecture",
            "python_version",
            "python_implementation",
            "python_compiler",
            "working_directory",
            "executable",
            "pid",
            "cpu_count",
            "user",
            "home",
        ]

        for key in expected_keys:
            assert key in info
            assert info[key] is not None

    def test_get_environment_info_types(self):
        """Test get_environment_info returns correct types"""
        info = get_environment_info()

        assert isinstance(info["platform"], str)
        assert isinstance(info["cpu_count"], int)
        assert isinstance(info["pid"], int)
