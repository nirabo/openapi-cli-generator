"""Test cases for the OpenAPI CLI generator."""

import json

import pytest

from openapi_cli_generator.generator import CLIGenerator


def test_command_structure(sample_openapi_spec):
    """Test the generated command structure."""
    generator = CLIGenerator(sample_openapi_spec)
    generator.generate_cli()

    # Test help output
    with pytest.raises(SystemExit):
        generator.execute(["--help"])

    # Test resource command
    with pytest.raises(SystemExit):
        generator.execute(["hr", "--help"])

    # Test action command
    with pytest.raises(SystemExit):
        generator.execute(["hr", "employees", "--help"])


def test_parameter_handling(sample_openapi_spec, capsys):
    """Test handling of different parameter types."""
    generator = CLIGenerator(sample_openapi_spec)
    generator.generate_cli()

    # Test required parameters
    with pytest.raises(SystemExit) as exc_info:
        generator.execute(["hr", "employees", "get"])
    assert exc_info.value.code != 0

    # Test optional parameters
    with pytest.raises(SystemExit):
        generator.execute(["hr", "employees", "list", "--department", "IT"])

    # Test integer parameters
    with pytest.raises(SystemExit):
        generator.execute(["hr", "employees", "list", "--limit", "10"])


def test_request_body_handling(sample_openapi_spec):
    """Test handling of request bodies."""
    generator = CLIGenerator(sample_openapi_spec)
    generator.generate_cli()

    employee_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "department": "IT",
    }

    # Test create command with request body
    with pytest.raises(SystemExit):
        generator.execute(
            ["hr", "employees", "create", "--data", json.dumps(employee_data)]
        )


def test_type_conversion(sample_openapi_spec):
    """Test parameter type conversion."""
    generator = CLIGenerator(sample_openapi_spec)

    # Test integer conversion
    assert generator._get_type("integer") == int

    # Test number conversion
    assert generator._get_type("number") == float

    # Test boolean conversion
    assert generator._get_type("boolean") == bool

    # Test string conversion
    assert generator._get_type("string") == str

    # Test default conversion
    assert generator._get_type("unknown") == str


def test_nested_resources(sample_openapi_spec, capsys):
    """Test handling of nested resources."""
    generator = CLIGenerator(sample_openapi_spec)
    generator.generate_cli()

    # Test nested resource command structure
    with pytest.raises(SystemExit):
        generator.execute(["hr", "employees", "--help"])

    captured = capsys.readouterr()
    # Check for available operations based on OpenAPI spec
    assert "create" in captured.out  # POST operation
    assert "list" in captured.out  # GET operation is mapped to "list" in the CLI


def test_error_handling(sample_openapi_spec, capsys):
    """Test error handling in the generator."""
    generator = CLIGenerator(sample_openapi_spec)
    generator.generate_cli()

    # Test invalid command
    with pytest.raises(SystemExit) as exc_info:
        generator.execute(["invalid", "command"])
    assert exc_info.value.code != 0

    # Test invalid parameter type
    with pytest.raises(SystemExit) as exc_info:
        generator.execute(["hr", "employees", "list", "--limit", "invalid"])
    assert exc_info.value.code != 0

    # Test invalid JSON in request body
    with pytest.raises(SystemExit) as exc_info:
        generator.execute(["hr", "employees", "create", "--data", "{invalid json}"])
    assert exc_info.value.code != 0
