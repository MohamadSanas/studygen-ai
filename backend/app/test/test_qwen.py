import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://router.huggingface.co/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {os.environ['HF_TOKEN']}",
    "Content-Type": "application/json",
}

response = requests.post(
    API_URL,
    headers=headers,
    json={
        "model": "Qwen/Qwen3.8-2.4T-A95B:novita",
        "messages": [
            {
                "role": "user",
                "content": "What is the capital of France?"
            }
        ]
    }
)

response.raise_for_status()

data = response.json()

print(data["choices"][0]["message"]["content"])