import math

import pytest
from pydantic import ValidationError

from unwritten_rules.application.retrieval.models import (
    RetrievalConfig,
    RetrievalResult,
)


def test_valid_retrieval_result():
    result = RetrievalResult(
        record_id="SYN-001",
        similarity_score=0.85,
        rank=1,
    )

    assert result.record_id == "SYN-001"
    assert result.similarity_score == 0.85
    assert result.rank == 1


@pytest.mark.parametrize("score", [-1.1, 1.1, math.inf, math.nan])
def test_invalid_similarity_score_is_rejected(score):
    with pytest.raises(ValidationError):
        RetrievalResult(
            record_id="SYN-001",
            similarity_score=score,
            rank=1,
        )


def test_blank_record_id_is_rejected():
    with pytest.raises(ValidationError):
        RetrievalResult(
            record_id="   ",
            similarity_score=0.5,
            rank=1,
        )


def test_nonpositive_rank_is_rejected():
    with pytest.raises(ValidationError):
        RetrievalResult(
            record_id="SYN-001",
            similarity_score=0.5,
            rank=0,
        )


def test_default_top_k():
    config = RetrievalConfig()

    assert config.top_k == 5


@pytest.mark.parametrize("top_k", [0, -1])
def test_invalid_top_k_is_rejected(top_k):
    with pytest.raises(ValidationError):
        RetrievalConfig(top_k=top_k)