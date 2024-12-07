"""Integration tests for generated CLI API calls."""

# import sys
# from unittest.mock import patch

# import pytest
# import requests

# from openapi_cli_generator.generator import CLIGenerator


# def test_generated_cli_api_calls(sample_openapi_spec, tmp_path, mock_response):
#     """Test that generated CLI correctly makes API calls."""
#     # Generate CLI in temporary directory
#     output_dir = tmp_path / "test_cli"
#     output_dir.mkdir()
#     generator = CLIGenerator(sample_openapi_spec)
#     generator.generate_cli(output_dir)

#     # Import the generated CLI module
#     sys.path.insert(0, str(tmp_path))
#     from test_cli import API

#     # Test API calls
#     api = API()
#     success_resp = mock_response({"id": 1, "name": "John Doe"})
#     with patch("requests.request", return_value=success_resp) as mock_request:
#         result = api.get_employee(1)
#         assert result == {"id": 1, "name": "John Doe"}
#         mock_request.assert_called_once_with(
#             "GET",
#             "http://localhost:8000/hr/employees/1",
#             headers=None,
#             data=None,
#             params=None,
#         )


# def test_generated_cli_error_handling(sample_openapi_spec, tmp_path, mock_response):
#     """Test error handling in generated CLI for API calls."""
#     # Generate CLI in temporary directory
#     output_dir = tmp_path / "error_test_cli"
#     output_dir.mkdir()
#     generator = CLIGenerator(sample_openapi_spec)
#     generator.generate_cli(output_dir)

#     # Import the generated CLI module
#     sys.path.insert(0, str(tmp_path))
#     from error_test_cli import API

#     # Test API error responses
#     api = API()
#     error_resp = mock_response({"error": "Not Found"}, status_code=404)
#     with patch("requests.request", return_value=error_resp) as mock_request:
#         with pytest.raises(requests.exceptions.HTTPError) as exc_info:
#             api.get_employee(1)
#         assert "404" in str(exc_info.value)


# def test_generated_cli_authentication(sample_openapi_spec, tmp_path, mock_response):
#     """Test authentication header handling in generated CLI."""
#     # Generate CLI in temporary directory
#     output_dir = tmp_path / "auth_test_cli"
#     output_dir.mkdir()
#     generator = CLIGenerator(sample_openapi_spec)
#     generator.generate_cli(output_dir)

#     # Import the generated CLI module
#     sys.path.insert(0, str(tmp_path))
#     from auth_test_cli import API

#     # Test API calls with auth headers
#     api = API()
#     success_resp = mock_response({"id": 1, "name": "John Doe"})
#     auth_headers = {"Authorization": "Bearer token123"}
#     with patch("requests.request", return_value=success_resp) as mock_request:
#         result = api.get_employee(1, headers=auth_headers)
#         assert result == {"id": 1, "name": "John Doe"}
#         mock_request.assert_called_once_with(
#             "GET",
#             "http://localhost:8000/hr/employees/1",
#             headers=auth_headers,
#             data=None,
#             params=None,
#         )
