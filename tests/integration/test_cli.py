"""Integration tests for the OpenAPI CLI Generator command-line interface."""

# import subprocess
# import sys

# from openapi_cli_generator.config import Config


# def test_cli_generate_command(sample_openapi_path, tmp_path):
#     """Test the generate command creates expected CLI structure."""
#     output_dir = tmp_path / "generated_cli"
#     result = subprocess.run(
#         [
#             sys.executable,
#             "-m",
#             "openapi_cli_generator",
#             "generate",
#             "--spec",
#             sample_openapi_path,
#             "--output",
#             str(output_dir),
#         ],
#         capture_output=True,
#         text=True,
#     )

#     assert result.returncode == 0
#     assert output_dir.exists()
#     assert (output_dir / "cli.py").exists()
#     assert (output_dir / "__init__.py").exists()

#     # Test importing and using the generated CLI
#     sys.path.insert(0, str(tmp_path))
#     from generated_cli import api

#     assert hasattr(api, "create_employee")
#     assert hasattr(api, "get_employee")
#     assert hasattr(api, "create_contractor")
#     assert hasattr(api, "get_contractor")
#     assert hasattr(api, "create_driver")
#     assert hasattr(api, "get_driver")


# def test_cli_alias_commands(sample_openapi_path, temp_config_dir, monkeypatch):
#     """Test alias-related commands work correctly."""
#     # Set up environment
#     monkeypatch.setenv("OPENAPI_CLI_CONFIG_DIR", str(temp_config_dir))
#     config = Config()
#     config.clear_all_aliases()  # Clear any existing aliases

#     # Test adding an alias
#     result = subprocess.run(
#         [
#             sys.executable,
#             "-m",
#             "openapi_cli_generator",
#             "alias",
#             "add",
#             "test-api",
#             sample_openapi_path,
#         ],
#         capture_output=True,
#         text=True,
#     )
#     assert result.returncode == 0, f"Error: {result.stderr}"
#     assert "test-api" in config.get_aliases()

#     # Test removing an alias
#     result = subprocess.run(
#         [
#             sys.executable,
#             "-m",
#             "openapi_cli_generator",
#             "alias",
#             "remove",
#             "test-api",
#         ],
#         capture_output=True,
#         text=True,
#     )
#     assert result.returncode == 0, f"Error: {result.stderr}"
#     assert "test-api" not in config.get_aliases()


# def test_cli_error_handling(tmp_path):
#     """Test CLI error handling with invalid inputs."""
#     # Test with non-existent spec file
#     result = subprocess.run(
#         [
#             sys.executable,
#             "-m",
#             "openapi_cli_generator",
#             "generate",
#             "--spec",
#             "nonexistent.json",
#             "--output",
#             str(tmp_path / "cli"),
#         ],
#         capture_output=True,
#         text=True,
#     )
#     assert result.returncode == 1
#     assert "Error" in result.stderr

#     # Test with invalid spec file
#     invalid_spec = tmp_path / "invalid.json"
#     invalid_spec.write_text("{invalid json}")
#     result = subprocess.run(
#         [
#             sys.executable,
#             "-m",
#             "openapi_cli_generator",
#             "generate",
#             "--spec",
#             str(invalid_spec),
#             "--output",
#             str(tmp_path),
#         ],
#         capture_output=True,
#         text=True,
#     )
#     assert result.returncode != 0
#     assert "Error" in result.stderr
