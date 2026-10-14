from unwritten_rules.application.preprocessing.validator import(
    ExperienceValidator,
)

def test_valid_experience():
    validator = ExperienceValidator()

    record = {
        "narrative": "A colleague ignored my greeting. ", 
        "country": "Egypt",
    }
    experience, error = validator.validate(record, record_index = 0)
    assert experience is not None
    assert error is None
    assert experience.narrative == record["narrative"]
    assert experience.country == "Egypt"

def test_missing_required_country():
    validator = ExperienceValidator()

    record = {
        "narrative": "A colleague ignored my greeting. "
    }
    experience, error = validator.validate(record, record_index = 1)
    assert experience is None
    assert error is not None
    assert error.record_index == 1
    assert any(
        "country" in item["loc"]
        for item in error.errors
    )

def test_blank_narrative():
    validator = ExperienceValidator()
    record = {
        "narrative": " ",
        "country": "Egypt",
    }
    experience, error = validator.validate(record, record_index = 2)

    assert experience is None
    assert error is not None

def test_optional_context_can_be_omitted():
    validator = ExperienceValidator()

    record = {
        "narrative": "A colleague ignored my greeting. ", 
        "country": "Egypt",
    }
    experience, error = validator.validate(record, record_index=3)

    assert error is None
    assert experience is not None
    assert experience.context == {}
    assert experience.evidence == []

def test_original_narrative_is_not_modified():
    validator = ExperienceValidator()
    original = " A colleague ignored my greetings. "
    record = {
        "narrative": original,
        "country": "Egypt",
    }
    experience, error = validator.validate(record, record_index = 4)
    assert error is None
    assert experience is not None
    assert experience.narrative == original