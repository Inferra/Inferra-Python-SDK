from typing import List, Optional, Union, AsyncIterator
from ..models.chat import ChatCompletion, ChatCompletionChunk, Message
from ..utils.retry import retry_with_exponential_backoff
from ..utils.rate_limiter import RateLimiter
from ..exceptions import InferraAPIError

class ChatAPI:
    def __init__(self, client):
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
        await self.rate_limiter.acquire()
        
        payload = {
            "model": model,
            "messages": [m.dict() for m in messages],
            "stream": stream
        }
        
        # Add optional parameters
        for key, value in locals().items():
            if value is not None and key not in ["self", "model", "messages", "stream"]:
                payload[key] = value
        
        response = await self.client.post(
            "/chat/completions",
            json=payload,
            stream=stream
        )
        
        if stream:
            return self._handle_streaming_response(response)
        return ChatCompletion(**response.json())

    async def _handle_streaming_response(
        self,
        response
    ) -> AsyncIterator[ChatCompletionChunk]:
        async for line in response.iter_lines():
            if line:
                chunk = ChatCompletionChunk.parse_raw(line)
                yield chunk
