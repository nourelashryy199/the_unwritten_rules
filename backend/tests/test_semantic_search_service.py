import pytest

from unwritten_rules.application.embeddings.models import (
    EmbeddedExperience,
    EmbeddingConfig,
)
from unwritten_rules.application.retrieval.models import RetrievalConfig
from unwritten_rules.application.retrieval.service import SemanticSearchService
from unwritten_rules.infrastructure.retrieval.in_memory import (
    InMemoryCosineRetriever,
)


class FakeEmbeddingModel:
    def __init__(
        self,
        dimensions: int = 3,
        returned_embeddings: list[list[float]] | None = None,
    ):
        self.dimensions = dimensions
        self.returned_embeddings = (
        returned_embeddings
        if returned_embeddings is not None
        else [[1.0, 0.0, 0.0]]
    )
        self.received_texts = None
        self.received_batch_size = None

    def encode(self, texts: list[str], batch_size: int) -> list[list[float]]:
        self.received_texts = texts
        self.received_batch_size = batch_size
        return self.returned_embeddings


def make_candidate(
    record_id: str,
    embedding: list[float],
    model_name: str = "test-model",
) -> EmbeddedExperience:
    return EmbeddedExperience(
        record_id=record_id,
        embedding=embedding,
        model_name=model_name,
        dimensions=len(embedding),
    )


def make_service(
    embedding_model: FakeEmbeddingModel | None = None,
    top_k: int = 5,
) -> SemanticSearchService:
    return SemanticSearchService(
        embedding_model=embedding_model or FakeEmbeddingModel(),
        retriever=InMemoryCosineRetriever(),
        embedding_config=EmbeddingConfig(
            model_name="test-model",
            dimensions=3,
            batch_size=8,
        ),
        retrieval_config=RetrievalConfig(top_k=top_k),
    )


def test_search_returns_ranked_results():
    service = make_service()

    candidates = [
        make_candidate("B", [0.0, 1.0, 0.0]),
        make_candidate("A", [1.0, 0.0, 0.0]),
        make_candidate("C", [1.0, 1.0, 0.0]),
    ]

    results = service.search("Someone declined my invitation", candidates)

    assert [result.record_id for result in results] == ["A", "C", "B"]
    assert [result.rank for result in results] == [1, 2, 3]


def test_search_respects_top_k():
    service = make_service(top_k=2)

    candidates = [
        make_candidate("A", [1.0, 0.0, 0.0]),
        make_candidate("B", [0.0, 1.0, 0.0]),
        make_candidate("C", [1.0, 1.0, 0.0]),
    ]

    results = service.search("A query", candidates)

    assert len(results) == 2
    assert [result.record_id for result in results] == ["A", "C"]


def test_search_strips_query_whitespace():
    model = FakeEmbeddingModel()
    service = make_service(embedding_model=model)

    service.search(
        "  Why was my refusal considered rude?  ",
        [make_candidate("A", [1.0, 0.0, 0.0])],
    )

    assert model.received_texts == ["Why was my refusal considered rude?"]
    assert model.received_batch_size == 8


@pytest.mark.parametrize("query", ["", " ", "\n\t"])
def test_search_rejects_blank_queries(query):
    service = make_service()

    with pytest.raises(ValueError, match="Query cannot be empty"):
        service.search(query, [])


@pytest.mark.parametrize("query", [None, 42, ["query"]])
def test_search_rejects_non_string_queries(query):
    service = make_service()

    with pytest.raises(TypeError, match="Query must be a string"):
        service.search(query, [])


def test_search_returns_empty_results_for_empty_corpus():
    model = FakeEmbeddingModel()
    service = make_service(embedding_model=model)

    assert service.search("A valid question", []) == []
    assert model.received_texts is None


def test_search_rejects_incompatible_candidate_model():
    service = make_service()

    candidates = [
        make_candidate(
            "A",
            [1.0, 0.0, 0.0],
            model_name="different-model",
        )
    ]

    with pytest.raises(ValueError, match="Candidate embedding model"):
        service.search("A query", candidates)


def test_search_rejects_incompatible_candidate_dimensions():
    service = make_service()

    candidates = [
        make_candidate("A", [1.0, 0.0]),
    ]

    with pytest.raises(ValueError, match="Candidate embedding dimensions"):
        service.search("A query", candidates)


def test_service_rejects_incompatible_embedding_model_dimensions():
    with pytest.raises(ValueError, match="Embedding model dimensions"):
        make_service(embedding_model=FakeEmbeddingModel(dimensions=5))


def test_search_rejects_missing_query_embedding():
    model = FakeEmbeddingModel(returned_embeddings=[])
    service = make_service(embedding_model=model)

    with pytest.raises(ValueError, match="exactly one query embedding"):
        service.search(
            "A query",
            [make_candidate("A", [1.0, 0.0, 0.0])],
        )


def test_search_rejects_incorrect_query_embedding_dimensions():
    model = FakeEmbeddingModel(returned_embeddings=[[1.0, 0.0]])
    service = make_service(embedding_model=model)

    with pytest.raises(ValueError, match="Query embedding dimensions"):
        service.search(
            "A query",
            [make_candidate("A", [1.0, 0.0, 0.0])],
        )