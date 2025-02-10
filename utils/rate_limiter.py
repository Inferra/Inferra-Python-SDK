import asyncio
import time
from typing import Optional
from ..exceptions import InferraRateLimitError

class RateLimiter:
    def __init__(
        self,
        requests_per_minute: int,
        burst_size: Optional[int] = None
    ):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Number of requests allowed per minute
            burst_size: Maximum burst size (defaults to requests_per_minute)
        """
        self.rate = requests_per_minute / 60.0  # Convert to requests per second
        self.burst_size = burst_size or requests_per_minute
        self.tokens = self.burst_size
        self.last_update = time.monotonic()
        self.lock = asyncio.Lock()

    async def acquire(self, tokens: int = 1):
        """
        Acquire tokens from the bucket.
        
        Args:
            tokens: Number of tokens to acquire
            
        Raises:
            InferraRateLimitError: If rate limit is exceeded
        """
        async with self.lock:
            await self._refill()
            
            if self.tokens < tokens:
                required_time = (tokens - self.tokens) / self.rate
                raise InferraRateLimitError(
                    f"Rate limit exceeded. Try again in {required_time:.1f} seconds.",
                    retry_after=required_time
                )
            
            self.tokens -= tokens

    async def _refill(self):
        """Refill tokens based on time elapsed."""
        now = time.monotonic()
        elapsed = now - self.last_update
        self.tokens = min(
            self.burst_size,
            self.tokens + (elapsed * self.rate)
        )
        self.last_update = now
