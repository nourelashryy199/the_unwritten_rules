import pytest

from unwritten_rules.application.evaluation.metrics import (
    mean_reciprocal_rank,
    recall_at_k,
    reciprocal_rank,
)


def test_recall_at_k_all_relevant_retrieved():
    ranked = ["SYN-001", "SYN-002", "SYN-003"]
    relevant = {"SYN-001", "SYN-003"}

    assert recall_at_k(ranked, relevant, k=3) == 1.0


def test_recall_at_k_partial_recall():
    ranked = ["SYN-002", "SYN-001", "SYN-003"]
    relevant = {"SYN-001", "SYN-003"}

    assert recall_at_k(ranked, relevant, k=2) == 0.5


def test_recall_at_k_no_relevant_retrieved():
    ranked = ["SYN-002", "SYN-004"]
    relevant = {"SYN-001"}

    assert recall_at_k(ranked, relevant, k=2) == 0.0


def test_recall_at_k_rejects_invalid_k():
    with pytest.raises(ValueError):
        recall_at_k(["SYN-001"], {"SYN-001"}, k=0)


def test_recall_at_k_rejects_empty_relevant_set():
    with pytest.raises(ValueError):
        recall_at_k(["SYN-001"], set(), k=1)


def test_reciprocal_rank_first_result():
    assert reciprocal_rank(
        ["SYN-001", "SYN-002"],
        {"SYN-001"},
    ) == 1.0


def test_reciprocal_rank_third_result():
    assert reciprocal_rank(
        ["SYN-002", "SYN-003", "SYN-001"],
        {"SYN-001"},
    ) == pytest.approx(1 / 3)


def test_reciprocal_rank_no_match():
    assert reciprocal_rank(
        ["SYN-002", "SYN-003"],
        {"SYN-001"},
    ) == 0.0


def test_mean_reciprocal_rank():
    assert mean_reciprocal_rank(
        [1.0, 0.5, 0.0],
    ) == pytest.approx(0.5)


def test_mean_reciprocal_rank_rejects_empty_input():
    with pytest.raises(ValueError):
        mean_reciprocal_rank([])