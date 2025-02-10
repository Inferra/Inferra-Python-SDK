from typing import Optional, Union, AsyncIterator
from ..models.completion import Completion, CompletionChunk
from ..utils.retry import retry_with_exponential_backoff
from ..utils.rate_limiter import RateLimiter
from ..exceptions import InferraAPIError

class CompletionsAPI:
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
        prompt: str,
        stream: bool = False,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[Union[str, list[str]]] = None,
    ) -> Union[Completion, AsyncIterator[CompletionChunk]]:
        """
        Create a completion for the provided prompt and parameters.

        Args:
            model: ID of the model to use
            prompt: The prompt to generate completions for
            stream: Whether to stream the response
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum number of tokens to generate
            top_p: Nucleus sampling parameter
            frequency_penalty: Frequency penalty parameter
            presence_penalty: Presence penalty parameter
            stop: Up to 4 sequences where the API will stop generating

        Returns:
            If stream=False, returns a Completion
            If stream=True, returns an AsyncIterator of CompletionChunk
        """
        await self.rate_limiter.acquire()

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream
        }

        # Add optional parameters if provided
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if top_p is not None:
            payload["top_p"] = top_p
        if frequency_penalty is not None:
            payload["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            payload["presence_penalty"] = presence_penalty
        if stop is not None:
            payload["stop"] = stop

        try:
            response = await self.client.post(
                "/completions",
                json=payload,
                stream=stream
            )

            if stream:
                return self._handle_streaming_response(response)
            return Completion(**response.json())

        except Exception as e:
            raise InferraAPIError(f"Error creating completion: {str(e)}")

    async def _handle_streaming_response(
        self,
        response
    ) -> AsyncIterator[CompletionChunk]:
        """
        Handle streaming response from the completions API.
        
        Args:
            response: The streaming response from the API
            
        Yields:
            CompletionChunk objects containing partial completions
        """
        try:
            async for line in response.iter_lines():
                if line:
                    chunk = CompletionChunk.parse_raw(line)
                    yield chunk
        except Exception as e:
            raise InferraAPIError(f"Error processing streaming response: {str(e)}")

    async def create_batch(
        self,
        model: str,
        prompts: list[str],
        **kwargs
    ) -> list[Completion]:
        """
        Create completions for multiple prompts in parallel.

        Args:
            model: ID of the model to use
            prompts: List of prompts to generate completions for
            **kwargs: Additional parameters passed to create()

        Returns:
            List of Completion objects in the same order as the input prompts
        """
        tasks = [
            self.create(model=model, prompt=prompt, **kwargs)
            for prompt in prompts
        ]
        return await asyncio.gather(*tasks)
