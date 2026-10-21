import math

from unwritten_rules.application.embeddings.models import EmbeddedExperience
from unwritten_rules.application.retrieval.models import RetrievalResult


class InMemoryCosineRetriever:

    def retrieve(
        self,
        query_embedding: list[float],
        candidates: list[EmbeddedExperience],
        top_k: int,
    ) -> list[RetrievalResult]:

        if top_k <= 0:
            raise ValueError("top_k must be positive.")

        if not query_embedding:
            raise ValueError("Query embedding cannot be empty.")

        if not all(math.isfinite(value) for value in query_embedding):
            raise ValueError("Query embedding must contain finite values.")

        if not candidates:
            return []

        query_dimensions = len(query_embedding)
        query_norm = math.sqrt(
            math.fsum(value * value for value in query_embedding)
        )

        if query_norm == 0:
            raise ValueError("Query embedding cannot be a zero vector.")

        scored_candidates = []

        for candidate in candidates:
            if len(candidate.embedding) != query_dimensions:
                raise ValueError(
                    "Candidate embedding dimensions do not match query."
                )

            candidate_norm = math.sqrt(
                math.fsum(value * value for value in candidate.embedding)
            )

            if candidate_norm == 0:
                raise ValueError(
                    "Candidate embedding cannot be a zero vector."
                )

            dot_product = math.fsum(
                query_value * candidate_value
                for query_value, candidate_value
                in zip(query_embedding, candidate.embedding)
            )

            similarity = dot_product / (query_norm * candidate_norm)

            similarity = max(-1.0, min(1.0, similarity))

            scored_candidates.append(
                (candidate.record_id, similarity)
            )

        scored_candidates.sort(
            key=lambda item: (-item[1], item[0])
        )

        return [
            RetrievalResult(
                record_id=record_id,
                similarity_score=score,
                rank=index,
            )
            for index, (record_id, score) in enumerate(
                scored_candidates[:top_k],
                start=1,
            )
        ]