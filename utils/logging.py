import logging
import json
from typing import Any, Optional
from datetime import datetime

class InferraLogger:
    def __init__(
        self,
        name: str = "inferra",
        level: int = logging.INFO,
        log_file: Optional[str] = None,
        format_string: Optional[str] = None
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        if not format_string:
            format_string = "[%(asctime)s] %(levelname)s [%(name)s] %(message)s"
        
        formatter = logging.Formatter(format_string)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler (optional)
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def _format_request(self, method: str, url: str, **kwargs) -> str:
        """Format request details for logging."""
        return json.dumps({
            "method": method,
            "url": url,
            "params": kwargs.get("params"),
            "headers": kwargs.get("headers", {})
        }, default=str)

    def _format_response(self, response: Any) -> str:
        """Format response details for logging."""
        if hasattr(response, "status_code"):
            return json.dumps({
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "length": len(response.content) if hasattr(response, "content") else None
            }, default=str)
        return str(response)

    def log_request(self, method: str, url: str, **kwargs):
        """Log API request details."""
        self.logger.info(
            f"API Request: {self._format_request(method, url, **kwargs)}"
        )

    def log_response(self, response: Any, elapsed: float):
        """Log API response details."""
        self.logger.info(
            f"API Response ({elapsed:.2f}s): {self._format_response(response)}"
        )

    def log_error(self, error: Exception, context: Optional[dict] = None):
        """Log error details with context."""
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {}
        }
        self.logger.error(f"Error: {json.dumps(error_data, default=str)}")

    def log_rate_limit(self, remaining: int, reset: datetime):
        """Log rate limit information."""
        self.logger.info(
            f"Rate limit - Remaining: {remaining}, Reset: {reset.isoformat()}"
        )

# Usage in client.py:
# Add to imports:
# from .utils.logging import InferraLogger

# Add to InferraClient.__init__:
# self.logger = InferraLogger()

# Add to request method:
# self.logger.log_request(method, path, **kwargs)
# start_time = time.time()
# try:
#     response = ...
#     self.logger.log_response(response, time.time() - start_time)
# except Exception as e:
#     self.logger.log_error(e, {"method": method, "path": path})
#     raise
