from collections.abc import Sequence

from unwritten_rules.application.embeddings.interfaces import EmbeddingModel
from unwritten_rules.application.embeddings.models import (
    EmbeddedExperience,
    EmbeddingConfig,
)
from unwritten_rules.application.retrieval.interfaces import SemanticRetriever
from unwritten_rules.application.retrieval.models import (
    RetrievalConfig,
    RetrievalResult,
)


class SemanticSearchService:

    def __init__(
        self,
        embedding_model: EmbeddingModel,
        retriever: SemanticRetriever,
        embedding_config: EmbeddingConfig,
        retrieval_config: RetrievalConfig,
    ) -> None:
        if embedding_model.dimensions != embedding_config.dimensions:
            raise ValueError(
                "Embedding model dimensions do not match configuration."
            )

        self._embedding_model = embedding_model
        self._retriever = retriever
        self._embedding_config = embedding_config
        self._retrieval_config = retrieval_config

    def search(
        self,
        query: str,
        candidates: Sequence[EmbeddedExperience],
    ) -> list[RetrievalResult]:
        if not isinstance(query, str):
            raise TypeError("Query must be a string.")

        normalized_query = query.strip()

        if not normalized_query:
            raise ValueError("Query cannot be empty or whitespace-only.")

        if not candidates:
            return []

        for candidate in candidates:
            if candidate.model_name != self._embedding_config.model_name:
                raise ValueError(
                    "Candidate embedding model does not match configuration."
                )

            if candidate.dimensions != self._embedding_config.dimensions:
                raise ValueError(
                    "Candidate embedding dimensions do not match configuration."
                )

        query_embeddings = self._embedding_model.encode(
            [normalized_query],
            batch_size=self._embedding_config.batch_size,
        )

        if len(query_embeddings) != 1:
            raise ValueError(
                "Embedding model must return exactly one query embedding."
            )

        query_embedding = query_embeddings[0]

        if len(query_embedding) != self._embedding_config.dimensions:
            raise ValueError(
                "Query embedding dimensions do not match configuration."
            )

        return self._retriever.retrieve(
            query_embedding=query_embedding,
            candidates=list(candidates),
            top_k=self._retrieval_config.top_k,
        )