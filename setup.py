"""Setup script for OpenAPI CLI."""

from setuptools import find_packages, setup

setup(
    name="openapi-cli-generator",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "pyyaml>=6.0.2",
        "requests>=2.32.3",
        "openapi-spec-validator>=0.7.1",
        "click>=8.1.3",
    ],
    entry_points={
        "console_scripts": [
            "openapi_cli_generator=openapi_cli_generator.cli:main",
        ],
    },
    # Test configuration
    tests_require=[
        "pytest>=8.3.4",
        "pytest-mock>=3.14.0",
        "pytest-cov>=6.0.0",
        "requests-mock>=1.12.0",
        "coverage>=7.2.0",
    ],
    extras_require={
        "test": [
            "pytest>=8.3.4",
            "pytest-mock>=3.14.0",
            "pytest-cov>=6.0.0",
            "requests-mock>=1.12.0",
            "coverage>=7.6.9",
            "flake8>=6.0.0",
            "pre-commit>=4.0.1",
        ],
        "dev": [
            "pytest>=8.3.4",
            "pytest-cov>=6.0.0",
            "flake8>=6.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "sphinx>=7.0.0",
        ],
    },
    python_requires=">=3.7",
    # Project metadata
    author="Lyuboslav Petrov",
    author_email="petrov.lyuboslav.work@gmail.com",
    description="A command line utility to turn any OpenAPIv3 API into a Python CLI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/nirabo/openapi-cli-generator",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # Test suite
    test_suite="tests",
    # Include package data
    include_package_data=True,
    # Command line options for test running
    options={
        "test": {
            "pytest": {
                "addopts": "--verbose --cov=openapi_cli_generator --cov-report=term-missing",
            },
        },
    },
)
