from unwritten_rules.application.embeddings.models import EmbeddedExperience
from unwritten_rules.infrastructure.retrieval.in_memory import InMemoryCosineRetriever


MODEL_NAME = "test-model"
DIMENSIONS = 3


def make_candidate(record_id: str, vector: list[float]) -> EmbeddedExperience:
    return EmbeddedExperience(
        record_id=record_id,
        embedding=vector,
        model_name=MODEL_NAME,
        dimensions=DIMENSIONS,
    )


def test_ranking_is_independent_of_candidate_order():
    retriever = InMemoryCosineRetriever()

    candidates = [
        make_candidate("EXP-001", [1.0, 0.0, 0.0]),
        make_candidate("EXP-002", [0.0, 1.0, 0.0]),
        make_candidate("EXP-003", [0.8, 0.6, 0.0]),
    ]

    forward = retriever.retrieve(
        query_embedding=[1.0, 0.0, 0.0],
        candidates=candidates,
        top_k=3,
    )

    reversed_order = retriever.retrieve(
        query_embedding=[1.0, 0.0, 0.0],
        candidates=list(reversed(candidates)),
        top_k=3,
    )

    assert [result.record_id for result in forward] == [
        result.record_id for result in reversed_order
    ]

    assert [result.similarity_score for result in forward] == [
        result.similarity_score for result in reversed_order
    ]


def test_baseline_uses_only_embedding_vectors_and_ids():
    retriever = InMemoryCosineRetriever()

    candidates = [
        make_candidate("EXP-001", [1.0, 0.0, 0.0]),
        make_candidate("EXP-002", [0.0, 1.0, 0.0]),
    ]

    results = retriever.retrieve(
        query_embedding=[1.0, 0.0, 0.0],
        candidates=candidates,
        top_k=2,
    )

    assert [result.record_id for result in results] == [
        "EXP-001",
        "EXP-002",
    ]

    assert results[0].similarity_score > results[1].similarity_score


def test_baseline_has_deterministic_tie_breaking():
    retriever = InMemoryCosineRetriever()

    candidates = [
        make_candidate("EXP-002", [1.0, 0.0, 0.0]),
        make_candidate("EXP-001", [1.0, 0.0, 0.0]),
    ]

    results = retriever.retrieve(
        query_embedding=[1.0, 0.0, 0.0],
        candidates=candidates,
        top_k=2,
    )

    assert [result.record_id for result in results] == [
        "EXP-001",
        "EXP-002",
    ]