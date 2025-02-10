from typing import Optional, Union, BinaryIO
from ..models.batch import BatchFile
from ..utils.retry import retry_with_exponential_backoff
from ..exceptions import InferraAPIError
import json
import aiohttp
from pathlib import Path

class FilesAPI:
    def __init__(self, client):
        self.client = client

    @retry_with_exponential_backoff(max_retries=3)
    async def create(
        self,
        file: Union[str, Path, BinaryIO, list],
        purpose: str = "batch"
    ) -> BatchFile:
        """
        Upload a file for batch processing.

        Args:
            file: File to upload. Can be:
                - Path to a file (str or Path)
                - File-like object
                - List of dictionaries (will be converted to JSONL)
            purpose: Purpose of the file (currently only "batch" is supported)

        Returns:
            BatchFile object containing the file details
        """
        try:
            # Handle different file input types
            if isinstance(file, (str, Path)):
                files = {'file': open(file, 'rb')}
            elif isinstance(file, list):
                # Convert list to JSONL
                jsonl_content = '\n'.join(json.dumps(item) for item in file)
                files = {
                    'file': ('batch.jsonl', jsonl_content.encode(), 'application/jsonl')
                }
            else:
                files = {'file': file}

            data = {'purpose': purpose}
            
            response = await self.client.post(
                "/files",
                data=data,
                files=files
            )
            
            return BatchFile(**response.json())

        except Exception as e:
            raise InferraAPIError(f"Error uploading file: {str(e)}")
        finally:
            # Close file if we opened it
            if isinstance(file, (str, Path)) and 'files' in locals():
                files['file'].close()

    async def retrieve(self, file_id: str) -> BatchFile:
        """
        Retrieve information about an uploaded file.

        Args:
            file_id: The ID of the file to retrieve

        Returns:
            BatchFile object containing the file details
        """
        try:
            response = await self.client.get(f"/files/{file_id}")
            return BatchFile(**response.json())
        except Exception as e:
            raise InferraAPIError(f"Error retrieving file {file_id}: {str(e)}")

    async def download(
        self,
        file_id: str,
        output_file: Optional[Union[str, Path]] = None
    ) -> Union[str, bytes]:
        """
        Download the content of an uploaded file.

        Args:
            file_id: The ID of the file to download
            output_file: Optional path to save the file to

        Returns:
            If output_file is None, returns the file content as string or bytes
            If output_file is provided, saves the file and returns None
        """
        try:
            response = await self.client.get(
                f"/files/{file_id}/content",
                stream=True
            )

            if output_file:
                with open(output_file, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        f.write(chunk)
                return None
            else:
                content = await response.read()
                try:
                    # Try to decode as UTF-8
                    return content.decode('utf-8')
                except UnicodeDecodeError:
                    # Return raw bytes if not UTF-8
                    return content

        except Exception as e:
            raise InferraAPIError(f"Error downloading file {file_id}: {str(e)}")

    async def delete(self, file_id: str) -> None:
        """
        Delete an uploaded file.

        Args:
            file_id: The ID of the file to delete
        """
        try:
            await self.client.delete(f"/files/{file_id}")
        except Exception as e:
            raise InferraAPIError(f"Error deleting file {file_id}: {str(e)}")

    async def list(
        self,
        purpose: Optional[str] = None,
        limit: int = 20,
        after: Optional[str] = None
    ) -> list[BatchFile]:
        """
        List uploaded files.

        Args:
            purpose: Filter files by purpose
            limit: Maximum number of files to return
            after: Return files after this file ID

        Returns:
            List of BatchFile objects
        """
        params = {"limit": limit}
        if purpose:
            params["purpose"] = purpose
        if after:
            params["after"] = after

        try:
            response = await self.client.get("/files", params=params)
            return [BatchFile(**file) for file in response.json()]
        except Exception as e:
            raise InferraAPIError(f"Error listing files: {str(e)}")
