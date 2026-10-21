from typing import Protocol

from unwritten_rules.application.embeddings.models import EmbeddedExperience
from unwritten_rules.application.retrieval.models import RetrievalResult

class SemanticRetriever(Protocol):
    def retriev(
        self,
        query_embedding: list[float],
        candidates: list[EmbeddedExperience],
        top_k: int,
    ) -> list[RetrievalResult]:
        ...
        