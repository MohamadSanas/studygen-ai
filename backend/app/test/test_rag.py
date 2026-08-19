import asyncio

from app.services.rag_service import RAGService


async def main():

    rag_service = RAGService()

    question = "What is a process?"

    result = await rag_service.ask(
        question=question,
        k=4,
    )

    print("=" * 80)
    print("QUESTION")
    print("=" * 80)
    print(question)

    print("\n" + "=" * 80)
    print("ANSWER")
    print("=" * 80)
    print(result["answer"])

    print("\n" + "=" * 80)
    print("SOURCES")
    print("=" * 80)

    for source in result["sources"]:
        print(source)


if __name__ == "__main__":
    asyncio.run(main())