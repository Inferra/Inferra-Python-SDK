class InferraError(Exception):
    """Base exception for all Inferra errors."""
    pass

class InferraAPIError(InferraError):
    """Raised when the API returns an error."""
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response

class InferraRateLimitError(InferraAPIError):
    """Raised when rate limits are exceeded."""
    def __init__(self, message: str, retry_after: float = None):
        super().__init__(message)
        self.retry_after = retry_after

class InferraAuthenticationError(InferraAPIError):
    """Raised when authentication fails."""
    pass

class InferraValidationError(InferraError):
    """Raised when input validation fails."""
    pass
