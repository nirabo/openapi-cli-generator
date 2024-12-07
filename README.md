# OpenAPI CLI Generator

A powerful command-line utility that transforms OpenAPI v3.x specifications into intuitive Python CLIs. This tool allows you to interact with any OpenAPI-compliant API through a user-friendly command-line interface.

## 🚀 Features

- **Automatic CLI Generation**: Convert any OpenAPI v3.x spec into a fully functional command-line interface
- **HTTP Method Support**: Complete coverage of standard HTTP methods (GET, POST, PUT, DELETE)
- **Alias Management**: Easy management of multiple API endpoints through aliases
- **Interactive Help**: Built-in documentation and command help
- **Request/Response Handling**: Automatic handling of API interactions
- **Parameter Validation**: Type checking and validation for all inputs

## 📦 Installation

```bash
# Install from PyPI
pip install openapi-cli-generator

# Install from source
git clone https://github.com/yourusername/openapi-cli-generator.git
cd openapi-cli-generator
pip install -r requirements.txt
```

## 🔧 Requirements

- Python 3.7+
- Dependencies (automatically installed):
  - PyYAML >= 6.0
  - Requests >= 2.31.0
  - OpenAPI Spec Validator >= 0.5.1
  - Click >= 8.1.3

## 🚦 Quick Start

1. Add an API alias:
```bash
openapi-cli-generator alias add petstore https://petstore3.swagger.io/api/v3/openapi.json
```

2. Use the generated CLI:
```bash
# Show available commands
openapi-cli-generator petstore --help

# List available pets
openapi-cli-generator petstore pet list

# Get pet by ID
openapi-cli-generator petstore pet get --id 1
```

## ⚙️ Configuration

All runtime configuration, including API aliases, is stored locally in `~/.openapi_cli_generator/config.json`. This ensures that:
- Your personal API configurations remain separate from the codebase
- Sensitive information is not accidentally committed to version control
- Each user maintains their own set of API aliases

## 📚 Documentation

- [Project Description](docs/ProjectDescription.md): Overview and key concepts
- [Requirements](docs/Requirements.md): Functional and non-functional requirements
- [Use Cases](docs/UseCases.md): Detailed use cases and scenarios
- [Software Architecture](docs/SoftwareArchitecture.md): System design and components
- [Testing Strategy](docs/TestingStrategy.md): Testing approach and coverage
- [Changelog](Changelog.md): Version history and updates

## 🔍 Common Commands

### Alias Management
```bash
# Add a new API alias
openapi-cli-generator alias add <url> <name>

# List all aliases
openapi-cli-generator alias list

# Remove an alias
openapi-cli-generator alias remove <name>

# Update existing alias
openapi-cli-generator alias update <name> <new-url>

# Show alias details
openapi-cli-generator alias show <name>
```

### API Interaction
```bash
# Get general help
openapi-cli-generator --help

# Get help for specific API
openapi-cli-generator <alias> --help

# Get help for specific endpoint
openapi-cli-generator <alias> <endpoint> --help
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
