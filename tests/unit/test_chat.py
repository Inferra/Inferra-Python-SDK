import pytest
from inferra.models.chat import Message, ChatCompletion
from inferra.exceptions import InferraAPIError

@pytest.mark.asyncio
async def test_chat_completion(client, mocker, sample_responses):
    mock_response = mocker.AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = sample_responses["chat_completion"]
    
    mocker.patch("aiohttp.ClientSession.request", return_value=mock_response)
    
    response = await client.chat.create(
        model="meta-llama/llama-3.1-8b-instruct/fp-8",
        messages=[
            Message(role="user", content="What is the meaning of life?")
        ]
    )
    
    assert isinstance(response, ChatCompletion)
    assert response.choices[0].message.content.startswith("The meaning of life")

@pytest.mark.asyncio
async def test_chat_completion_streaming(client, mocker, sample_responses):
    mock_response = mocker.AsyncMock()
    mock_response.status = 200
    mock_response.content.iter_lines.return_value = [
        b'data: ' + str(sample_responses["streaming_chunk"]).encode()
    ]
    
    mocker.patch("aiohttp.ClientSession.request", return_value=mock_response)
    
    chunks = []
    async for chunk in await client.chat.create(
        model="meta-llama/llama-3.1-8b-instruct/fp-8",
        messages=[Message(role="user", content="Hi")],
        stream=True
    ): 
        chunks.append(chunk)
    
    assert len(chunks) > 0
    assert chunks[0].choices[0].delta.content == "The meaning"
