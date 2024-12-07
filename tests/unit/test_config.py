"""Test cases for the Config class."""

import json
from pathlib import Path

import pytest

from openapi_cli_generator.config import Config


def test_config_creation(temp_config_dir, monkeypatch):
    """Test configuration file creation."""
    monkeypatch.setattr(Path, "home", lambda: temp_config_dir.parent)

    config = Config()
    assert config.config_file.exists()
    assert config.config == {"aliases": {}}


def test_add_alias(temp_config_dir, monkeypatch):
    """Test adding an alias."""
    monkeypatch.setattr(Path, "home", lambda: temp_config_dir.parent)

    config = Config()
    config.add_alias("test", "http://example.com/api.json")

    # Verify alias was added
    assert config.config["aliases"]["test"] == "http://example.com/api.json"

    # Verify file was updated
    with open(config.config_file) as f:
        saved_config = json.load(f)
    assert saved_config["aliases"]["test"] == "http://example.com/api.json"

    # Test adding duplicate alias
    with pytest.raises(ValueError):
        config.add_alias("test", "http://example.com/other.json")


def test_get_alias(temp_config_dir, monkeypatch):
    """Test retrieving an alias."""
    monkeypatch.setattr(Path, "home", lambda: temp_config_dir.parent)

    config = Config()
    config.add_alias("test", "http://example.com/api.json")

    # Test getting existing alias
    assert config.get_alias("test") == "http://example.com/api.json"

    # Test getting non-existent alias
    with pytest.raises(KeyError):
        config.get_alias("nonexistent")


def test_list_aliases(temp_config_dir, monkeypatch):
    """Test listing all aliases."""
    monkeypatch.setattr(Path, "home", lambda: temp_config_dir.parent)

    config = Config()
    config.add_alias("test1", "http://example.com/api1.json")
    config.add_alias("test2", "http://example.com/api2.json")

    aliases = config.list_aliases()
    assert len(aliases) == 2
    assert aliases["test1"] == "http://example.com/api1.json"
    assert aliases["test2"] == "http://example.com/api2.json"


def test_remove_alias(temp_config_dir, monkeypatch):
    """Test removing an alias."""
    monkeypatch.setattr(Path, "home", lambda: temp_config_dir.parent)

    config = Config()
    config.add_alias("test", "http://example.com/api.json")

    # Test removing existing alias
    config.remove_alias("test")
    assert "test" not in config.config["aliases"]

    # Test removing non-existent alias
    with pytest.raises(KeyError):
        config.remove_alias("nonexistent")


def test_update_alias(temp_config_dir, monkeypatch):
    """Test updating an alias."""
    monkeypatch.setattr(Path, "home", lambda: temp_config_dir.parent)

    config = Config()
    config.add_alias("test", "http://example.com/api.json")

    # Test updating existing alias
    config.update_alias("test", "http://example.com/new.json")
    assert config.get_alias("test") == "http://example.com/new.json"

    # Test updating non-existent alias
    with pytest.raises(KeyError):
        config.update_alias("nonexistent", "http://example.com/api.json")


def test_config_file_permissions(temp_config_dir, monkeypatch):
    """Test configuration file permissions and error handling."""
    monkeypatch.setattr(Path, "home", lambda: temp_config_dir.parent)

    config = Config()
    config.add_alias("test", "http://example.com/api.json")

    # Test read-only config file
    config.config_file.chmod(0o444)
    with pytest.raises(PermissionError):
        config.add_alias("test2", "http://example.com/api2.json")


def test_invalid_config_file(temp_config_dir, monkeypatch):
    """Test handling of invalid configuration file."""
    monkeypatch.setattr(Path, "home", lambda: temp_config_dir.parent)

    # Create invalid JSON in config file
    config_file = temp_config_dir / "config.json"
    config_file.write_text("invalid json")

    with pytest.raises(json.JSONDecodeError):
        Config()
