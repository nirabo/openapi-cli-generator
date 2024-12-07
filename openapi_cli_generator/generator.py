"""OpenAPI CLI Generator.

This module provides a class for generating command line interfaces from OpenAPI specs.
"""

import argparse
import json
import sys

import requests


class CLIGenerator:
    """CLI Generator class."""

    def __init__(self, spec):
        """Initialize CLI Generator with OpenAPI spec."""
        self.spec = spec
        self.parser = None
        self.base_url = self._get_base_url()

    def _get_base_url(self):
        """Extract base URL from the OpenAPI spec."""
        if "servers" in self.spec and self.spec["servers"]:
            return self.spec["servers"][0]["url"]
        return ""

    def _make_request(self, method, path, params=None, data=None):
        """Make HTTP request to the API."""
        url = self.base_url + path
        try:
            response = requests.request(
                method=method.upper(), url=url, params=params, json=data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request: {str(e)}")
            sys.exit(1)

    def _get_resource_and_action(self, path, method):
        """Extract resource and action from path and method."""
        # Remove leading/trailing slashes and split path
        parts = [p for p in path.strip("/").split("/") if not p.startswith("{")]

        if not parts:
            return ["root"], method.lower()

        # Map HTTP methods to friendly names
        method_mapping = {
            "get": "list" if path.endswith("}") else "get",
            "post": "create",
            "put": "update",
            "patch": "update",
            "delete": "delete",
        }

        action = method_mapping.get(method.lower(), method.lower())

        # Special cases for common patterns
        if len(parts) > 1 and parts[-1] in ["search", "filter", "export", "import"]:
            action = parts[-1]
            parts = parts[:-1]

        # Return all path parts except the last one as resource path
        return parts, action

    def _add_command_to_group(
        self, subparsers, resource, action, path, method, operation
    ):
        """Add a command to the resource group."""
        command_name = action

        # Get or create the resource group
        if resource not in subparsers:
            resource_parser = self.parser.add_subparsers(dest="resource")
            resource_group = resource_parser.add_parser(
                resource, help=f"Operations on {resource}"
            )
            subparsers[resource] = resource_group.add_subparsers(dest="action")

        # Create the command parser
        command_parser = subparsers[resource].add_parser(
            command_name,
            help=operation.get("summary", ""),
            description=operation.get("description", ""),
        )

        # Store method and path for execution
        command_parser.set_defaults(method=method, path=path)

        # Add parameters as arguments
        if "parameters" in operation:
            for param in operation["parameters"]:
                name = param["name"]
                required = param.get("required", False)
                help_text = param.get("description", "")
                param_type = param.get("schema", {}).get("type", "string")

                if required:
                    command_parser.add_argument(
                        name, help=help_text, type=self._get_type(param_type)
                    )
                else:
                    command_parser.add_argument(
                        f"--{name}", help=help_text, type=self._get_type(param_type)
                    )

        # Handle request body if present
        if "requestBody" in operation:
            command_parser.add_argument(
                "--data", help="Request body (JSON string)", type=json.loads
            )

    def generate_cli(self):
        """Generate CLI interface from OpenAPI spec."""
        self.parser = argparse.ArgumentParser(
            description=self.spec.get("info", {}).get("description", "")
        )

        # First pass: collect all resources and their actions
        resource_groups = {}

        for path, path_item in self.spec["paths"].items():
            for method, operation in path_item.items():
                resource_path, action = self._get_resource_and_action(path, method)

                # Navigate to the correct nested level
                current = resource_groups
                for resource in resource_path[:-1]:  # All but the last resource
                    if resource not in current:
                        current[resource] = {}
                    current = current[resource]

                # Handle the leaf resource
                if resource_path:
                    leaf_resource = resource_path[-1]
                    if leaf_resource not in current:
                        current[leaf_resource] = {"actions": {}}
                    if "actions" not in current[leaf_resource]:
                        current[leaf_resource]["actions"] = {}

                    # Store the operation
                    if action not in current[leaf_resource]["actions"]:
                        current[leaf_resource]["actions"][action] = []
                    current[leaf_resource]["actions"][action].append(
                        {"method": method, "path": path, "operation": operation}
                    )

        def create_parser_for_resource(parser, resource_dict):
            """Recursively create parsers for resources and their children."""
            subparsers = parser.add_subparsers(dest="command", required=True)

            # Process each resource
            for resource_name, resource_data in resource_dict.items():
                if resource_name == "actions":
                    # Add action commands to the current parser
                    for action, operations in resource_data.items():
                        action_parser = subparsers.add_parser(
                            action, help=operations[0]["operation"].get("summary", "")
                        )

                        # Store operation details
                        action_parser.set_defaults(
                            method=operations[0]["method"], path=operations[0]["path"]
                        )

                        # Add parameters
                        operation = operations[0]["operation"]
                        if "parameters" in operation:
                            for param in operation["parameters"]:
                                name = param["name"]
                                required = param.get("required", False)
                                help_text = param.get("description", "")
                                param_type = param.get("schema", {}).get(
                                    "type", "string"
                                )

                                if required:
                                    action_parser.add_argument(
                                        name,
                                        help=help_text,
                                        type=self._get_type(param_type),
                                    )
                                else:
                                    action_parser.add_argument(
                                        f"--{name}",
                                        help=help_text,
                                        type=self._get_type(param_type),
                                    )

                        if "requestBody" in operation:
                            action_parser.add_argument(
                                "--data",
                                help="Request body (JSON string)",
                                type=json.loads,
                            )
                else:
                    # Create a new subparser for this resource
                    resource_parser = subparsers.add_parser(
                        resource_name, help=f"Operations on {resource_name}"
                    )

                    # Recursively create parsers for nested resources
                    create_parser_for_resource(resource_parser, resource_data)

        # Create the parser hierarchy
        if resource_groups:
            create_parser_for_resource(self.parser, resource_groups)

    def _get_type(self, param_type):
        """Convert OpenAPI types to Python types."""
        type_map = {"integer": int, "number": float, "boolean": bool, "string": str}
        return type_map.get(param_type, str)

    def execute(self, args=None):
        """Execute the CLI with the given arguments."""
        if args is None:
            args = sys.argv[1:]

        parsed_args = self.parser.parse_args(args)

        # Find the action from the parsed args
        action = None
        for key, value in vars(parsed_args).items():
            if key == "command" and value is not None:
                action = value
                break

        if not action:
            self.parser.print_help()
            return

        # Extract method and path
        method = getattr(parsed_args, "method", None)
        path = getattr(parsed_args, "path", None)

        if not method or not path:
            self.parser.print_help()
            return

        # Convert args to dict and remove special attributes
        args_dict = vars(parsed_args)
        special_keys = ["command", "method", "path"]
        for special in special_keys:
            args_dict.pop(special, None)

        # Separate query parameters and request body
        data = args_dict.pop("data", None)

        # Make the request
        result = self._make_request(method, path, params=args_dict, data=data)

        # Print response
        print(json.dumps(result, indent=2))
