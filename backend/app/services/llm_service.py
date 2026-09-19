import logging
from typing import List, Dict, Optional
import httpx

from app.core.config import settings
from app.services.llm_service_qwen_local import QwenLLMServiceLocal

logger = logging.getLogger(__name__)


class CloudLLMService:
    """Production Cloud LLM Service (Hugging Face / Router API)."""

    def __init__(self):
        self.api_url = settings.HF_API_URL
        self.api_token = settings.HF_TOKEN
        self.model = settings.HF_MODEL or "Qwen/Qwen2.5-7B-Instruct"

    async def generate(
        self,
        question: str = "",
        context: str = "",
        chat_history: Optional[List[Dict[str, str]]] = None,
        prompt: Optional[str] = None,
    ) -> str:
        if not self.api_url or not self.api_token:
            raise ValueError("HF_API_URL and HF_TOKEN must be configured for production Cloud LLM.")

        chat_history = chat_history or []
        user_content = prompt if prompt else f"QUESTION:\n{question}\n\nLECTURE MATERIAL:\n{context}"

        messages = [
            {
                "role": "system",
                "content": (
                    "You are StudyGen AI, a university study assistant. "
                    "Answer questions using the provided lecture material. "
                    "Do not invent information that is not present in the material."
                ),
            }
        ]
        for msg in chat_history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_content})

        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
        }

        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            raise ValueError(f"Unexpected Cloud response format: {data}") from e


def get_llm_service():
    """
    Factory that returns:
    - QwenLLMServiceLocal (Free, offline) during development / testing
    - CloudLLMService in production
    """
    is_prod = (
        settings.ENVIRONMENT.lower() == "production" 
        or getattr(settings, "LLM_PROVIDER", "") == "huggingface"
    )

    if is_prod:
        logger.info("[LLM Factory] Using Production Cloud LLM Service.")
        return CloudLLMService()
    else:
        logger.info("[LLM Factory] Using Local Ollama (Free dev/test mode).")
        return QwenLLMServiceLocal()


# Default instance
llm_service = get_llm_service()
