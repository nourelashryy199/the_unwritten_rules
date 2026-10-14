
from unwritten_rules.application.preprocessing.processor import (
    ExperienceProcessor,
)


def make_record(narrative="A colleague ignored my greeting."):
    return {
        "narrative": narrative,
        "country": "Egypt",
    }


def test_valid_record_is_processed():
    result = ExperienceProcessor().process([make_record()])

    assert len(result.valid_records) == 1
    assert result.invalid_records == []


def test_original_narrative_is_preserved():
    narrative = "  A colleague ignored my greeting.  "

    result = ExperienceProcessor().process([
        make_record(narrative)
    ])

    processed = result.valid_records[0]

    assert processed.original_narrative == narrative
    assert processed.experience.narrative == narrative


def test_retrieval_text_is_separate():
    result = ExperienceProcessor().process([make_record()])

    processed = result.valid_records[0]

    assert "Narrative: A colleague ignored my greeting." in (
        processed.retrieval_text
    )
    assert "Country: Egypt" in processed.retrieval_text
    assert processed.original_narrative != processed.retrieval_text


def test_invalid_record_is_reported():
    result = ExperienceProcessor().process([
        {"narrative": "Missing country."}
    ])

    assert result.valid_records == []
    assert len(result.invalid_records) == 1
    assert result.invalid_records[0].record_index == 0


def test_valid_records_continue_after_invalid_record():
    result = ExperienceProcessor().process([
        make_record("First valid experience."),
        {"country": "Egypt"},
        make_record("Second valid experience."),
    ])

    assert len(result.valid_records) == 2
    assert len(result.invalid_records) == 1


def test_duplicates_are_identified():
    result = ExperienceProcessor().process([
        make_record("Repeated experience."),
        make_record("Different experience."),
        make_record("Repeated experience."),
    ])

    assert len(result.valid_records) == 3
    assert len(result.duplicate_indices) == 1

    indices = next(iter(result.duplicate_indices.values()))
    assert indices == [0, 2]


def test_preprocessing_is_deterministic():
    processor = ExperienceProcessor()
    record = make_record()

    first = processor.process([record]).valid_records[0]
    second = processor.process([record]).valid_records[0]

    assert first.retrieval_text == second.retrieval_text
    assert first.content_fingerprint == second.content_fingerprint


def test_different_content_has_different_fingerprints():
    result = ExperienceProcessor().process([
        make_record("First experience."),
        make_record("Second experience."),
    ])

    assert (
        result.valid_records[0].content_fingerprint
        != result.valid_records[1].content_fingerprint
    )


def test_empty_batch():
    result = ExperienceProcessor().process([])

    assert result.valid_records == []
    assert result.invalid_records == []
    assert result.duplicate_indices == {}


def test_multiple_invalid_records_are_reported():
    result = ExperienceProcessor().process([
        {"narrative": "Missing country."},
        {"country": "Egypt"},
        make_record("Valid experience."),
    ])

    assert len(result.valid_records) == 1
    assert len(result.invalid_records) == 2

    indices = [
        error.record_index
        for error in result.invalid_records
    ]

    assert indices == [0, 1]


def test_generated_metadata_does_not_affect_fingerprint():
    processor = ExperienceProcessor()

    first = processor.process([
        make_record("Same experience.")
    ]).valid_records[0]

    second = processor.process([
        make_record("Same experience.")
    ]).valid_records[0]

    assert first.experience.id != second.experience.id

    assert (
        first.content_fingerprint
        == second.content_fingerprint
    )


def test_duplicate_detection_preserves_all_records():
    result = ExperienceProcessor().process([
        make_record("Repeated."),
        make_record("Repeated."),
    ])

    assert len(result.valid_records) == 2
    assert len(result.duplicate_indices) == 1


def test_country_changes_fingerprint():
    first = make_record("Same narrative.")
    second = {
        "narrative": "Same narrative.",
        "country": "Canada",
    }

    result = ExperienceProcessor().process([first, second])

    assert (
        result.valid_records[0].content_fingerprint
        != result.valid_records[1].content_fingerprint
    )


def test_whitespace_is_preserved_in_original_narrative():
    narrative = "  First line.\n\nSecond line.  "

    result = ExperienceProcessor().process([
        make_record(narrative)
    ])

    processed = result.valid_records[0]

    assert processed.original_narrative == narrative
    assert processed.experience.narrative == narrative


def test_unknown_context_is_preserved_in_retrieval_text():
    record = {
        "narrative": "A colleague avoided answering.",
        "country": "Egypt",
        "context": {
            "relationship": {
                "status": "unknown"
            }
        },
    }

    result = ExperienceProcessor().process([record])

    assert result.invalid_records == []

    processed = result.valid_records[0]

    assert "relationship: unknown" in processed.retrieval_text


def test_context_order_does_not_change_retrieval_text():
    context_a = {
        "setting": {
            "status": "known",
            "value": "Workplace",
            "source": "contributor",
        },
        "relationship": {
            "status": "known",
            "value": "Colleagues",
            "source": "contributor",
        },
    }

    context_b = {
        "relationship": context_a["relationship"],
        "setting": context_a["setting"],
    }

    first = {
        **make_record(),
        "context": context_a,
    }

    second = {
        **make_record(),
        "context": context_b,
    }

    result = ExperienceProcessor().process([first, second])

    assert result.invalid_records == []

    assert (
        result.valid_records[0].retrieval_text
        == result.valid_records[1].retrieval_text
    )

    assert (
        result.valid_records[0].content_fingerprint
        == result.valid_records[1].content_fingerprint
    )
