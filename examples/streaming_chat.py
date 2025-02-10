import os
import asyncio
from inferra import InferraClient

async def main():
    client = InferraClient(api_key=os.getenv("INFERRA_API_KEY"))
    
    async for chunk in await client.chat.create(
        model="meta-llama/llama-3.1-8b-instruct/fp-8",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Write a story about a space adventure."}
        ],
        stream=True
    ):
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
