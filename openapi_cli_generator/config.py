"""OpenAPI CLI configuration management.

This module provides a class for managing OpenAPI CLI configuration,
including adding, updating, and removing API aliases.
"""

import json
from pathlib import Path


class Config:
    """OpenAPI CLI configuration manager."""

    def __init__(self, config_dir=None):
        """Initialize the configuration manager.

        Args:
            config_dir (Path, optional): Override default config directory for testing.
        """
        self.config_dir = (
            Path(config_dir) if config_dir else Path.home() / ".openapi_cli_generator"
        )
        self.config_file = self.config_dir / "config.json"
        self._ensure_config_exists()
        self.load_config()

    def _ensure_config_exists(self):
        """Ensure config directory and file exist with empty default structure."""
        self.config_dir.mkdir(exist_ok=True)
        if not self.config_file.exists():
            # Initialize with empty structure
            default_config = {
                "aliases": {},
                "version": "1.0.0",
                "created_at": None,  # Will be set on first alias addition
            }
            with open(self.config_file, "w") as f:
                json.dump(default_config, f, indent=2)

    def load_config(self):
        """Load configuration from file."""
        with open(self.config_file) as f:
            self.config = json.load(f)

        # Ensure basic structure exists
        if "aliases" not in self.config:
            self.config["aliases"] = {}
            self.save_config()

    def save_config(self):
        """Save configuration to file."""
        # Create backup before saving
        if self.config_file.exists():
            backup_file = self.config_file.with_suffix(".json.bak")
            try:
                import shutil

                shutil.copy2(self.config_file, backup_file)
            except Exception:
                pass  # Ignore backup errors

        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)

    def add_alias(self, name, url):
        """Add a new API alias."""
        if name in self.config["aliases"]:
            raise ValueError(
                f"Alias '{name}' already exists. Use update_alias to modify it."
            )
        self.config["aliases"][name] = url
        self.save_config()

    def get_alias(self, name):
        """Get URL for an alias."""
        if name not in self.config["aliases"]:
            raise KeyError(f"Alias '{name}' not found")
        return self.config["aliases"][name]

    def update_alias(self, name, url):
        """Update an existing alias."""
        if name not in self.config["aliases"]:
            raise KeyError(f"Alias '{name}' not found")
        self.config["aliases"][name] = url
        self.save_config()

    def remove_alias(self, name):
        """Remove an alias."""
        if name not in self.config["aliases"]:
            raise KeyError(f"Alias '{name}' not found")
        del self.config["aliases"][name]
        self.save_config()

    def list_aliases(self):
        """List all aliases."""
        return self.config["aliases"]

    def clear_all_aliases(self):
        """Clear all aliases (useful for testing or reset)."""
        self.config["aliases"] = {}
        self.save_config()
