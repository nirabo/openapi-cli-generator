"""Integration tests for generated CLI API calls."""

import json
import sys
from unittest.mock import patch

import pytest
import requests

from openapi_cli_generator.generator import CLIGenerator


def test_generated_cli_api_calls(sample_openapi_spec, tmp_path, mock_response):
    """Test that generated CLI correctly makes API calls."""
    # Generate CLI in temporary directory
    output_dir = tmp_path / "test_cli"
    output_dir.mkdir()
    generator = CLIGenerator(sample_openapi_spec)
    generator.generate_cli()

    # Import the generated CLI module
    import sys

    sys.path.insert(0, str(tmp_path))
    from test_cli import cli

    # Mock requests for testing
    expected_response = {"message": "Success"}
    mock_resp = mock_response(expected_response)

    with patch("requests.get", return_value=mock_resp) as mock_get, patch(
        "requests.post", return_value=mock_resp
    ) as mock_post:

        # Test GET endpoint
        result = cli.get_endpoint()
        assert result == expected_response
        mock_get.assert_called_once()

        # Test POST endpoint with parameters
        test_data = {"key": "value"}
        result = cli.post_endpoint(json.dumps(test_data))
        assert result == expected_response
        mock_post.assert_called_once()
        assert json.loads(mock_post.call_args[1]["data"]) == test_data


def test_generated_cli_error_handling(sample_openapi_spec, tmp_path, mock_response):
    """Test error handling in generated CLI for API calls."""
    # Generate CLI in temporary directory
    output_dir = tmp_path / "error_test_cli"
    output_dir.mkdir()
    generator = CLIGenerator(sample_openapi_spec)
    generator.generate_cli()

    # Import the generated CLI module
    sys.path.insert(0, str(tmp_path))
    from error_test_cli import cli

    # Test API error responses
    error_resp = mock_response({"error": "Not Found"}, status_code=404)
    with patch("requests.get", return_value=error_resp) as mock_get:
        with pytest.raises(requests.exceptions.HTTPError):
            cli.get_endpoint()
        mock_get.assert_called_once()


def test_generated_cli_authentication(sample_openapi_spec, tmp_path, mock_response):
    """Test authentication handling in generated CLI."""
    # Generate CLI in temporary directory
    output_dir = tmp_path / "auth_test_cli"
    output_dir.mkdir()
    generator = CLIGenerator(sample_openapi_spec)
    generator.generate_cli()

    # Import the generated CLI module
    sys.path.insert(0, str(tmp_path))
    from auth_test_cli import cli

    # Test with authentication headers
    auth_token = "Bearer test-token"
    expected_response = {"authenticated": True}
    mock_resp = mock_response(expected_response)

    with patch("requests.get", return_value=mock_resp) as mock_get:
        result = cli.get_endpoint(headers={"Authorization": auth_token})
        assert result == expected_response
        assert mock_get.call_args[1]["headers"]["Authorization"] == auth_token
