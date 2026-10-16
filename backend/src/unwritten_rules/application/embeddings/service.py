
from collections.abc import Sequence

from unwritten_rules.application.embeddings.interfaces import EmbeddingModel
from unwritten_rules.application.embeddings.models import (
    EmbeddedExperience,
    EmbeddingConfig,
)
from unwritten_rules.application.preprocessing.models import (
    PreprocessedExperience,
)


class EmbeddingService:
    """Generate validated embeddings for preprocessed experiences."""

    def __init__(
        self,
        model: EmbeddingModel,
        config: EmbeddingConfig,
    ):
        if model.dimensions != config.dimensions:
            raise ValueError(
                "Configured dimensions do not match model dimensions."
            )

        self._model = model
        self._config = config

    def generate(
        self,
        records: Sequence[PreprocessedExperience],
    ) -> list[EmbeddedExperience]:
        """Generate embeddings while preserving record order."""

        if not records:
            return []

        texts = [record.retrieval_text for record in records]

        if any(not text.strip() for text in texts):
            raise ValueError(
                "Retrieval text cannot be empty."
            )

        vectors = self._model.encode(
            texts,
            batch_size=self._config.batch_size,
        )

        if len(vectors) != len(records):
            raise ValueError(
                "Embedding count does not match record count."
            )

        results = []

        for record, vector in zip(records, vectors):
            results.append(
                EmbeddedExperience(
                    record_id=str(record.experience.id),
                    embedding=vector,
                    model_name=self._config.model_name,
                    dimensions=self._config.dimensions,
                )
            )

        return results
