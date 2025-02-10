from typing import List, Optional
from ..models.chat import Message
from ..exceptions import InferraAPIError
from ..constants import AVAILABLE_MODELS

def validate_model(model: str) -> None:
    """
    Validate that the model is supported.
    
    Args:
        model: Model identifier
        
    Raises:
        InferraAPIError: If model is not supported
    """
    if model not in AVAILABLE_MODELS:
        raise InferraAPIError(
            f"Model '{model}' is not supported. Available models: {', '.join(AVAILABLE_MODELS)}"
        )

def validate_messages(messages: List[Message]) -> None:
    """
    Validate chat messages.
    
    Args:
        messages: List of chat messages
        
    Raises:
        InferraAPIError: If messages are invalid
    """
    if not messages:
        raise InferraAPIError("Messages list cannot be empty")
    
    valid_roles = {"system", "user", "assistant"}
      for message in messages:
        if message.role not in valid_roles:
            raise InferraAPIError(
                f"Invalid role '{message.role}'. Must be one of: {', '.join(valid_roles)}"
            )
        
        if not message.content or not message.content.strip():
            raise InferraAPIError("Message content cannot be empty")
