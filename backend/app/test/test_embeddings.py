from app.services.embedding_service import EmbeddingService


def main():
    embedding_service = EmbeddingService()

    text = "Overfitting occurs when a model learns the training data too closely."

    vector = embedding_service.embed_text(text)

    print("Embedding generated successfully")
    print("Vector type:", type(vector))
    print("Vector dimensions:", len(vector))
    print("First 10 values:", vector[:10])


if __name__ == "__main__":
    main()