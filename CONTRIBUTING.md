# Contributing to Watson Code Assistant OpenAI Proxy

Thank you for your interest in contributing to the Watson Code Assistant OpenAI Proxy! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project.

## How to Contribute

1. Fork the repository
2. Create a new branch for your feature or bugfix
3. Make your changes
4. Run tests to ensure your changes don't break existing functionality
5. Submit a pull request

## Development Setup

1. Clone your fork of the repository:

   ```bash
   git clone https://github.com/yourusername/wca-openai-proxy.git
   cd wca-openai-proxy
   ```

2. Create a virtual environment and install dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r test-requirements.txt  # For running tests
   pip install -e .
   ```

3. Set up your environment variables:

   ```bash
   export IAM_APIKEY="your-watson-ai-api-key"  # For testing purposes
   ```

## Running Tests

Run the test suite to ensure your changes don't break existing functionality:

```bash
pytest
```

The tests are designed to run without requiring an actual Watson AI API key. All API calls to the Watson AI API are mocked in the test suite. If you add new functionality that interacts with the Watson AI API, make sure to add appropriate mocks in your tests.

## Code Style

This project follows PEP 8 style guidelines. You can check your code with flake8:

```bash
flake8 src tests
```

## Pull Request Process

1. Update the README.md or documentation with details of changes if appropriate
2. Update the tests to cover your changes
3. Ensure all tests pass
4. Your PR will be reviewed by maintainers, who may request changes

## Docker Development

To build and run the Docker container locally:

```bash
docker build -t wca-openai-proxy .
docker run -p 5000:5000 -e IAM_APIKEY="your-watson-ai-api-key" wca-openai-proxy
```

Or using Docker Compose:

```bash
export IAM_APIKEY="your-watson-ai-api-key"
docker-compose up
```
