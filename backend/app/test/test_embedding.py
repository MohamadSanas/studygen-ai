from app.services.embedding_service import EmbeddingService

service = EmbeddingService()

embedding = service.get_embeddings().embed_query(
    "The CPU executes instructions."
)

print(type(embedding))
print(len(embedding))
print(embedding[:10])