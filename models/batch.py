from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime

class BatchFile(BaseModel):
    """A file used in batch processing."""
    id: str = Field(..., description="Unique identifier for the file")
    object: str = Field("file", description="Object type")
    purpose: str = Field(..., description="Purpose of the file (e.g., 'batch')")
    filename: str = Field(..., description="Name of the uploaded file")
    size: int = Field(..., description="Size of the file in bytes")
    created_at: int = Field(..., description="Unix timestamp of when the file was created")
    status: str = Field(..., description="Status of the file (e.g., 'processed')")

class BatchRequestCounts(BaseModel):
    """Counts of requests in a batch."""
    total: int = Field(..., description="Total number of requests in the batch")
    completed: int = Field(..., description="Number of completed requests")
    failed: int = Field(..., description="Number of failed requests")

class Batch(BaseModel):
    """A batch processing job."""
    id: str = Field(..., description="Unique identifier for the batch")
    object: str = Field("batch", description="Object type")
    status: str = Field(..., description="Status of the batch")
    input_file_id: str = Field(..., description="ID of the input file")
    output_file_id: Optional[str] = Field(None, description="ID of the output file")
    error_file_id: Optional[str] = Field(None, description="ID of the error file")
    completion_window: str = Field(..., description="Time window for completion")
    created_at: int = Field(..., description="Unix timestamp of creation")
    in_progress_at: Optional[int] = Field(None, description="When processing started")
    completed_at: Optional[int] = Field(None, description="When processing completed")
    failed_at: Optional[int] = Field(None, description="When processing failed")
    expired_at: Optional[int] = Field(None, description="When the batch expired")
    request_counts: BatchRequestCounts = Field(..., description="Request counts")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Custom metadata")
