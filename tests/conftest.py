"""Test fixtures for the OpenAPI CLI generator."""

import json
import os

import pytest


@pytest.fixture
def sample_openapi_path():
    """Return the path to the sample OpenAPI specification."""
    return os.path.join(os.path.dirname(__file__), "openapi.json")


@pytest.fixture
def sample_openapi_spec(sample_openapi_path):
    """Load and return the sample OpenAPI specification."""
    with open(sample_openapi_path) as f:
        return json.load(f)


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary config directory."""
    config_dir = tmp_path / ".openapi_cli_generator"
    config_dir.mkdir()
    config_file = config_dir / "config.json"
    config_file.write_text('{"aliases": {}}')
    return config_dir


@pytest.fixture
def mock_response():
    """Return a mock response for API calls."""

    class MockResponse:
        def __init__(self, json_data, status_code=200, headers=None):
            self.json_data = json_data
            self.status_code = status_code
            self.headers = headers or {"content-type": "application/json"}
            self.text = json.dumps(json_data)

        def json(self):
            return self.json_data

        def raise_for_status(self):
            if self.status_code >= 400:
                raise Exception(f"HTTP Error: {self.status_code}")

    return MockResponse
