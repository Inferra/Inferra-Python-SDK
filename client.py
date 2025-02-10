import aiohttp
from typing import Optional, Union, AsyncIterator
from .config import Config
from .api import ChatAPI, CompletionsAPI, BatchAPI, FilesAPI
from .exceptions import (
    InferraAPIError,
    InferraAuthenticationError,
    InferraRateLimitError
)

class InferraClient:
    """
    Main client for interacting with the Inferra API.
    
    Args:
        api_key: Inferra API key
        base_url: Base URL for API requests
        timeout: Request timeout in seconds
        max_retries: Maximum number of retries for failed requests
        requests_per_minute: Rate limit for requests
    """
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.inferra.net/v1",
        timeout: float = 60.0,
        max_retries: int = 3,
        requests_per_minute: int = 500
    ):
        self.config = Config(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            requests_per_minute=requests_per_minute
        )
        
        self._session = None
        
        # Initialize API interfaces
        self.chat = ChatAPI(self)
        self.completions = CompletionsAPI(self)
        self.batch = BatchAPI(self)
        self.files = FilesAPI(self)

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json",
                }
            )
        return self._session

    async def close(self):
        """Close the client session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def request(
        self,
        method: str,
        path: str,
        **kwargs
    ) -> Union[dict, AsyncIterator[dict]]:
        """
        Make a request to the API.
        
        Args:
            method: HTTP method
            path: API endpoint path
            **kwargs: Additional request parameters
            
        Returns:
            Response data
        """
        session = await self._get_session()
        
        url = f"{self.config.base_url.rstrip('/')}/{path.lstrip('/')}"
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        
        try:
            async with session.request(method, url, timeout=timeout, **kwargs) as response:
                if response.status == 429:
                    retry_after = response.headers.get("Retry-After", "60")
                    raise InferraRateLimitError(
                        "Rate limit exceeded",
                        retry_after=float(retry_after)
                    )
                
                if response.status == 401:
                    raise InferraAuthenticationError("Invalid API key")
                
                if response.status != 200:
                    error_data = await response.json()
                    raise InferraAPIError(
                        f"API request failed: {error_data.get('error', {}).get('message', 'Unknown error')}",
                        status_code=response.status,
                        response=error_data
                    )
                
                if kwargs.get("stream", False):
                    return response.content
                
                return await response.json()
                
        except aiohttp.ClientError as e:
            raise InferraAPIError(f"Request failed: {str(e)}")

    # Convenience methods
    async def get(self, path: str, **kwargs):
        """Make a GET request."""
        return await self.request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs):
        """Make a POST request."""
        return await self.request("POST", path, **kwargs)

    async def delete(self, path: str, **kwargs):
        """Make a DELETE request."""
        return await self.request("DELETE", path, **kwargs)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._session and not self._session.closed:
            self._session.close()
