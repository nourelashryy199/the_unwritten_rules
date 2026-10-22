from collections.abc import Sequence


def recall_at_k(
    ranked_ids: Sequence[str],
    relevant_ids: set[str],
    k: int,
) -> float:
    """Calculate the fraction of relevant records retrieved in the top K."""

    if k <= 0:
        raise ValueError("K must be positive.")

    if not relevant_ids:
        raise ValueError("Recall is undefined without relevant records.")

    retrieved = set(ranked_ids[:k])

    return len(retrieved & relevant_ids) / len(relevant_ids)


def reciprocal_rank(
    ranked_ids: Sequence[str],
    relevant_ids: set[str],
) -> float:
    """Calculate the reciprocal rank of the first relevant record."""

    for rank, record_id in enumerate(ranked_ids, start=1):
        if record_id in relevant_ids:
            return 1.0 / rank

    return 0.0


def mean_reciprocal_rank(
    reciprocal_ranks: Sequence[float],
) -> float:
    """Calculate the arithmetic mean of per-query reciprocal ranks."""

    if not reciprocal_ranks:
        raise ValueError("At least one reciprocal rank is required.")

    if any(not 0.0 <= rank <= 1.0 for rank in reciprocal_ranks):
        raise ValueError("Reciprocal ranks must be between 0 and 1.")

    return sum(reciprocal_ranks) / len(reciprocal_ranks)