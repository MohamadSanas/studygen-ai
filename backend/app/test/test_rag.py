import asyncio

from app.services.rag_service import RAGService


async def main():

    rag = RAGService()

    question = "What programming languages does this person know?"

    result = await rag.ask(question)

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