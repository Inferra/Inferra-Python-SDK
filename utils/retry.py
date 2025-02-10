import asyncio
from functools import wraps
from typing import Type, Union, Tuple, Optional
from ..exceptions import InferraAPIError, InferraRateLimitError

def retry_with_exponential_backoff(
    max_retries: int = 3,
    initial_delay: float = 1,
    max_delay: float = 60,
    exponential_base: float = 2,
    retry_on: Optional[Union[Type[Exception], Tuple[Type[Exception], ...]]] = None
):
    """
    Decorator that retries an async function with exponential backoff.
    
    Args:
        max_retries: Maximum number of retries
        initial_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential_base: Base for exponential backoff
        retry_on: Exception or tuple of exceptions to retry on
    """
    if retry_on is None:
        retry_on = (InferraAPIError,)

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except retry_on as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        raise last_exception
                    
                    if isinstance(e, InferraRateLimitError):
                        # Use retry-after header if available
                        retry_after = getattr(e, 'retry_after', None)
                        if retry_after is not None:
                            delay = float(retry_after)
                    
                    # Calculate next delay with exponential backoff
                    await asyncio.sleep(min(delay, max_delay))
                    delay *= exponential_base
                
                except Exception as e:
                    # Don't retry on unspecified exceptions
                    raise e

            raise last_exception

        return wrapper
    return decorator
