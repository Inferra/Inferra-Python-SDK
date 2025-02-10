# Available models and their prices (per 1M tokens)
AVAILABLE_MODELS = {
    "meta-llama/llama-3.2-1b-instruct/fp-8": 0.015,
    "meta-llama/llama-3.2-3b-instruct/fp-8": 0.03,
    "meta-llama/llama-3.1-8b-instruct/fp-8": 0.045,
    "meta-llama/llama-3.1-8b-instruct/fp-16": 0.05,
    "mistralai/mistral-nemo-12b-instruct/fp-8": 0.10,
    "meta-llama/llama-3.1-70b-instruct/fp-8": 0.30,
}

# API endpoints
ENDPOINTS = {
    "chat": "/chat/completions",
    "completions": "/completions",
    "batch": "/batch",
    "files": "/files",
}

# Rate limits
RATE_LIMITS = {
    "language_models": 500,  # requests per minute
    "image_models": 100,     # requests per minute
}
