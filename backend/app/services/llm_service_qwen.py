import httpx

from app.core.config import settings


class QwenLLMService:

    def __init__(self):
        self.api_url = settings.HF_API_URL
        self.api_token = settings.HF_TOKEN
        self.model = settings.HF_MODEL

    async def generate(self, question: str, context: str) -> str:
        prompt = f"""
            You are StudyGen AI, a university study assistant.
            {question}
            LECTURE MATERIAL:
            {context}
        """

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=180.0) as client:

            response = await client.post(
                self.api_url,
                headers=headers,
                json=payload
            )

            response.raise_for_status()

            data = response.json()

        try:
            return data["choices"][0]["message"]["content"]

        except (KeyError, IndexError, TypeError) as e:
            raise ValueError(
                f"Unexpected Hugging Face response: {data}"
            ) from e