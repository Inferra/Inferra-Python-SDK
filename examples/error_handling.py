import os
from inferra import InferraClient, InferraAPIError, InferraRateLimitError

def main():
    client = InferraClient(api_key=os.getenv("INFERRA_API_KEY")) # Find this in your dashboard
    
    try:
        response = client.chat.create(
            model="nonexistent-model",
            messages=[
                {"role": "user", "content": "Hello!"}
            ]
        )
    except InferraAPIError as e:
        print(f"API Error: {e}")
    except InferraRateLimitError as e:
        print(f"Rate limit exceeded: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
