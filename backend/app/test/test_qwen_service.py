import asyncio

from app.services.llm_service_qwen import QwenLLMService


async def main():
    qwen = QwenLLMService()

    answer = await qwen.generate(
        question="What is overfitting?",
        context=(
            "Overfitting occurs when a machine learning model "
            "learns the training data too closely and performs "
            "poorly on unseen data."
        ),
    )

    print("\n--- Qwen Response ---")
    print(answer)


if __name__ == "__main__":
    asyncio.run(main())