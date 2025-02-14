from typing import List, Optional, Union, AsyncIterator, Dict, Any
from ..models.chat import ChatCompletion, ChatCompletionChunk, Message
from ..utils.retry import retry_with_exponential_backoff
from ..utils.rate_limiter import RateLimiter
from ..utils.validators import validate_messages, validate_model
from ..exceptions import InferraAPIError, InferraValidationError
from ..constants import ENDPOINTS

class ChatAPI:
    """
    API client for chat completions.
    
    Handles chat-based interactions with the model, including streaming responses
    and rate limiting.
    """
    
    def __init__(self, client):
        """
        Initialize the chat API client.

        Args:
            client: The main Inferra client instance
        """
        self.client = client
        self.rate_limiter = RateLimiter(
            requests_per_minute=500,
            burst_size=50
        )

    @retry_with_exponential_backoff(max_retries=3)
    async def create(
        self,
        model: str,
        messages: List[Message],
        stream: bool = False,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
    ) -> Union[ChatCompletion, AsyncIterator[ChatCompletionChunk]]:
        """
        Create a chat completion.

        Args:
            model: The model to use for completion
            messages: List of messages in the conversation
            stream: Whether to stream the response
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            frequency_penalty: Frequency penalty parameter
            presence_penalty: Presence penalty parameter

        Returns:
            Either a ChatCompletion or an AsyncIterator of ChatCompletionChunks

        Raises:
            InferraValidationError: If the input parameters are invalid
            InferraAPIError: If the API request fails
        """
        # Validate inputs
        validate_model(model)
        validate_messages(messages)
        
        if temperature is not None and not 0 <= temperature <= 2:
            raise InferraValidationError("Temperature must be between 0 and 2")
        
        if max_tokens is not None and max_tokens < 1:
            raise InferraValidationError("max_tokens must be positive")

        await self.rate_limiter.acquire()
        
        try:
            payload = self._build_payload(locals())
            
            response = await self.client.post(
                ENDPOINTS["chat"],
                json=payload,
                stream=stream
            )
            
            if stream:
                return self._handle_streaming_response(response)
            return ChatCompletion(**response.json())
            
        except Exception as e:
            if isinstance(e, InferraAPIError):
                raise
            raise InferraAPIError(f"Chat completion failed: {str(e)}")

    def _build_payload(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build the request payload from parameters.

        Args:
            params: Dictionary of parameters

        Returns:
            Request payload dictionary
        """
        payload = {
            "model": params["model"],
            "messages": [m.dict() for m in params["messages"]],
            "stream": params["stream"]
        }
        
        # Add optional parameters if they have values
        optional_params = [
            "temperature", "max_tokens", "top_p",
            "frequency_penalty", "presence_penalty"
        ]
        
        for param in optional_params:
            if params[param] is not None:
                payload[param] = params[param]
        
        return payload

    async def _handle_streaming_response(
        self,
        response
    ) -> AsyncIterator[ChatCompletionChunk]:
        """
        Handle streaming response from the API.

        Args:
            response: The streaming response object

        Yields:
            ChatCompletionChunk objects
            
        Raises:
            InferraAPIError: If there's an error processing the stream
        """
        try:
            async for line in response.iter_lines():
                if line:
                    chunk = ChatCompletionChunk.parse_raw(line)
                    yield chunk
        except Exception as e:
            raise InferraAPIError(f"Error processing stream: {str(e)}")

    async def create_many(
        self,
        model: str,
        message_lists: List[List[Message]],
        **kwargs
    ) -> List[ChatCompletion]:
        """
        Create multiple chat completions in parallel.

        Args:
            model: The model to use
            message_lists: List of message lists, one for each completion
            **kwargs: Additional parameters passed to create()

        Returns:
            List of ChatCompletion objects
        """
        return await asyncio.gather(*[
            self.create(model=model, messages=messages, **kwargs)
            for messages in message_lists
        ])
