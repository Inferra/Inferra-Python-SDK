import pytest
import os
import json
from pathlib import Path
from inferra import InferraClient

@pytest.mark.integration
@pytest.mark.asyncio
async def test_batch_processing_integration():
    client = InferraClient(api_key=os.getenv("INFERRA_API_KEY"))
    
    # Read test batch input
    input_path = Path(__file__).parent.parent / "data" / "test_files" / "batch_input.jsonl"
    
    # Create batch file
    batch_file = await client.files.create(
        file=input_path,
        purpose="batch"
    )
    
    # Create batch
    batch = await client.batch.create(
        input_file_id=batch_file.id,
        completion_window="24h"
    )
    
    # Wait for completion
    completed_batch = await client.batch.wait_for_completion(
        batch.id,
        timeout=300,  # 5 minutes
        poll_interval=5
    )
    
    assert completed_batch.status == "completed"
    assert completed_batch.request_counts.completed == 2
    assert completed_batch.request_counts.failed == 0
    
    # Download results
    results = await client.files.download(completed_batch.output_file_id)
    result_lines = results.strip().split("\n")
    assert len(result_lines) == 2
    
    # Verify results
    for line in result_lines:
        result = json.loads(line)
        assert result["response"]["status_code"] == 200
        assert "capital" in result["response"]["body"]["choices"][0]["message"]["content"].lower()

@pytest.mark.integration
@pytest.mark.asyncio
async def test_batch_file_operations():
    client = InferraClient(api_key=os.getenv("INFERRA_API_KEY"))
    
    # List files
    files = await client.files.list(purpose="batch", limit=10)
    initial_count = len(files)
    
    # Create a test file
    test_data = [
        {"custom_id": "test-1", "content": "Test content 1"},
        {"custom_id": "test-2", "content": "Test content 2"}
    ]
    
    batch_file = await client.files.create(
        file=test_data,
        purpose="batch"
    )
    
    # Verify file was created
    files = await client.files.list(purpose="batch", limit=10)
    assert len(files) == initial_count + 1
    
    # Retrieve file info
    file_info = await client.files.retrieve(batch_file.id)
    assert file_info.purpose == "batch"
    assert file_info.status == "processed"
    
    # Clean up
    await client.files.delete(batch_file.id)
    
    # Verify deletion
    files = await client.files.list(purpose="batch", limit=10)
    assert len(files) == initial_count
