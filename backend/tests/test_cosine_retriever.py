import math

import pytest

from unwritten_rules.application.embeddings.models import EmbeddedExperience
from unwritten_rules.infrastructure.retrieval.in_memory import (
    InMemoryCosineRetriever,
)


def make_candidate(record_id, vector):
    return EmbeddedExperience(
        record_id=record_id,
        embedding=vector,
        model_name="test-model",
        dimensions=len(vector),
    )


@pytest.fixture
def retriever():
    return InMemoryCosineRetriever()


def test_ranks_by_descending_similarity(retriever):
    candidates = [
        make_candidate("B", [0.0, 1.0]),
        make_candidate("C", [1.0, 1.0]),
        make_candidate("A", [1.0, 0.0]),
    ]

    results = retriever.retrieve([1.0, 0.0], candidates, top_k=3)

    assert [result.record_id for result in results] == ["A", "C", "B"]
    assert [result.rank for result in results] == [1, 2, 3]


def test_respects_top_k(retriever):
    candidates = [
        make_candidate("A", [1.0, 0.0]),
        make_candidate("B", [0.0, 1.0]),
    ]

    results = retriever.retrieve([1.0, 0.0], candidates, top_k=1)

    assert len(results) == 1
    assert results[0].record_id == "A"


def test_top_k_larger_than_corpus(retriever):
    candidates = [make_candidate("A", [1.0, 0.0])]

    results = retriever.retrieve([1.0, 0.0], candidates, top_k=10)

    assert len(results) == 1


def test_empty_corpus(retriever):
    assert retriever.retrieve([1.0, 0.0], [], top_k=5) == []


def test_invalid_top_k(retriever):
    with pytest.raises(ValueError):
        retriever.retrieve([1.0, 0.0], [], top_k=0)


def test_empty_query_embedding(retriever):
    with pytest.raises(ValueError):
        retriever.retrieve([], [], top_k=5)


def test_zero_query_vector(retriever):
    candidates = [make_candidate("A", [1.0, 0.0])]

    with pytest.raises(ValueError):
        retriever.retrieve([0.0, 0.0], candidates, top_k=5)


def test_zero_candidate_vector(retriever):
    candidates = [make_candidate("A", [0.0, 0.0])]

    with pytest.raises(ValueError):
        retriever.retrieve([1.0, 0.0], candidates, top_k=5)


def test_dimension_mismatch(retriever):
    candidates = [make_candidate("A", [1.0, 0.0, 0.0])]

    with pytest.raises(ValueError):
        retriever.retrieve([1.0, 0.0], candidates, top_k=5)


def test_nonfinite_query_embedding(retriever):
    with pytest.raises(ValueError):
        retriever.retrieve([math.nan, 1.0], [], top_k=5)


def test_deterministic_tie_breaking(retriever):
    candidates = [
        make_candidate("B", [1.0, 0.0]),
        make_candidate("A", [1.0, 0.0]),
    ]

    results = retriever.retrieve([1.0, 0.0], candidates, top_k=2)

    assert [result.record_id for result in results] == ["A", "B"]


def test_opposite_vectors_have_negative_similarity(retriever):
    candidates = [make_candidate("A", [-1.0, 0.0])]

    results = retriever.retrieve([1.0, 0.0], candidates, top_k=1)

    assert results[0].similarity_score == pytest.approx(-1.0)