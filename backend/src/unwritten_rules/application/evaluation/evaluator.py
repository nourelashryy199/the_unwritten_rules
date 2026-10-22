from collections.abc import Mapping, Sequence

from unwritten_rules.application.evaluation.metrics import (
    recall_at_k,
    reciprocal_rank,
)


def evaluate_query(
    ranked_ids: Sequence[str],
    labels: Mapping[str, int | None],
    k_values: Sequence[int] = (1, 3, 5, 10),
) -> dict:
    """Evaluate a complete ranking against manual relevance judgments."""

    if not labels:
        raise ValueError("Relevance judgments cannot be empty.")

    if not k_values or any(k <= 0 for k in k_values):
        raise ValueError("K values must be positive.")

    if any(label not in (0, 1, 2, None) for label in labels.values()):
        raise ValueError("Invalid relevance label.")

    if len(ranked_ids) != len(set(ranked_ids)):
        raise ValueError("Ranked results contain duplicate record IDs.")

    if set(ranked_ids) != set(labels):
        raise ValueError(
            "Full ranking must contain exactly the labelled candidates."
        )

    relevant_ids = {
        record_id
        for record_id, label in labels.items()
        if label == 2
    }

    uncertain_ids = {
        record_id
        for record_id, label in labels.items()
        if label is None
    }

    assessable_ranking = [
        record_id
        for record_id in ranked_ids
        if record_id not in uncertain_ids
    ]

    if not relevant_ids:
        return {
            "status": "unscorable",
            "recall": None,
            "reciprocal_rank": None,
            "relevant_count": 0,
            "uncertain_count": len(uncertain_ids),
            "original_ranking": list(ranked_ids),
            "assessable_ranking": assessable_ranking,
        }

    recalls = {
        f"recall_at_{k}": recall_at_k(
            assessable_ranking,
            relevant_ids,
            k,
        )
        for k in k_values
    }

    return {
        "status": "scored",
        "recall": recalls,
        "reciprocal_rank": reciprocal_rank(
            assessable_ranking,
            relevant_ids,
        ),
        "relevant_count": len(relevant_ids),
        "uncertain_count": len(uncertain_ids),
        "original_ranking": list(ranked_ids),
        "assessable_ranking": assessable_ranking,
    }