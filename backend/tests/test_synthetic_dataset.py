import json
from collections import defaultdict
from pathlib import Path

import pytest

from unwritten_rules.data.synthetic_record import(
    ComparisonType, 
    SyntheticExperienceRecord,
)

DATASET_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "synthetic"
    / "experiences.json"
)

@pytest.fixture(scope = "module")
def records():
    with DATASET_PATH.open(encoding = "utf-8") as file:
        return json.load(file)

@pytest.fixture(scope = "module")
def pairs(records):
    grouped = defaultdict(list)
    for record in records:
        grouped[record["pair_id"]].append(record)

    return grouped

def test_dataset_contains_at_least_twelve_records(records):
    assert len(records) >=12

def test_all_records_match_synthetic_schema(records):
    for record in records:
        SyntheticExperienceRecord.model_validate(record)

def test_record_ids_are_unique(records):
    ids = [record["record_id"] for record in records]
    assert len(ids) == len(set(ids))

def test_dataset_covers_multiple_countries(records):
    countries = {
        record["experience"]["country"]
        for record in records
    }
    assert len(countries) >= 3

def test_dataset_covers_multiple_social_settings(records):
    settings = {
        record["experience"]["context"]["setting"]["value"]
        for record in records
    }
    assert len(settings) >= 4

def test_every_record_is_explicitly_synthetic(records):
    assert all(
        record["record_type"] == "synthetic"
        for record in records
    )
def test_each_pair_has_exactly_two_records(pairs):
    assert len(pairs) == 8

    for pair_id, members, in pairs.items():
        assert len(members) == 2, (
            f"{pair_id} has {len(members)} records"
        )
def test_comparison_types_are_consistent_within_pairs(pairs):
    for pair_id, members, in pairs.items():
        comparison_types = {
            member["comparison_type"]
            for member in members
        }
        assert len(comparison_types) == 1, (
            f"{pair_id} has inconsistent comparison types"
        )

def test_same_behaviour_pairs_have_different_expectations(pairs):
    matching_pairs = [
        members
        for members in pairs.values()
        if members[0]["comparison_type"]
        == ComparisonType.SAME_BEHAVIOUR_DIFFERENT_EXPECTATIONS.value
    ]

    assert len(matching_pairs) >= 1
    for members in matching_pairs:
        labels = {
            member["expectation_label"]
            for member in members
        }
        assert len(labels) == 2

def test_different_behaviour_pairs_share_expectations(pairs):
    matching_pairs = [
        members
        for members in pairs.values()
        if members[0]["comparison_type"]
        ==ComparisonType.DIFFERENT_BEHAVIOURS_SAME_EXPECTATION
    ]
    assert len(matching_pairs) >=1
    for members in matching_pairs:
        labels = {
            member["expectation_label"]
            for member in members
        }
        assert len(labels) == 1

def test_observations_and_interpretations_are_distinguishable(records):
    for record in records: 
        evidence_types = {
            item["type"]
            for item in record["experience"]["evidence"]
        }
        assert "observation" in evidence_types
        assert "interpretation" in evidence_types

def test_all_records_include_context(records):
    for record in records: 
        assert record["experience"]["context"]


