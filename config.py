import os
from typing import Optional

class Config:
    """Global configuration settings."""
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.inferra.net/v1",
        timeout: float = 60.0,
        max_retries: int = 3,
        requests_per_minute: int = 500
    ):
        self.api_key = api_key or os.getenv("INFERRA_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided or set in INFERRA_API_KEY environment variable")
            
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.requests_per_minute = requests_per_minute
