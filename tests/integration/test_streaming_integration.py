import pytest
import os
import asyncio
from inferra import InferraClient
from inferra.models.chat import Message
from inferra.exceptions import InferraAPIError

@pytest.mark.integration
@pytest.mark.asyncio
async def test_streaming_chat_completion():
    client = InferraClient(api_key=os.getenv("INFERRA_API_KEY"))
    
    chunks = []
    content = []
    
    async for chunk in await client.chat.create(
        model="meta-llama/llama-3.1-8b-instruct/fp-8",
        messages=[
            Message(role="system", content="You are a helpful assistant."),
            Message(role="user", content="Write a short poem about coding.")
        ],
        stream=True
    ):
        chunks.append(chunk)
        if chunk.choices[0].delta.content:
            content.append(chunk.choices[0].delta.content)
    
    complete_response = "".join(content)
    
    assert len(chunks) > 0
    assert len(complete_response) > 0
    assert "poem" in complete_response.lower() or "verse" in complete_response.lower()
    assert chunks[-1].choices[0].finish_reason == "stop"

@pytest.mark.integration
@pytest.mark.asyncio
async def test_streaming_error_handling():
    client = InferraClient(api_key=os.getenv("INFERRA_API_KEY"))
    
    with pytest.raises(InferraAPIError):
        async for chunk in await client.chat.create(
            model="nonexistent-model",
            messages=[Message(role="user", content="Hello")],
            stream=True
        ):
            pass

@pytest.mark.integration
@pytest.mark.asyncio
async def test_concurrent_streaming():
    client = InferraClient(api_key=os.getenv("INFERRA_API_KEY"))
    
    async def process_stream(prompt):
        content = []
        async for chunk in await client.chat.create(
            model="meta-llama/llama-3.1-8b-instruct/fp-8",
            messages=[Message(role="user", content=prompt)],
            stream=True
        ):
            if chunk.choices[0].delta.content:
                content.append(chunk.choices[0].delta.content)
        return "".join(content)
    
    prompts = [
        "Write a haiku about programming.",
        "Write a haiku about debugging.",
        "Write a haiku about testing."
    ]
    
    responses = await asyncio.gather(*[
        process_stream(prompt) for prompt in prompts
    ])
    
    assert len(responses) == len(prompts)
    for response in responses:
        assert len(response) > 0
        assert "haiku" in response.lower() or "\n" in response

@pytest.mark.integration
@pytest.mark.asyncio
async def test_streaming_rate_limiting():
    client = InferraClient(
        api_key=os.getenv("INFERRA_API_KEY"),
        requests_per_minute=10  # Set a low limit for testing
    )
    
    start_time = asyncio.get_event_loop().time()
    
    # Make multiple requests that should trigger rate limiting
    for _ in range(5):
        async for chunk in await client.chat.create(
            model="meta-llama/llama-3.1-8b-instruct/fp-8",
            messages=[Message(role="user", content="Hello")],
            stream=True
        ):
            if chunk.choices[0].finish_reason == "stop":
                break
    
    elapsed_time = asyncio.get_event_loop().time() - start_time
    
    # Verify that rate limiting added some delay
    assert elapsed_time > 2.0  # Should take at least 2 seconds due to rate limiting

@pytest.mark.integration
@pytest.mark.asyncio
async def test_streaming_timeout():
    client = InferraClient(
        api_key=os.getenv("INFERRA_API_KEY"),
        timeout=1.0  # Set a very short timeout
    )
    
    with pytest.raises(InferraAPIError, match="Request failed: TimeoutError"):
        async for chunk in await client.chat.create(
            model="meta-llama/llama-3.1-8b-instruct/fp-8",
            messages=[
                Message(
                    role="user",
                    content="Write a very long essay about artificial intelligence."
                )
            ],
            stream=True
        ):
            await asyncio.sleep(2)  # Force timeout
