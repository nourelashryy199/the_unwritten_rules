
import json
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]

QUERIES_PATH = PROJECT_ROOT / "data/evaluation/queries.json"
LABELS_PATH = PROJECT_ROOT / "data/evaluation/relevance_labels.json"
EXPERIENCES_PATH = PROJECT_ROOT / "data/synthetic/experiences.json"

VALID_LABELS = {0, 1, 2, None}

VALID_QUERY_TYPES = {
    "similar_wording_different_expectations",
    "different_wording_same_expectation",
    "context_sensitive",
    "ambiguous",
}


@pytest.fixture(scope="module")
def evaluation_data():
    with QUERIES_PATH.open(encoding="utf-8") as file:
        queries = json.load(file)

    with LABELS_PATH.open(encoding="utf-8") as file:
        labels = json.load(file)

    with EXPERIENCES_PATH.open(encoding="utf-8") as file:
        experiences = json.load(file)

    return queries, labels, experiences


def test_evaluation_queries_exist(evaluation_data):
    queries, _, _ = evaluation_data

    assert len(queries) == 12


def test_query_ids_are_unique(evaluation_data):
    queries, _, _ = evaluation_data

    query_ids = [query["query_id"] for query in queries]

    assert len(query_ids) == len(set(query_ids))


def test_queries_have_required_fields(evaluation_data):
    queries, _, _ = evaluation_data

    for query in queries:
        assert isinstance(query["query_id"], str)
        assert query["query_id"].strip()

        assert isinstance(query["query"], str)
        assert query["query"].strip()

        assert query["query_type"] in VALID_QUERY_TYPES

        assert isinstance(query["context"], dict)


def test_queries_have_expected_context_fields(evaluation_data):
    queries, _, _ = evaluation_data

    required_context_fields = {
        "setting",
        "relationship",
        "country",
    }

    for query in queries:
        assert set(query["context"]) == required_context_fields

        for value in query["context"].values():
            assert value is None or (
                isinstance(value, str) and value.strip()
            )


def test_all_query_types_are_represented(evaluation_data):
    queries, _, _ = evaluation_data

    actual_types = {query["query_type"] for query in queries}

    assert actual_types == VALID_QUERY_TYPES


def test_evaluation_labels_cover_all_queries(evaluation_data):
    queries, labels, _ = evaluation_data

    query_ids = {query["query_id"] for query in queries}

    judgment_ids = [
        judgment["query_id"]
        for judgment in labels["judgments"]
    ]

    assert len(judgment_ids) == len(set(judgment_ids))
    assert set(judgment_ids) == query_ids


def test_every_query_covers_all_candidate_experiences(evaluation_data):
    _, labels, experiences = evaluation_data

    experience_ids = {
        experience["record_id"]
        for experience in experiences
    }

    assert len(experience_ids) == len(experiences)

    for judgment in labels["judgments"]:
        assert set(judgment["labels"]) == experience_ids


def test_relevance_labels_are_valid(evaluation_data):
    _, labels, _ = evaluation_data

    for judgment in labels["judgments"]:
        for relevance in judgment["labels"].values():
            assert type(relevance) in (int, type(None))
            assert relevance in VALID_LABELS


def test_every_judgment_has_a_rationale(evaluation_data):
    _, labels, _ = evaluation_data

    for judgment in labels["judgments"]:
        assert isinstance(judgment["rationale"], str)
        assert judgment["rationale"].strip()


def test_ambiguous_queries_include_uncertain_labels(evaluation_data):
    queries, labels, _ = evaluation_data

    ambiguous_ids = {
        query["query_id"]
        for query in queries
        if query["query_type"] == "ambiguous"
    }

    judgments_by_query = {
        judgment["query_id"]: judgment
        for judgment in labels["judgments"]
    }

    for query_id in ambiguous_ids:
        values = judgments_by_query[query_id]["labels"].values()

        assert any(value is None for value in values)


def test_non_ambiguous_queries_have_relevant_candidates(evaluation_data):
    queries, labels, _ = evaluation_data

    judgments_by_query = {
        judgment["query_id"]: judgment
        for judgment in labels["judgments"]
    }

    for query in queries:
        if query["query_type"] == "ambiguous":
            continue

        values = judgments_by_query[
            query["query_id"]
        ]["labels"].values()

        assert any(value == 2 for value in values)


def test_hard_negative_pairs_are_distinguished(evaluation_data):
    _, labels, _ = evaluation_data

    judgments_by_query = {
        judgment["query_id"]: judgment["labels"]
        for judgment in labels["judgments"]
    }

    expected_hard_negatives = {
        "Q-001": ("SYN-001", "SYN-002"),
        "Q-002": ("SYN-003", "SYN-004"),
        "Q-003": ("SYN-005", "SYN-006"),
        "Q-004": ("SYN-007", "SYN-008"),
        "Q-009": ("SYN-002", "SYN-001"),
        "Q-010": ("SYN-004", "SYN-003"),
    }

    for query_id, (positive_id, negative_id) in (
        expected_hard_negatives.items()
    ):
        judgments = judgments_by_query[query_id]

        assert judgments[positive_id] == 2
        assert judgments[negative_id] == 0


def test_cross_behaviour_positive_pairs(evaluation_data):
    _, labels, _ = evaluation_data

    judgments_by_query = {
        judgment["query_id"]: judgment["labels"]
        for judgment in labels["judgments"]
    }

    expected_positive_pairs = {
        "Q-005": ("SYN-009", "SYN-010"),
        "Q-006": ("SYN-011", "SYN-012"),
        "Q-007": ("SYN-013", "SYN-014"),
        "Q-008": ("SYN-015", "SYN-016"),
    }

    for query_id, experience_ids in expected_positive_pairs.items():
        for experience_id in experience_ids:
            assert judgments_by_query[query_id][experience_id] == 2


def test_evaluation_dataset_has_expected_size(evaluation_data):
    queries, labels, experiences = evaluation_data

    total_judgments = sum(
        len(judgment["labels"])
        for judgment in labels["judgments"]
    )

    assert len(queries) == 12
    assert len(experiences) == 16
    assert total_judgments == 192


def test_uncertain_judgments_are_preserved(evaluation_data):
    _, labels, _ = evaluation_data

    uncertain_count = sum(
        relevance is None
        for judgment in labels["judgments"]
        for relevance in judgment["labels"].values()
    )

    assert uncertain_count == 4
