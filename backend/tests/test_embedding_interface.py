
from unwritten_rules.application.embeddings.interfaces import EmbeddingModel


class FakeEmbeddingModel:
    """Lightweight model for testing the interface."""

    @property
    def dimensions(self) -> int:
        return 3

    def encode(
        self,
        texts: list[str],
        batch_size: int,
    ) -> list[list[float]]:
        return [
            [float(len(text)), 1.0, 0.5]
            for text in texts
        ]


def test_fake_model_implements_embedding_interface():
    model: EmbeddingModel = FakeEmbeddingModel()

    assert model.dimensions == 3


def test_embedding_interface_supports_batch_processing():
    model: EmbeddingModel = FakeEmbeddingModel()

    embeddings = model.encode(
        ["First experience", "Second experience"],
        batch_size=2,
    )

    assert len(embeddings) == 2
    assert all(len(vector) == 3 for vector in embeddings)


def test_embedding_interface_handles_empty_batch():
    model: EmbeddingModel = FakeEmbeddingModel()

    embeddings = model.encode([], batch_size=2)

    assert embeddings == []
