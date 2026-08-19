from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings


class LLMService:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=settings.MODEL_NAME,
            google_api_key=settings.GOOGLE_API_KEY,
            max_tokens=settings.MAX_TOKENS,
            temperature=0,
        )

    async def generate(self, prompt: str) -> str:
        response = await self.llm.ainvoke(prompt)

        if isinstance(response.content, str):
            return response.content

        return "".join(
            block["text"]
            for block in response.content
            if block.get("type") == "text"
        )

    async def generate_structured(self, prompt: str, schema):
        structured_llm = self.llm.with_structured_output(
            schema,
            method="json_schema",
        )

        return await structured_llm.ainvoke(prompt)