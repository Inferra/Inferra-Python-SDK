import pytest
from inferra.utils.token_counter import TokenCounter
from inferra.utils.validators import validate_model, validate_messages
from inferra.exceptions import InferraAPIError
from inferra.models.chat import Message

def test_token_counter():
    counter = TokenCounter("meta-llama/llama-3.1-8b-instruct/fp-8")
    messages = [
        Message(role="system", content="You are a helpful assistant."),
        Message(role="user", content="Hello!")
    ]
    
    token_count = counter.count_message_tokens(messages)
    assert token_count["prompt_tokens"] > 0
    assert "total_tokens" in token_count

def test_model_validation():
    # Valid model
    validate_model("meta-llama/llama-3.1-8b-instruct/fp-8")
    
    # Invalid model
    with pytest.raises(InferraAPIError):
        validate_model("invalid-model")

def test_message_validation():
    # Valid messages
    messages = [Message(role="user", content="Hello!")]
    validate_messages(messages)
    
    # Invalid role
    with pytest.raises(InferraAPIError):
        validate_messages([Message(role="invalid", content="Hello!")])
    
    # Empty content
    with pytest.raises(InferraAPIError):
        validate_messages([Message(role="user", content="")])
