"""Parser for OpenAPI specification.

This module provides a class for parsing and validating OpenAPI specifications.

Attributes:
    OpenAPIParser: A class for parsing and validating OpenAPI specifications.

"""

import json
from urllib.parse import urlparse

import requests
import yaml
from openapi_spec_validator import validate


class OpenAPIParser:
    """Parser for OpenAPI specification.

    Attributes:
        spec_url (str): The URL of the OpenAPI specification.

    """

    def __init__(self, spec_url):
        """Initialize parser with spec URL."""
        if not spec_url:
            raise ValueError("Spec URL cannot be empty")

        # Basic URL validation
        parsed = urlparse(spec_url)
        if not all([parsed.scheme, parsed.netloc]):
            raise ValueError("Invalid URL format")

        self.spec_url = spec_url

    def parse(self):
        """Parse and validate OpenAPI specification."""
        try:
            response = requests.get(self.spec_url + "/openapi.json")
            response.raise_for_status()

            content_type = response.headers.get("content-type", "")

            # First try to parse the content
            try:
                if "json" in content_type:
                    spec = response.json()  # This will raise JSONDecodeError if invalid
                else:
                    spec = yaml.safe_load(response.text)
            except json.JSONDecodeError:
                raise  # Re-raise JSON decode errors directly
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML format: {str(e)}")

            # Then validate the specification
            try:
                validate(spec)
            except Exception as e:
                raise ValueError(f"Invalid OpenAPI specification: {str(e)}")

            return spec

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to fetch OpenAPI spec: {str(e)}")
