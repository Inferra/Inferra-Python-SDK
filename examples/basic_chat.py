import os
from inferra import InferraClient

def main():
    client = InferraClient(api_key=os.getenv("INFERRA_API_KEY"))
    
    response = client.chat.create(
        model="meta-llama/llama-3.1-8b-instruct/fp-8",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the meaning of life?"}
        ]
    )
    
    print(response.choices[0].message.content)

if __name__ == "__main__":
    main()
