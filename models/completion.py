from typing import List, Optional, Union
from pydantic import BaseModel, Field
from .common import Usage, Choice

class Completion(BaseModel):
    """Response from a text completion request."""
    id: str = Field(..., description="Unique identifier for the completion")
    object: str = Field("text_completion", description="Object type")
    created: int = Field(..., description="Unix timestamp of when the completion was created")
    model: str = Field(..., description="ID of the model used")
    choices: List[Choice] = Field(..., description="List of completion choices")
    usage: Usage = Field(..., description="Token usage information")

class CompletionChunk(BaseModel):
    """A chunk of a streaming text completion response."""
    id: str = Field(..., description="Unique identifier for the completion")
    object: str = Field("text_completion.chunk", description="Object type")
    created: int = Field(..., description="Unix timestamp of when the chunk was created")
    model: str = Field(..., description="ID of the model used")
    choices: List[Choice] = Field(..., description="List of completion choices")
    usage: Optional[Usage] = Field(None, description="Token usage information (only in final chunk)")
