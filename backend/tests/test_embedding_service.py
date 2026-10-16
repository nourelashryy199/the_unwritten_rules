
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from unwritten_rules.application.embeddings.models import (
    EmbeddedExperience,
    EmbeddingConfig,
)
from unwritten_rules.application.embeddings.service import EmbeddingService
from unwritten_rules.application.preprocessing.models import (
    PreprocessedExperience,
)
from unwritten_rules.domain.experience import Experience


@pytest.fixture
def config():
    return EmbeddingConfig(
        model_name="test-model",
        dimensions=3,
        batch_size=2,
    )


@pytest.fixture
def model():
    fake = MagicMock()
    fake.dimensions = 3
    return fake


def make_record(narrative: str) -> PreprocessedExperience:
    experience = Experience(
        narrative=narrative,
        country="Egypt",
    )

    return PreprocessedExperience(
        experience=experience,
        original_narrative=narrative,
        retrieval_text=f"Narrative: {narrative}\nCountry: Egypt",
        content_fingerprint="test-fingerprint",
    )


def test_service_generates_embeddings(model, config):
    model.encode.return_value = [
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
    ]

    records = [
        make_record("I declined an invitation."),
        make_record("My colleague seemed upset."),
    ]

    service = EmbeddingService(model, config)
    results = service.generate(records)

    assert len(results) == 2

    assert results[0].record_id == str(records[0].experience.id)
    assert results[1].record_id == str(records[1].experience.id)

    assert results[0].embedding == [0.1, 0.2, 0.3]
    assert results[1].embedding == [0.4, 0.5, 0.6]

    assert all(result.model_name == "test-model" for result in results)

    model.encode.assert_called_once_with(
        [
            records[0].retrieval_text,
            records[1].retrieval_text,
        ],
        batch_size=2,
    )


def test_service_handles_empty_records(model, config):
    service = EmbeddingService(model, config)

    assert service.generate([]) == []

    model.encode.assert_not_called()


def test_service_rejects_model_dimension_mismatch(model, config):
    model.dimensions = 5

    with pytest.raises(ValueError, match="dimensions"):
        EmbeddingService(model, config)


def test_service_rejects_incorrect_vector_count(model, config):
    model.encode.return_value = [[0.1, 0.2, 0.3]]

    service = EmbeddingService(model, config)

    with pytest.raises(ValueError, match="count"):
        service.generate([
            make_record("First experience."),
            make_record("Second experience."),
        ])


def test_service_rejects_wrong_vector_dimensions(model, config):
    model.encode.return_value = [[0.1, 0.2]]

    service = EmbeddingService(model, config)

    with pytest.raises(ValidationError, match="dimensions"):
        service.generate([make_record("First experience.")])


def test_service_rejects_non_finite_vectors(model, config):
    model.encode.return_value = [[0.1, float("nan"), 0.3]]

    service = EmbeddingService(model, config)

    with pytest.raises(ValidationError, match="finite"):
        service.generate([make_record("First experience.")])


def test_embedded_experience_validates_dimensions():
    with pytest.raises(ValidationError, match="dimensions"):
        EmbeddedExperience(
            record_id="test-id",
            embedding=[0.1, 0.2],
            model_name="test-model",
            dimensions=3,
        )


def test_service_supports_model_replacement():
    record = make_record("A colleague refused my invitation.")

    first_model = MagicMock()
    first_model.dimensions = 3
    first_model.encode.return_value = [[0.1, 0.2, 0.3]]

    second_model = MagicMock()
    second_model.dimensions = 2
    second_model.encode.return_value = [[0.7, 0.8]]

    first_service = EmbeddingService(
        first_model,
        EmbeddingConfig(
            model_name="model-v1",
            dimensions=3,
        ),
    )

    second_service = EmbeddingService(
        second_model,
        EmbeddingConfig(
            model_name="model-v2",
            dimensions=2,
        ),
    )

    first_result = first_service.generate([record])[0]
    second_result = second_service.generate([record])[0]

    assert first_result.model_name == "model-v1"
    assert first_result.dimensions == 3

    assert second_result.model_name == "model-v2"
    assert second_result.dimensions == 2
    assert second_result.embedding == [0.7, 0.8]
