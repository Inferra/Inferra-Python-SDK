# Inferra Python SDK

The official Python SDK for [Inferra.net](https://inferra.net) - Access leading open source AI models with just a few lines of code.

## Installation

```bash
pip install inferra
```

## Quick Start

```python
from inferra import InferraClient

# Initialize client
client = InferraClient(api_key="your-api-key")

# Create a chat completion
response = client.chat.create(
    model="meta-llama/llama-3.1-8b-instruct/fp-8",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the meaning of life?"}
    ],
    stream=True
)

# Process streaming response
for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end='', flush=True)
```

## Features
- Full support for Inferra's API
- Async/await support
- Type hints throughout
- Built-in rate limiting and retries
- Streaming support
- Batch processing
- Comprehensive documentation

## Available Models

| Model Name | Price (per 1M tokens) |
|------------|----------------------|
| meta-llama/llama-3.2-1b-instruct/fp-8 | $0.015 |
| meta-llama/llama-3.2-3b-instruct/fp-8 | $0.03 |
| meta-llama/llama-3.1-8b-instruct/fp-8 | $0.045 |
| meta-llama/llama-3.1-8b-instruct/fp-16 | $0.05 |
| mistralai/mistral-nemo-12b-instruct/fp-8 | $0.10 |
| meta-llama/llama-3.1-70b-instruct/fp-8 | $0.30 |

## Development
```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
make test

# Run linting
make lint
```
