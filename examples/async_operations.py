import os
import asyncio
from inferra import InferraClient

async def process_conversation(client, conversation):
    response = await client.chat.create(
        model="meta-llama/llama-3.1-8b-instruct/fp-8",
        messages=conversation
    )
    return response.choices[0].message.content

async def main():
    client = InferraClient(api_key=os.getenv("INFERRA_API_KEY")) # Find this in your dashboard
    
    conversations = [
        [{"role": "user", "content": "Tell me a joke."}],
        [{"role": "user", "content": "Write a haiku."}],
        [{"role": "user", "content": "Give me a fun fact."}]
    ]
    
    # Process multiple conversations concurrently
    tasks = [process_conversation(client, conv) for conv in conversations]
    responses = await asyncio.gather(*tasks)
    
    for i, response in enumerate(responses):
        print(f"\nConversation {i + 1}:")
        print(response)

if __name__ == "__main__":
    asyncio.run(main())
