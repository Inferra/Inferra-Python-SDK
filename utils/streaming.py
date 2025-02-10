from typing import AsyncIterator, Any
import json
from ..exceptions import InferraAPIError

class StreamProcessor:
    @staticmethod
    async def process_stream(response: AsyncIterator[bytes]) -> AsyncIterator[dict]:
        """
        Process a streaming response.
        
        Args:
            response: Raw streaming response
            
        Yields:
            Parsed JSON chunks
        """
        async for chunk in response:
            if chunk:
                # Remove 'data: ' prefix if present
                if chunk.startswith(b'data: '):
                    chunk = chunk[6:]
                
                # Skip keep-alive
                if chunk.strip() == b'':
                    continue
                
                try:
                    yield json.loads(chunk)
                except json.JSONDecodeError as e:
                    raise InferraAPIError(f"Error decoding streaming response: {str(e)}")

    @staticmethod
    def format_chunk(chunk: dict) -> str:
        """
        Format a chunk for display.
        
        Args:
            chunk: Response chunk
            
        Returns:
            Formatted string
        """
        if not chunk.get('choices'):
            return ''
        
        choice = chunk['choices'][0]
        if not choice.get('delta') or 'content' not in choice['delta']:
            return ''
            
        return choice['delta']['content']
