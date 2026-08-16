import asyncio

from app.services.llm_service import LLMService


async def main():
    llm = LLMService()

    response = await llm.generate(
        "Explain overfitting in machine learning in 3 simple sentences."
    )

    print("\n--- StudyGen AI Response ---")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())