import os
import asyncio
from inferra import InferraClient

async def main():
    client = InferraClient(api_key=os.getenv("INFERRA_API_KEY")) # Add the key you get from the dashbpard
    
    # Create batch input file
    batch_input = [
        {
            "custom_id": "request-1",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": "meta-llama/llama-3.1-8b-instruct/fp-8",
                "messages": [{"role": "user", "content": "What is the capital of France?"}]
            }
        },
        {
            "custom_id": "request-2",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": "meta-llama/llama-3.1-8b-instruct/fp-8",
                "messages": [{"role": "user", "content": "What is the capital of Germany?"}]
            }
        }
    ]
    
    # Upload batch file
    batch_file = await client.files.create(
        file=batch_input,
        purpose="batch"
    )
    
    # Create and start batch
    batch = await client.batch.create(
        input_file_id=batch_file.id,
        completion_window="24h"
    )
    
    # Poll for completion
    while True:
        status = await client.batch.retrieve(batch.id)
        if status.status in ["completed", "failed"]:
            break
        await asyncio.sleep(5)
    
    # Get results
    if status.status == "completed":
        results = await client.files.retrieve(status.output_file_id)
        print(results)

if __name__ == "__main__":
    asyncio.run(main())
