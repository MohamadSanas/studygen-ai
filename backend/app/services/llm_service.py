import httpx

from app.core.config import settings


class LLMService:
    def __init__(self):
        self.api_url = settings.HF_API_URL
        self.api_token = settings.HF_TOKEN
        self.model = settings.HF_MODEL

    async def generate(self, prompt: str) -> str:
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

    async def generate_structured(self, prompt: str, schema):
        """
        Generate structured JSON output from the LLM.

        The schema should be a Pydantic model.
        """

        schema_json = schema.model_json_schema()

        structured_prompt = f"""
{prompt}

Return the answer ONLY as valid JSON.

The JSON must follow this schema:

{schema_json}
"""

        result = await self.generate(structured_prompt)

        return result