"""Unit tests for the OpenAPIParser class."""

import json

import pytest
import requests

from openapi_cli_generator.parser import OpenAPIParser


def test_parse_valid_json(sample_openapi_path, mock_response, monkeypatch):
    """Test parsing a valid OpenAPI JSON specification."""

    def mock_get(*args, **kwargs):
        with open(sample_openapi_path) as f:
            return mock_response(json.load(f))

    monkeypatch.setattr(requests, "get", mock_get)
    parser = OpenAPIParser("http://example.com/api.json")
    spec = parser.parse()

    assert spec["openapi"] == "3.1.0"
    assert spec["info"]["title"] == "FastAPI"  # Updated to match actual spec
    assert "/hr/employees/" in spec["paths"]


def test_parse_invalid_json(mock_response, monkeypatch):
    """Test parsing an invalid JSON specification."""
    invalid_json = '{"invalid": json'  # Missing closing brace

    class MockResponseWithRawText(mock_response):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.text = invalid_json

        def json(self):
            return json.loads(self.text)

    def mock_get(*args, **kwargs):
        return MockResponseWithRawText(
            None, headers={"content-type": "application/json"}
        )

    monkeypatch.setattr(requests, "get", mock_get)
    parser = OpenAPIParser("http://example.com/api.json")

    with pytest.raises(json.JSONDecodeError):
        parser.parse()


def test_parse_yaml_spec(mock_response, monkeypatch):
    """Test parsing a YAML specification."""
    yaml_content = """
    openapi: 3.0.0
    info:
      title: Test API
      version: 1.0.0
    paths: {}
    """

    def mock_get(*args, **kwargs):
        import yaml

        return mock_response(
            yaml.safe_load(yaml_content), headers={"content-type": "application/yaml"}
        )

    monkeypatch.setattr(requests, "get", mock_get)
    parser = OpenAPIParser("http://example.com/api.yaml")
    spec = parser.parse()

    assert spec["openapi"] == "3.0.0"
    assert spec["info"]["title"] == "Test API"


def test_network_error(monkeypatch):
    """Test handling of network errors."""

    def mock_get(*args, **kwargs):
        raise requests.exceptions.ConnectionError()

    monkeypatch.setattr(requests, "get", mock_get)
    parser = OpenAPIParser("http://example.com/api.json")

    with pytest.raises(ConnectionError, match="Failed to fetch OpenAPI spec"):
        parser.parse()


def test_invalid_url():
    """Test handling of invalid URLs."""
    with pytest.raises(ValueError):
        OpenAPIParser("")  # Empty URL

    with pytest.raises(ValueError):
        OpenAPIParser("not-a-url")  # Invalid URL format
