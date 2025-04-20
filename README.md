# Watson Code Assistant OpenAI Proxy

A Flask-based proxy server that adapts Watson AI's API to be compatible with OpenAI's API format. This allows applications designed to work with OpenAI's API to seamlessly use Watson Code Assistant (WCA) from IBM instead.

## Overview

This proxy service translates requests from OpenAI's API format to Watson AI's format and vice versa, enabling you to:

- Use tools and libraries designed for OpenAI with Watson AI
- Maintain compatibility with OpenAI-dependent applications
- Leverage Watson AI's capabilities through a familiar API interface

## Features

- OpenAI-compatible `/v1/chat/completions` endpoint
- Support for streaming responses
- Legacy `/v1/completions` endpoint for older tools
- History for chats
- Models listing endpoint
- Built-in Watson AI client module (`src/watsonai.py`)

## Prerequisites

- Python 3.9 or higher
- Watson AI API key (IAM_APIKEY)
- Docker/Podman (optional, for containerized deployment)

## Installation

### Local Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/wca-openai-proxy.git
   cd wca-openai-proxy
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set your Watson AI API key:

   ```bash
   export IAM_APIKEY="your-watson-ai-api-key"
   ```

4. Run the server:

   ```bash
   python src/watson_openai_proxy.py
   ```

### Docker/Podman Setup

#### Using Pre-built Images

You can use the pre-built Docker/Podman images from Docker Hub or Quay.io:

```bash
# From Docker Hub
docker run -p 5000:5000 -e IAM_APIKEY="your-watson-ai-api-key" docker.io/sshnaidm/wca2openai:latest
podman run -p 5000:5000 -e IAM_APIKEY="your-watson-ai-api-key" docker.io/sshnaidm/wca2openai:latest

# From Quay.io
docker run -p 5000:5000 -e IAM_APIKEY="your-watson-ai-api-key" quay.io/sshnaidm1/wca2openai:latest
podman run -p 5000:5000 -e IAM_APIKEY="your-watson-ai-api-key" quay.io/sshnaidm1/wca2openai:latest
```

#### Building Locally

1. Build the Docker image:

   ```bash
   docker build -t wca-openai-proxy .
   ```

   ```bash
   podman build -t wca-openai-proxy .
   ```

2. Run the container:

   ```bash
   docker run -p 5000:5000 -e IAM_APIKEY="your-watson-ai-api-key" wca-openai-proxy
   ```

   ```bash
   podman run -p 5000:5000 -e IAM_APIKEY="your-watson-ai-api-key" wca-openai-proxy
   ```

## Usage

### API Endpoints

#### Chat Completions

```bash
curl http://localhost:5000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "watson-ai",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Hello, how are you?"}
    ]
  }'
```

#### Streaming Chat Completions

```bash
curl http://localhost:5000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "watson-ai",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Hello, how are you?"}
    ],
    "stream": true
  }'
```

#### Legacy Completions

```bash
curl http://localhost:5000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "watson-ai",
    "prompt": "Hello, how are you?"
  }'
```

#### List Models

```bash
curl http://localhost:5000/v1/models
```

## Configuration

The proxy server uses the following environment variables:

- `IAM_APIKEY`: Your Watson AI API key (required)

## Integration Examples

### Python with OpenAI Library

```python
import openai

# Point to your proxy server
openai.api_base = "http://localhost:5000/v1"
openai.api_key = "dummy-key"  # The proxy uses IAM_APIKEY, not this key

# Use the OpenAI library as usual
response = openai.ChatCompletion.create(
    model="watson-ai",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a hello world program in Python."}
    ]
)

print(response.choices[0].message.content)
```

### Node.js with OpenAI Library

```javascript
const { Configuration, OpenAIApi } = require("openai");

const configuration = new Configuration({
    apiKey: "dummy-key",  // The proxy uses IAM_APIKEY, not this key
    basePath: "http://localhost:5000/v1",
});

const openai = new OpenAIApi(configuration);

async function main() {
    const response = await openai.createChatCompletion({
        model: "watson-ai",
        messages: [
            {role: "system", content: "You are a helpful assistant."},
            {role: "user", content: "Write a hello world program in JavaScript."}
        ],
    });

    console.log(response.data.choices[0].message.content);
}

main();
```

### Langchain Integration

```python
from langchain_openai import ChatOpenAI

# Point to your proxy server
chat_llm = ChatOpenAI(base_url="http://localhost:5000/v1", model="watson-ai", api_key="dummy-key")
response = chat_llm.invoke("Write a hello world program in Python.")
print(response.content)
```

## Limitations

- Only supports a single model ("watson-ai")
- Token counting is approximate
- Some advanced OpenAI API features may not be supported
- Tooling is not supported since Watson Code Assistant AI does not support it

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. [Contributions guide](CONTRIBUTING.md).

### Running Tests

The tests are designed to run without requiring an actual Watson AI API key. All API calls are mocked in the test suite:

```bash
# Install test dependencies
pip install -r test-requirements.txt

# Run the tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=term-missing
```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
