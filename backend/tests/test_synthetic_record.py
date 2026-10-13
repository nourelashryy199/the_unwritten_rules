import json 
from pathlib import Path

import pytest
from pydantic import ValidationError

from unwritten_rules.data.synthetic_record import(
    SyntheticExperienceRecord,
)

DATASET_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "synthetic"
    / "experiences.json"
)

def load_first_record() -> dict:
    with DATASET_PATH.open(encoding = "utf-8") as file:
        return json.load(file)[0]

def test_valid_synthetic_record():
    record = SyntheticExperienceRecord.model_validate(
        load_first_record()
    )
    assert record.record_id == "SYN-001"
    assert record.record_type == "synthetic"
    assert record.experience.country == "Egypt"

def test_record_must_be_synthetic():
    data = load_first_record()
    data["record_type"] = "authentic"

    with pytest.raises(ValidationError):
        SyntheticExperienceRecord.model_validate(data)

def test_invalid_comparison_type_is_rejected():
    data = load_first_record()
    data["comparison_type"] = "unknown_comparison"

    with pytest.raises(ValidationError):
        SyntheticExperienceRecord.model_validate(data)

def test_empty_expectation_label_is_rejected():
    data = load_first_record()
    data["expectation_label"] = " "

    with pytest.raises(ValidationError):
        SyntheticExperienceRecord.model_validate(data)


def test_unexpected_metadata_is_rejected():
    data = load_first_record()
    data["unexpected_field"] = "value"

    with pytest.raises(ValidationError):
        SyntheticExperienceRecord.model_validate(data)