import pytest
import os
from inferra import InferraClient
from inferra.models.chat import Message

@pytest.mark.integration
@pytest.mark.asyncio
async def test_chat_completion_integration():
    client = InferraClient(api_key=os.getenv("INFERRA_API_KEY"))
    
    response = await client.chat.create(
        model="meta-llama/llama-3.1-8b-instruct/fp-8",
        messages=[
            Message(role="system", content="You are a helpful assistant."),
            Message(role="user", content="Say 'hello world'")
        ]
    )
    
    assert response.choices[0].message.content.lower().startswith("hello world")
    assert response.usage.prompt_tokens > 0
    assert response.usage.completion_tokens > 0

@pytest.mark.integration
@pytest.mark.asyncio
async def test_streaming_chat_integration():
    client = InferraClient(api_key=os.getenv("INFERRA_API_KEY"))
    
    chunks = []
    async for chunk in await client.chat.create(
        model="meta-llama/llama-3.1-8b-instruct/fp-8",
        messages=[
            Message(role="user", content="Count from 1 to 5.")
        ],
        stream=True
    ):
        chunks.append(chunk)
        if chunk.choices[0].finish_reason == "stop":
            break
    
    assert len(chunks) > 0
    complete_response = "".join(
        chunk.choices[0].delta.content
        for chunk in chunks
        if chunk.choices[0].delta.content
    )
    assert all(str(i) in complete_response for i in range(1, 6))
