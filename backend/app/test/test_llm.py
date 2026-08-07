import asyncio
from app.services.llm_service import LLMService

async def main():
    llm_service = LLMService()
    prompt = "Hello, how are you?"
    response = await llm_service.generate(prompt)
    print(response)

if __name__ == "__main__":
    asyncio.run(main())