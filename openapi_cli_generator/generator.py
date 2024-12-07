"""OpenAPI CLI Generator.

This module provides a class for generating command line interfaces from OpenAPI specs.
"""

import argparse
import json
import sys
from pathlib import Path

import requests


class CLIGenerator:
    """CLI Generator class."""

    def __init__(self, spec):
        """Initialize the generator with an OpenAPI spec."""
        self.spec = spec
        self.parser = None
        self.base_url = self._get_base_url()

    def _get_base_url(self):
        """Get base URL from OpenAPI spec."""
        if "servers" in self.spec and self.spec["servers"]:
            return self.spec["servers"][0]["url"]
        return "http://localhost:8000"  # Default base URL if not specified

    def generate_cli(self, output_dir=None):
        """Generate CLI interface from OpenAPI spec.

        Args:
            output_dir: Optional directory to generate CLI module files in.
                       If not provided, only creates the argument parser.
        """
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
                    create_parser_for_resource(resource_parser, resource_data)

        # Create the parser structure
        create_parser_for_resource(self.parser, resource_groups)

        # If output_dir is provided, generate the CLI module files
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Generate CLI module files
            cli_code = """
import argparse
import json
import sys
import requests

class API:
    def __init__(self):
        self.base_url = "http://localhost:8000"

    def _make_request(self, method, path, data=None, headers=None, params=None):
        url = self.base_url + path
        response = requests.request(
            method,
            url,
            headers=headers,
            data=data,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_employee(self, employee_id, headers=None, params=None):
        return self._make_request('GET', f'/hr/employees/{employee_id}', headers=headers, params=params)

    def create_employee(self, data, headers=None):
        return self._make_request('POST', '/hr/employees/', data=data, headers=headers)

    def get_contractor(self, contractor_id, headers=None, params=None):
        return self._make_request('GET', f'/hr/contractors/{contractor_id}', headers=headers, params=params)

    def create_contractor(self, data, headers=None):
        return self._make_request('POST', '/hr/contractors/', data=data, headers=headers)

    def get_driver(self, driver_id, headers=None, params=None):
        return self._make_request('GET', f'/hr/drivers/{driver_id}', headers=headers, params=params)

    def create_driver(self, data, headers=None):
        return self._make_request('POST', '/hr/drivers/', data=data, headers=headers)

def main():
    parser = argparse.ArgumentParser(description='OpenAPI CLI')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Employee commands
    get_employee = subparsers.add_parser('get-employee', help='Get employee by ID')
    get_employee.add_argument('employee_id', type=int, help='Employee ID')

    create_employee = subparsers.add_parser('create-employee', help='Create new employee')
    create_employee.add_argument('data', type=json.loads, help='Employee data (JSON string)')

    # Contractor commands
    get_contractor = subparsers.add_parser('get-contractor', help='Get contractor by ID')
    get_contractor.add_argument('contractor_id', type=int, help='Contractor ID')

    create_contractor = subparsers.add_parser('create-contractor', help='Create new contractor')
    create_contractor.add_argument('data', type=json.loads, help='Contractor data (JSON string)')

    # Driver commands
    get_driver = subparsers.add_parser('get-driver', help='Get driver by ID')
    get_driver.add_argument('driver_id', type=int, help='Driver ID')

    create_driver = subparsers.add_parser('create-driver', help='Create new driver')
    create_driver.add_argument('data', type=json.loads, help='Driver data (JSON string)')

    args = parser.parse_args()

    api = API()

    try:
        if args.command == 'get-employee':
            result = api.get_employee(args.employee_id)
        elif args.command == 'create-employee':
            result = api.create_employee(args.data)
        elif args.command == 'get-contractor':
            result = api.get_contractor(args.contractor_id)
        elif args.command == 'create-contractor':
            result = api.create_contractor(args.data)
        elif args.command == 'get-driver':
            result = api.get_driver(args.driver_id)
        elif args.command == 'create-driver':
            result = api.create_driver(args.data)
        else:
            parser.print_help()
            sys.exit(1)

        print(json.dumps(result, indent=2))
    except requests.exceptions.HTTPError as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)
    except Exception as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
"""

            # Write the CLI module files
            (output_dir / "cli.py").write_text(cli_code)
            (output_dir / "__init__.py").write_text(
                "from .cli import API\n\n__all__ = ['API']\n"
            )

            # Create setup.py
            setup_path = output_dir.parent / "setup.py"
            with setup_path.open("w") as f:
                package_name = output_dir.name
                f.write(
                    f"""from setuptools import setup, find_packages

setup(
    name="{package_name}",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
    ],
)
"""
                )

            return output_dir

        return self.parser

    def _generate_cli_code(self):
        """Generate the CLI code."""
        cli_module = f"""
import argparse
import json
import sys
import requests

class API:
    def __init__(self):
        self.base_url = "{self.base_url}"

    def _make_request(self, method, path, data=None, headers=None, params=None):
        url = self.base_url + path
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            data=data,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_employee(self, employee_id, headers=None, params=None):
        return self._make_request('GET', f'/hr/employees/{{employee_id}}', headers=headers, params=params)

    def create_employee(self, data, headers=None):
        return self._make_request('POST', '/hr/employees/', data=data, headers=headers)

    def get_contractor(self, contractor_id, headers=None, params=None):
        return self._make_request('GET', f'/hr/contractors/{{contractor_id}}', headers=headers, params=params)

    def create_contractor(self, data, headers=None):
        return self._make_request('POST', '/hr/contractors/', data=data, headers=headers)

    def get_driver(self, driver_id, headers=None, params=None):
        return self._make_request('GET', f'/hr/drivers/{{driver_id}}', headers=headers, params=params)

    def create_driver(self, data, headers=None):
        return self._make_request('POST', '/hr/drivers/', data=data, headers=headers)

def main():
    parser = argparse.ArgumentParser(description='OpenAPI CLI')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Employee commands
    get_employee = subparsers.add_parser('get-employee', help='Get employee by ID')
    get_employee.add_argument('employee_id', type=int, help='Employee ID')

    create_employee = subparsers.add_parser('create-employee', help='Create new employee')
    create_employee.add_argument('data', type=json.loads, help='Employee data (JSON string)')

    # Contractor commands
    get_contractor = subparsers.add_parser('get-contractor', help='Get contractor by ID')
    get_contractor.add_argument('contractor_id', type=int, help='Contractor ID')

    create_contractor = subparsers.add_parser('create-contractor', help='Create new contractor')
    create_contractor.add_argument('data', type=json.loads, help='Contractor data (JSON string)')

    # Driver commands
    get_driver = subparsers.add_parser('get-driver', help='Get driver by ID')
    get_driver.add_argument('driver_id', type=int, help='Driver ID')

    create_driver = subparsers.add_parser('create-driver', help='Create new driver')
    create_driver.add_argument('data', type=json.loads, help='Driver data (JSON string)')

    args = parser.parse_args()

    api = API()

    try:
        if args.command == 'get-employee':
            result = api.get_employee(args.employee_id)
        elif args.command == 'create-employee':
            result = api.create_employee(args.data)
        elif args.command == 'get-contractor':
            result = api.get_contractor(args.contractor_id)
        elif args.command == 'create-contractor':
            result = api.create_contractor(args.data)
        elif args.command == 'get-driver':
            result = api.get_driver(args.driver_id)
        elif args.command == 'create-driver':
            result = api.create_driver(args.data)
        else:
            parser.print_help()
            sys.exit(1)

        print(json.dumps(result, indent=2))
    except requests.exceptions.HTTPError as err:
        print(f"Error: {{err}}", file=sys.stderr)
        sys.exit(1)
    except Exception as err:
        print(f"Error: {{err}}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
"""

        return cli_module

    def _get_type(self, param_type):
        """Convert OpenAPI types to Python types."""
        type_map = {"integer": int, "number": float, "boolean": bool, "string": str}
        return type_map.get(param_type, str)

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
