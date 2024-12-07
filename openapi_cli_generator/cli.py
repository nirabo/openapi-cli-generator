"""CLI for generating command line interfaces from OpenAPI specs.

Usage:
    openapi_cli_generator --help
    openapi_cli_generator alias --help
    openapi_cli_generator alias add <url> <name>
    openapi_cli_generator alias list
    openapi_cli_generator alias remove <name>
    openapi_cli_generator alias update <name> <url>
    openapi_cli_generator alias show <name>
    openapi_cli_generator generate <spec_url> [args...]
"""

import sys
from pathlib import Path

import click

from .config import Config
from .generator import CLIGenerator
from .parser import OpenAPIParser

CONFIG_DIR = Path.home() / ".openapi_cli_generator"
CONFIG_FILE = CONFIG_DIR / "config.json"


def handle_api_command(spec_url, remaining_args):
    """Handle API-specific commands by generating a CLI from the spec."""
    try:
        parser = OpenAPIParser(spec_url)
        spec = parser.parse()
        generator = CLIGenerator(spec)
        generator.generate_cli()
        if remaining_args:
            generator.execute(remaining_args)
        else:
            generator.execute(["--help"])
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@click.group()
def cli():
    """OpenAPI CLI Generator - Convert OpenAPI specs to command line interfaces."""
    pass


@cli.group()
def alias():
    """Manage API aliases."""
    pass


@alias.command()
@click.argument("url")
@click.argument("name")
def add(url, name):
    """Add a new API alias."""
    try:
        config = Config()
        config.add_alias(name, url)
        click.echo(f"Added alias '{name}' for {url}")
    except ValueError as e:
        click.echo(f"Error: {str(e)}", err=True)


@alias.command()
def list():
    """List all available API aliases."""
    config = Config()
    aliases = config.list_aliases()
    if not aliases:
        click.echo("No aliases configured.")
        return

    click.echo("Configured aliases:")
    for name, url in aliases.items():
        click.echo(f"  {name}: {url}")


@alias.command()
@click.argument("name")
def remove(name):
    """Remove an API alias."""
    try:
        config = Config()
        config.remove_alias(name)
        click.echo(f"Removed alias '{name}'")
    except KeyError as e:
        click.echo(f"Error: {str(e)}", err=True)


@alias.command()
@click.argument("name")
@click.argument("url")
def update(name, url):
    """Update an existing API alias."""
    try:
        config = Config()
        config.update_alias(name, url)
        click.echo(f"Updated alias '{name}' to {url}")
    except KeyError as e:
        click.echo(f"Error: {str(e)}", err=True)


@alias.command()
@click.argument("name")
def show(name):
    """Show details for a specific alias."""
    try:
        config = Config()
        url = config.get_alias(name)
        click.echo(f"Alias '{name}': {url}")
    except KeyError as e:
        click.echo(f"Error: {str(e)}", err=True)


@cli.command()
@click.argument("spec_url")
def generate(spec_url):
    """Generate CLI from an OpenAPI specification."""
    handle_api_command(spec_url, None)


def main():
    """OpenAPI CLI Generator - Convert OpenAPI specs to command line interfaces."""
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        cli.main(["--help"])
        return

    # Load config to check for aliases
    config = Config()
    aliases = config.list_aliases()

    # Check if first argument is an alias
    if sys.argv[1] in aliases:
        alias_name = sys.argv[1]
        spec_url = aliases[alias_name]
        handle_api_command(spec_url, sys.argv[2:])
        return

    # Otherwise, proceed with normal CLI commands
    cli.main()


if __name__ == "__main__":
    main()
