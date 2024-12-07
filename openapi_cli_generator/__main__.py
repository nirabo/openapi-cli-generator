"""The main entry point for generating CLIs from OpenAPI v3.x specs."""

import argparse
import json
import sys

from .generator import CLIGenerator


def main():
    """Maiun function entry point."""
    parser = argparse.ArgumentParser(description="OpenAPI CLI Generator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Generate command
    generate_parser = subparsers.add_parser(
        "generate", help="Generate a CLI from an OpenAPI spec"
    )
    generate_parser.add_argument(
        "--spec", required=True, help="Path to OpenAPI spec file"
    )
    generate_parser.add_argument(
        "--output", required=True, help="Output directory for generated CLI"
    )

    # Alias commands
    alias_parser = subparsers.add_parser("alias", help="Manage API aliases")
    alias_subparsers = alias_parser.add_subparsers(dest="alias_command", required=True)

    # Add alias
    add_parser = alias_subparsers.add_parser("add", help="Add an API alias")
    add_parser.add_argument("name", help="Name of the alias")
    add_parser.add_argument("spec", help="Path to OpenAPI spec file")

    # Remove alias
    remove_parser = alias_subparsers.add_parser("remove", help="Remove an API alias")
    remove_parser.add_argument("name", help="Name of the alias to remove")

    # List aliases
    # list_parser = alias_subparsers.add_parser("list", help="List all API aliases")

    args = parser.parse_args()

    if args.command == "generate":
        try:
            with open(args.spec) as f:
                spec = json.load(f)
            generator = CLIGenerator(spec)
            generator.generate_cli(args.output)
            print(f"CLI generated successfully in {args.output}")
        except Exception as e:
            print(f"Error generating CLI: {str(e)}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "alias":
        from .config import Config

        config = Config()

        if args.alias_command == "add":
            try:
                with open(args.spec) as f:
                    json.load(f)  # Validate JSON
                config.add_alias(args.name, args.spec)
                print(f"Added alias '{args.name}' -> {args.spec}")
            except Exception as e:
                print(f"Error adding alias: {str(e)}", file=sys.stderr)
                sys.exit(1)

        elif args.alias_command == "remove":
            try:
                config.remove_alias(args.name)
                print(f"Removed alias '{args.name}'")
            except Exception as e:
                print(f"Error removing alias: {str(e)}", file=sys.stderr)
                sys.exit(1)

        elif args.alias_command == "list":
            aliases = config.get_aliases()
            if aliases:
                print("Available aliases:")
                for name, spec in aliases.items():
                    print(f"  {name} -> {spec}")
            else:
                print("No aliases configured")


if __name__ == "__main__":
    main()
