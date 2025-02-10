from typing import Optional, Dict, Any
from ..models.batch import Batch, BatchFile
from ..utils.retry import retry_with_exponential_backoff
from ..exceptions import InferraAPIError
import json
import asyncio

class BatchAPI:
    def __init__(self, client):
        self.client = client

    @retry_with_exponential_backoff(max_retries=3)
    async def create(
        self,
        input_file_id: str,
        completion_window: str = "24h",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Batch:
        """
        Create a new batch processing job.

        Args:
            input_file_id: ID of the uploaded input file
            completion_window: Time window for batch completion (e.g., "24h")
            metadata: Optional metadata to associate with the batch

        Returns:
            Batch object containing the batch job details
        """
        payload = {
            "input_file_id": input_file_id,
            "completion_window": completion_window,
        }
        
        if metadata:
            payload["metadata"] = metadata

        try:
            response = await self.client.post("/batch", json=payload)
            return Batch(**response.json())
        except Exception as e:
            raise InferraAPIError(f"Error creating batch: {str(e)}")

    async def retrieve(self, batch_id: str) -> Batch:
        """
        Retrieve the status of a batch processing job.

        Args:
            batch_id: The ID of the batch to retrieve

        Returns:
            Batch object containing the current status
        """
        try:
            response = await self.client.get(f"/batch/{batch_id}")
            return Batch(**response.json())
        except Exception as e:
            raise InferraAPIError(f"Error retrieving batch {batch_id}: {str(e)}")

    async def list(
        self,
        limit: int = 20,
        after: Optional[str] = None
    ) -> list[Batch]:
        """
        List batch processing jobs.

        Args:
            limit: Maximum number of batches to return
            after: Return batches after this batch ID

        Returns:
            List of Batch objects
        """
        params = {"limit": limit}
        if after:
            params["after"] = after

        try:
            response = await self.client.get("/batch", params=params)
            return [Batch(**batch) for batch in response.json()]
        except Exception as e:
            raise InferraAPIError(f"Error listing batches: {str(e)}")

    async def wait_for_completion(
        self,
        batch_id: str,
        timeout: float = 86400,  # 24 hours
        poll_interval: float = 5
    ) -> Batch:
        """
        Wait for a batch job to complete.

        Args:
            batch_id: The ID of the batch to wait for
            timeout: Maximum time to wait in seconds
            poll_interval: Time between status checks in seconds

        Returns:
            Completed Batch object

        Raises:
            TimeoutError: If the batch doesn't complete within the timeout
        """
        start_time = asyncio.get_event_loop().time()
        
        while True:
            batch = await self.retrieve(batch_id)
            
            if batch.status in ["completed", "failed", "cancelled", "expired"]:
                return batch
            
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise TimeoutError(f"Batch {batch_id} did not complete within {timeout} seconds")
            
            await asyncio.sleep(poll_interval)

    async def cancel(self, batch_id: str) -> Batch:
        """
        Cancel a batch processing job.

        Args:
            batch_id: The ID of the batch to cancel

        Returns:
            Updated Batch object
        """
        try:
            response = await self.client.post(f"/batch/{batch_id}/cancel")
            return Batch(**response.json())
        except Exception as e:
            raise InferraAPIError(f"Error cancelling batch {batch_id}: {str(e)}")
