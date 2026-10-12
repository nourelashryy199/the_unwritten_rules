
import pytest
from pydantic import ValidationError

from unwritten_rules.domain.context import ContextAttribute
from unwritten_rules.domain.experience import Experience


def test_create_experience_with_required_fields():
    experience = Experience(
        narrative="I declined an invitation without explaining why.",
        country="Egypt",
    )

    assert experience.narrative == (
        "I declined an invitation without explaining why."
    )
    assert experience.country == "Egypt"
    assert experience.context == {}
    assert experience.observation is None
    assert experience.interpretation is None


def test_create_experience_with_optional_context():
    experience = Experience(
        narrative="I declined an invitation without explaining why.",
        country="Egypt",
        context={
            "setting": ContextAttribute(
                value="Family gathering"
            ),
            "interpersonal_relationship": ContextAttribute(
                value="Extended family"
            ),
        },
    )

    assert experience.context["setting"].value == "Family gathering"
    assert (
        experience.context["interpersonal_relationship"].value
        == "Extended family"
    )


def test_experiences_have_independent_context():
    first = Experience(
        narrative="A social interaction.",
        country="Egypt",
    )

    second = Experience(
        narrative="Another social interaction.",
        country="UK",
    )

    first.context["setting"] = ContextAttribute(
        value="Workplace"
    )

    assert second.context == {}


def test_narrative_is_required():
    with pytest.raises(ValidationError):
        Experience(
            country="Egypt"
        )


def test_country_is_required():
    with pytest.raises(ValidationError):
        Experience(
            narrative="An unexpected social interaction."
        )


def test_empty_narrative_is_rejected():
    with pytest.raises(ValidationError):
        Experience(
            narrative="",
            country="Egypt",
        )


def test_empty_country_is_rejected():
    with pytest.raises(ValidationError):
        Experience(
            narrative="A social interaction.",
            country="",
        )


def test_unknown_fields_are_rejected():
    with pytest.raises(ValidationError):
        Experience(
            narrative="A social experience.",
            country="Egypt",
            unsupported_field="value",
        )


def test_empty_context_attribute_is_rejected():
    with pytest.raises(ValidationError):
        ContextAttribute(
            value=""
        )


def test_context_attribute_default_source():
    attribute = ContextAttribute(
        value="Family gathering"
    )

    assert attribute.source == "contributor"


def test_experience_with_observation_and_interpretation():
    experience = Experience(
        narrative="My colleague did not respond to my greeting.",
        country="UK",
        observation="My colleague walked past without speaking.",
        interpretation="I thought they might be upset with me.",
    )

    assert experience.observation == (
        "My colleague walked past without speaking."
    )
    assert experience.interpretation == (
        "I thought they might be upset with me."
    )

def test_whitespace_only_narrative_is_rejected():
    with pytest.raises(ValidationError):
        Experience(
            narrative = " ",
            country = "Egypt",
        )
def test_original_narrative_is_preserved():
    original = " I declined an invitation. \nI felt uncomfortable. "
    experience = Experience(
        narrative = original, 
        country = "Egypt"
    )
    assert experience.narrative == original

def test_invalid_context_source_is_rejected():
    with pytest.raises(ValidationError):
        ContextAttribute(
            value = "Family gathering",
            source = "unknown",
        )

def test_whitespace_only_country_is_rejected():
    with pytest.raises(ValidationError):
        Experience(
            narrative="A social interaction.",
            country="   ",
        )