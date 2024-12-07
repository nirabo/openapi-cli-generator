"""OpenAPI CLI configuration management.

This module provides a class for managing OpenAPI CLI configuration,
including adding, updating, and removing API aliases.
"""

import json
import os
from pathlib import Path


class Config:
    """Configuration manager for the OpenAPI CLI generator."""

    def __init__(self):
        """Initialize configuration."""
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / "config.json"
        self.config = self._load_config()

    def _get_config_dir(self):
        """Get configuration directory path."""
        config_dir = os.getenv("OPENAPI_CLI_CONFIG_DIR")
        if config_dir:
            path = Path(config_dir)
        else:
            path = Path.home() / ".openapi_cli_generator"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _load_config(self):
        """Load configuration from file."""
        if not self.config_file.exists():
            self._create_default_config()
        try:
            with self.config_file.open() as f:
                return json.load(f)
        except json.JSONDecodeError:
            raise

    def _create_default_config(self):
        """Create default configuration file."""
        default_config = {"aliases": {}}
        with self.config_file.open("w") as f:
            json.dump(default_config, f, indent=2)
        self.config_file.chmod(0o600)

    def _save_config(self):
        """Save configuration to file."""
        with self.config_file.open("w") as f:
            json.dump(self.config, f, indent=2)

    def add_alias(self, name, url):
        """Add a new API alias."""
        if name in self.config["aliases"]:
            raise ValueError(
                f"Alias '{name}' already exists. Use update_alias to modify it."
            )
        self.config["aliases"][name] = url
        self._save_config()

    def get_alias(self, name):
        """Get URL for an alias."""
        if name not in self.config["aliases"]:
            raise KeyError(f"Alias '{name}' not found.")
        return self.config["aliases"][name]

    def update_alias(self, name, url):
        """Update an existing alias."""
        if name not in self.config["aliases"]:
            raise KeyError(f"Alias '{name}' not found.")
        self.config["aliases"][name] = url
        self._save_config()

    def remove_alias(self, name):
        """Remove an alias."""
        if name not in self.config["aliases"]:
            raise KeyError(f"Alias '{name}' not found.")
        del self.config["aliases"][name]
        self._save_config()

    def list_aliases(self):
        """List all aliases."""
        return self.config["aliases"]

    def get_aliases(self):
        """Get all aliases."""
        return self.config["aliases"]

    def clear_all_aliases(self):
        """Remove all aliases."""
        self.config["aliases"] = {}
        self._save_config()
