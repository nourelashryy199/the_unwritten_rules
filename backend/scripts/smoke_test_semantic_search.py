from unwritten_rules.application.embeddings.models import (
    EmbeddedExperience,
    EmbeddingConfig,
)
from unwritten_rules.application.retrieval.models import RetrievalConfig
from unwritten_rules.application.retrieval.service import SemanticSearchService
from unwritten_rules.infrastructure.embeddings.sentence_transformer import (
    SentenceTransformerAdapter,
)
from unwritten_rules.infrastructure.retrieval.in_memory import (
    InMemoryCosineRetriever,
)


def main() -> None:
    config = EmbeddingConfig()

    embedding_model = SentenceTransformerAdapter(
        model_name=config.model_name
    )

    experiences = {
        "EXP-001": "I declined a friend's invitation, and they seemed offended.",
        "EXP-002": "My colleague expected me to respond to work messages after hours.",
        "EXP-003": "I offered to split the restaurant bill, but my friend insisted on paying.",
        "EXP-004": "My friend was upset because I didn't explain why I couldn't attend.",
    }

    experience_ids = list(experiences.keys())
    experience_texts = list(experiences.values())

    vectors = embedding_model.encode(
        experience_texts,
        batch_size=config.batch_size,
    )

    candidates = [
        EmbeddedExperience(
            record_id=record_id,
            embedding=vector,
            model_name=config.model_name,
            dimensions=config.dimensions,
        )
        for record_id, vector in zip(
            experience_ids,
            vectors,
            strict=True,
        )
    ]

    service = SemanticSearchService(
        embedding_model=embedding_model,
        retriever=InMemoryCosineRetriever(),
        embedding_config=config,
        retrieval_config=RetrievalConfig(top_k=3),
    )

    query = "Why did my friend get upset when I said I couldn't come?"

    results = service.search(query, candidates)

    print(f"\nQuery: {query}\n")

    for result in results:
        print(
            f"Rank {result.rank} | "
            f"Similarity: {result.similarity_score:.4f} | "
            f"ID: {result.record_id}"
        )
        print(f"Experience: {experiences[result.record_id]}\n")


if __name__ == "__main__":
    main()