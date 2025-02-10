from typing import List, Optional
from pydantic import BaseModel, Field
from .common import Usage, Choice, DeltaMessage

class Message(BaseModel):
    """A message in a chat conversation."""
    role: str = Field(..., description="The role of the message sender (system, user, or assistant)")
    content: str = Field(..., description="The content of the message")
    name: Optional[str] = Field(None, description="The name of the sender (optional)")

class ChatCompletion(BaseModel):
    """Response from a chat completion request."""
    id: str = Field(..., description="Unique identifier for the completion")
    object: str = Field("chat.completion", description="Object type")
    created: int = Field(..., description="Unix timestamp of when the completion was created")
    model: str = Field(..., description="ID of the model used")
    choices: List[Choice] = Field(..., description="List of completion choices")
    usage: Usage = Field(..., description="Token usage information")

class ChatCompletionChunk(BaseModel):
    """A chunk of a streaming chat completion response."""
    id: str = Field(..., description="Unique identifier for the completion")
    object: str = Field("chat.completion.chunk", description="Object type")
    created: int = Field(..., description="Unix timestamp of when the chunk was created")
    model: str = Field(..., description="ID of the model used")
    choices: List[Choice] = Field(..., description="List of completion choices")
    usage: Optional[Usage] = Field(None, description="Token usage information (only in final chunk)")
