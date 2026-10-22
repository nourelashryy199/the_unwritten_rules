import pytest

from unwritten_rules.application.evaluation.evaluator import evaluate_query


def test_evaluator_scores_query_with_one_relevant_candidate():
    labels = {
        "SYN-001": 2,
        "SYN-002": 0,
        "SYN-003": 0,
    }

    result = evaluate_query(
        ranked_ids=["SYN-002", "SYN-001", "SYN-003"],
        labels=labels,
        k_values=(1, 2, 3),
    )

    assert result["status"] == "scored"
    assert result["recall"]["recall_at_1"] == 0.0
    assert result["recall"]["recall_at_2"] == 1.0
    assert result["reciprocal_rank"] == 0.5


def test_evaluator_excludes_uncertain_candidates():
    labels = {
        "SYN-001": None,
        "SYN-002": 2,
        "SYN-003": 0,
    }

    result = evaluate_query(
        ranked_ids=["SYN-001", "SYN-002", "SYN-003"],
        labels=labels,
        k_values=(1,),
    )

    assert result["original_ranking"] == [
        "SYN-001",
        "SYN-002",
        "SYN-003",
    ]
    assert result["assessable_ranking"] == [
        "SYN-002",
        "SYN-003",
    ]
    assert result["recall"]["recall_at_1"] == 1.0
    assert result["uncertain_count"] == 1


def test_evaluator_handles_ambiguous_query():
    labels = {
        "SYN-001": None,
        "SYN-002": None,
        "SYN-003": 0,
    }

    result = evaluate_query(
        ranked_ids=["SYN-003", "SYN-001", "SYN-002"],
        labels=labels,
    )

    assert result["status"] == "unscorable"
    assert result["recall"] is None
    assert result["reciprocal_rank"] is None
    assert result["uncertain_count"] == 2


def test_evaluator_rejects_incomplete_ranking():
    labels = {
        "SYN-001": 2,
        "SYN-002": 0,
    }

    with pytest.raises(ValueError):
        evaluate_query(
            ranked_ids=["SYN-001"],
            labels=labels,
        )


def test_evaluator_rejects_duplicate_candidates():
    labels = {
        "SYN-001": 2,
        "SYN-002": 0,
    }

    with pytest.raises(ValueError):
        evaluate_query(
            ranked_ids=["SYN-001", "SYN-001"],
            labels=labels,
        )


def test_evaluator_rejects_invalid_labels():
    labels = {
        "SYN-001": 3,
        "SYN-002": 0,
    }

    with pytest.raises(ValueError):
        evaluate_query(
            ranked_ids=["SYN-001", "SYN-002"],
            labels=labels,
        )