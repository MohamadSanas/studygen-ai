import asyncio
from pathlib import Path

from app.services.past_paper_processor import PastPaperProcessor


async def main():

    processor = PastPaperProcessor()

    base_dir = Path(__file__).resolve().parents[2]

    pdf_path = (
        base_dir
        / "test_data"
        / "EC9630.pdf"
    )

    if not pdf_path.exists():
        print("Past paper not found:")
        print(pdf_path)
        return

    result = await processor.process(
        file_path=pdf_path,
        document_id="ec9630-2024",
        year=2024,
    )

    print("\nPast paper processed successfully")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())