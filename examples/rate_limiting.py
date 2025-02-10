import os
import asyncio
from inferra import InferraClient

async def make_request(client, message):
    try:
        response = await client.chat.create(
            model="meta-llama/llama-3.1-8b-instruct/fp-8",
            messages=[{"role": "user", "content": message}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

async def main():
    client = InferraClient(api_key=os.getenv("INFERRA_API_KEY"))
    
    # Create many concurrent requests
    messages = [f"Write a one-line story #{i}" for i in range(100)]
    
    # The client's built-in rate limiter will handle throttling
    tasks = [make_request(client, msg) for msg in messages]
    results = await asyncio.gather(*tasks)
    
    for i, result in enumerate(results):
        print(f"Request {i}: {result}")

if __name__ == "__main__":
    asyncio.run(main())
