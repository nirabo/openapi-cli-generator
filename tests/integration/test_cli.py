"""Integration tests for the OpenAPI CLI Generator command-line interface."""

import subprocess
import sys

from openapi_cli_generator.config import Config


def test_cli_generate_command(sample_openapi_path, tmp_path):
    """Test the generate command creates expected CLI structure."""
    output_dir = tmp_path / "generated_cli"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "openapi_cli_generator",
            "generate",
            "--spec",
            sample_openapi_path,
            "--output",
            str(output_dir),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert output_dir.exists()
    assert (output_dir / "cli.py").exists()
    assert (output_dir / "config.json").exists()


def test_cli_alias_commands(sample_openapi_path, temp_config_dir, monkeypatch):
    """Test alias-related commands work correctly."""
    # Set up environment
    monkeypatch.setenv("OPENAPI_CLI_CONFIG_DIR", str(temp_config_dir))
    config = Config()

    # Test adding an alias
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "openapi_cli_generator",
            "alias",
            "add",
            "test-api",
            sample_openapi_path,
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0

    # Verify alias was added
    config.load()
    assert "test-api" in config.aliases
    assert config.aliases["test-api"] == sample_openapi_path

    # Test listing aliases
    result = subprocess.run(
        [sys.executable, "-m", "openapi_cli_generator", "alias", "list"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "test-api" in result.stdout

    # Test removing alias
    result = subprocess.run(
        [sys.executable, "-m", "openapi_cli_generator", "alias", "remove", "test-api"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0

    # Verify alias was removed
    config.load()
    assert "test-api" not in config.aliases


def test_cli_error_handling(tmp_path):
    """Test CLI error handling with invalid inputs."""
    # Test with non-existent spec file
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "openapi_cli_generator",
            "generate",
            "--spec",
            "nonexistent.json",
            "--output",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "Error" in result.stderr

    # Test with invalid spec file
    invalid_spec = tmp_path / "invalid.json"
    invalid_spec.write_text("{invalid json}")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "openapi_cli_generator",
            "generate",
            "--spec",
            str(invalid_spec),
            "--output",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "Error" in result.stderr
