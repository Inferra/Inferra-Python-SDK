import pytest
from inferra.models.batch import Batch, BatchFile
from inferra.exceptions import InferraAPIError

@pytest.mark.asyncio
async def test_create_batch(client, mocker, sample_responses):
    mock_response = mocker.AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = sample_responses["batch_status"]
    
    mocker.patch("aiohttp.ClientSession.request", return_value=mock_response)
    
    batch = await client.batch.create(
        input_file_id="file-123",
        completion_window="24h"
    )
    
    assert isinstance(batch, Batch)
    assert batch.status == "completed"
    assert batch.request_counts.total == 2

@pytest.mark.asyncio
async def test_batch_status_polling(client, mocker, sample_responses):
    mock_response = mocker.AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = sample_responses["batch_status"]
    
    mocker.patch("aiohttp.ClientSession.request", return_value=mock_response)
    
    batch = await client.batch.wait_for_completion(
        "batch_123",
        poll_interval=0.1,
        timeout=1
    )
    
    assert batch.status == "completed"
    assert batch.completed_at is not None
