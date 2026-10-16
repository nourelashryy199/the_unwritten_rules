
import math

from sentence_transformers import SentenceTransformer


class SentenceTransformerAdapter:
    """Generate text embeddings using Sentence Transformers."""

    def __init__(self, model_name: str):
        if not model_name.strip():
            raise ValueError("Model name cannot be blank.")

        self._model = SentenceTransformer(model_name)

        dimensions = self._model.get_sentence_embedding_dimension()

        if dimensions is None or dimensions <= 0:
            raise ValueError(
                "The embedding model must report a positive dimensionality."
            )

        self._dimensions = dimensions

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def encode(
        self,
        texts: list[str],
        batch_size: int,
    ) -> list[list[float]]:
        if batch_size <= 0:
            raise ValueError("Batch size must be positive.")

        if not isinstance(texts, list):
            raise TypeError("Texts must be provided as a list.")

        if any(
            not isinstance(text, str) or not text.strip()
            for text in texts
        ):
            raise ValueError(
                "Every input must be a non-empty string."
            )

        if not texts:
            return []

        embeddings = self._model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
        )

        vectors = embeddings.tolist()

        if len(vectors) != len(texts):
            raise ValueError(
                "The model returned an unexpected number of embeddings."
            )

        for vector in vectors:
            if len(vector) != self._dimensions:
                raise ValueError(
                    "Embedding dimensionality does not match the model."
                )

            if not all(math.isfinite(value) for value in vector):
                raise ValueError(
                    "Embedding contains non-finite values."
                )

        return vectors
