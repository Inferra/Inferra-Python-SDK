from typing import List, Dict, Optional
import tiktoken
from ..models.chat import Message
from ..exceptions import InferraAPIError

class TokenCounter:
    def __init__(self, model: str):
        """
        Initialize token counter for a specific model.
        
        Args:
            model: The model identifier
        """
        try:
            self.encoder = tiktoken.encoding_for_model(model)
        except KeyError:
            # Fall back to cl100k_base for unknown models
            self.encoder = tiktoken.get_encoding("cl100k_base")
        
        # Model-specific settings
        self.tokens_per_message = 3  # Default for most models
        self.tokens_per_name = 1
        
        if "llama" in model.lower():
            self.tokens_per_message = 4
            self.tokens_per_name = 2

    def count_message_tokens(self, messages: List[Message]) -> Dict[str, int]:
        """
        Count tokens in a list of chat messages.
        
        Args:
            messages: List of chat messages
            
        Returns:
            Dictionary with prompt_tokens, completion_tokens, and total_tokens
        """
        num_tokens = 0
        
        for message in messages:
            num_tokens += self.tokens_per_message
            
            for key, value in message.dict().items():
                if value:
                    num_tokens += len(self.encoder.encode(str(value)))
                    if key == "name":
                        num_tokens += self.tokens_per_name
        
        # Every reply is primed with <|start|>assistant<|message|>
        num_tokens += 3
        
        return {
            "prompt_tokens": num_tokens,
            "completion_tokens": 0,  # Will be filled by API response
            "total_tokens": num_tokens
        }

    def count_string_tokens(self, text: str) -> int:
        """
        Count tokens in a string.
        
        Args:
            text: Input text
            
        Returns:
            Number of tokens
        """
        return len(self.encoder.encode(text))
