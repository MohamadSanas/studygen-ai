from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings

class LLMService:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=settings.MODEL_NAME,
            google_api_key=settings.GOOGLE_API_KEY,  
            max_tokens=settings.MAX_TOKENS
        )

    async def generate (self,prompt:str):
        response = await self.llm.ainvoke(prompt)
        return response.content