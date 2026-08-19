from app.services.embedding_service import EmbeddingService


def main():
    service = EmbeddingService()

    text = "A process is a program in execution."

    embedding = service.embed_text(text)

    print("Embedding generated successfully")
    print("Vector type:", type(embedding))
    print("Vector dimensions:", len(embedding))
    print("First 5 values:", embedding[:5])


if __name__ == "__main__":
    main()