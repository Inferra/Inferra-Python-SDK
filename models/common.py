from typing import Optional, List, Union
from pydantic import BaseModel, Field

class Usage(BaseModel):
    """Token usage information."""
    prompt_tokens: int = Field(..., description="Number of tokens in the prompt")
    completion_tokens: int = Field(..., description="Number of tokens in the completion")
    total_tokens: int = Field(..., description="Total number of tokens used")

class DeltaMessage(BaseModel):
    """A delta message in a streaming response."""
    role: Optional[str] = Field(None, description="The role of the message sender")
    content: Optional[str] = Field(None, description="The content of the message")
    name: Optional[str] = Field(None, description="The name of the sender")

class Choice(BaseModel):
    """A completion choice."""
    index: int = Field(..., description="Index of this choice")
    message: Union[Message, DeltaMessage] = Field(..., description="The message or delta")
    finish_reason: Optional[str] = Field(None, description="Reason for finishing")
    logprobs: Optional[dict] = Field(None, description="Log probabilities of tokens")
