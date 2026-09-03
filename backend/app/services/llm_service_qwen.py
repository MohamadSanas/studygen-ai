from time import time
from aiohttp import payload
import httpx

from app.core.config import settings

class QwenLLMService:

    def __init__(self):
        self.base_url = settings.QWEN_API_URL.strip('/')


    async def generate(self,question:str,context:str) -> str:
        payload = {
            "question":question,
            "context":context,
        }

        #use infer api 
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                f"{self.base_url}/generate",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        if "answer" not in data:
            raise ValueError(
                "Qwen API did not return 'answer' in response",
                data,
            )

        answer = data["answer"]

        return answer

        
            