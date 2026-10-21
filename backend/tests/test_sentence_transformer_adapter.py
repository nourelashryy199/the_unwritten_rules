
from unittest.mock import MagicMock, patch

import pytest

from unwritten_rules.infrastructure.embeddings.sentence_transformer import (
    SentenceTransformerAdapter,
)


@pytest.fixture
def mock_model():
    model = MagicMock()
    model.get_embedding_dimension.return_value = 3

    model.encode.return_value.tolist.return_value = [
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
    ]

    return model


def test_adapter_loads_configured_model(mock_model):
    with patch(
        "unwritten_rules.infrastructure.embeddings.sentence_transformer.SentenceTransformer",
        return_value=mock_model,
    ) as constructor:
        adapter = SentenceTransformerAdapter("test-model")

    constructor.assert_called_once_with("test-model")
    assert adapter.dimensions == 3


def test_adapter_generates_batch_embeddings(mock_model):
    with patch(
        "unwritten_rules.infrastructure.embeddings.sentence_transformer.SentenceTransformer",
        return_value=mock_model,
    ):
        adapter = SentenceTransformerAdapter("test-model")

        vectors = adapter.encode(
            ["First experience", "Second experience"],
            batch_size=2,
        )

    assert vectors == [
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
    ]

    mock_model.encode.assert_called_once_with(
        ["First experience", "Second experience"],
        batch_size=2,
        convert_to_numpy=True,
    )


def test_adapter_handles_empty_batch(mock_model):
    with patch(
        "unwritten_rules.infrastructure.embeddings.sentence_transformer.SentenceTransformer",
        return_value=mock_model,
    ):
        adapter = SentenceTransformerAdapter("test-model")

        assert adapter.encode([], batch_size=2) == []

    mock_model.encode.assert_not_called()


@pytest.mark.parametrize("batch_size", [0, -1])
def test_adapter_rejects_invalid_batch_size(mock_model, batch_size):
    with patch(
        "unwritten_rules.infrastructure.embeddings.sentence_transformer.SentenceTransformer",
        return_value=mock_model,
    ):
        adapter = SentenceTransformerAdapter("test-model")

        with pytest.raises(ValueError, match="Batch size"):
            adapter.encode(["Experience"], batch_size=batch_size)


def test_adapter_rejects_blank_text(mock_model):
    with patch(
        "unwritten_rules.infrastructure.embeddings.sentence_transformer.SentenceTransformer",
        return_value=mock_model,
    ):
        adapter = SentenceTransformerAdapter("test-model")

        with pytest.raises(ValueError, match="non-empty"):
            adapter.encode(["   "], batch_size=2)


def test_adapter_rejects_invalid_dimensions(mock_model):
    mock_model.get_embedding_dimension.return_value = None

    with patch(
        "unwritten_rules.infrastructure.embeddings.sentence_transformer.SentenceTransformer",
        return_value=mock_model,
    ):
        with pytest.raises(ValueError, match="dimensionality"):
            SentenceTransformerAdapter("test-model")


def test_adapter_rejects_wrong_vector_dimensions(mock_model):
    mock_model.encode.return_value.tolist.return_value = [
        [0.1, 0.2],
    ]

    with patch(
        "unwritten_rules.infrastructure.embeddings.sentence_transformer.SentenceTransformer",
        return_value=mock_model,
    ):
        adapter = SentenceTransformerAdapter("test-model")

        with pytest.raises(ValueError, match="dimensionality"):
            adapter.encode(["Experience"], batch_size=1)


def test_adapter_rejects_non_finite_vectors(mock_model):
    mock_model.encode.return_value.tolist.return_value = [
        [0.1, float("nan"), 0.3],
    ]

    with patch(
        "unwritten_rules.infrastructure.embeddings.sentence_transformer.SentenceTransformer",
        return_value=mock_model,
    ):
        adapter = SentenceTransformerAdapter("test-model")

        with pytest.raises(ValueError, match="non-finite"):
            adapter.encode(["Experience"], batch_size=1)
