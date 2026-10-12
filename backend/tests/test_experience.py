
import pytest
from pydantic import ValidationError

from unwritten_rules.domain.context import ContextAttribute, ContextStatus
from unwritten_rules.domain.experience import Experience
from unwritten_rules.domain.evidence import Evidence, EvidenceType


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
    assert experience.evidence == []  


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
        evidence = [Evidence(
            type = EvidenceType.OBSERVATION,
            content = "My colleague walked past without speaking. ", 
        ),
        Evidence(
            type = EvidenceType.INTERPRETATION,
            content = "I thought they might be upset with me. ",
        ),
        ],
    )
    assert len(experience.evidence) == 2
    assert experience.evidence[0].type == EvidenceType.OBSERVATION
    assert experience.evidence[1].type == EvidenceType.INTERPRETATION


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

def test_experience_with_evidence():
    experience = Experience(
        narrative=(
            "I greeted my colleague, but she looked away. "
            "I thought she was ignoring me."
        ),
        country="UK",
        evidence=[
            Evidence(
                type=EvidenceType.OBSERVATION,
                content="She looked away and did not respond.",
            ),
            Evidence(
                type=EvidenceType.INTERPRETATION,
                content="I thought she was deliberately ignoring me.",
            ),
            Evidence(
                type=EvidenceType.UNKNOWN,
                content="Why she did not respond.",
            ),
        ],
    )

    assert len(experience.evidence) == 3
    assert experience.evidence[0].type == EvidenceType.OBSERVATION
    assert experience.evidence[1].type == EvidenceType.INTERPRETATION
    assert experience.evidence[2].type == EvidenceType.UNKNOWN


def test_invalid_evidence_type_is_rejected():
    with pytest.raises(ValidationError):
        Evidence(
            type="confirmed_fact",
            content="She was deliberately ignoring me.",
        )


def test_whitespace_only_evidence_is_rejected():
    with pytest.raises(ValidationError):
        Evidence(
            type=EvidenceType.OBSERVATION,
            content="   ",
        )


def test_experiences_have_independent_evidence():
    first = Experience(
        narrative="First experience.",
        country="Egypt",
    )

    second = Experience(
        narrative="Second experience.",
        country="UK",
    )

    first.evidence.append(
        Evidence(
            type=EvidenceType.OBSERVATION,
            content="Someone left the room.",
        )
    )

    assert second.evidence == []


def test_known_context_attribute():
    attribute = ContextAttribute(
        value = "Family gathering"
    )
    assert attribute.status == ContextStatus.KNOWN
    assert attribute.value == "Family gathering"

def test_explicitly_unknwon_context_attribute():
    attribute = ContextAttribute(
        status = ContextStatus.UNKNOWN
    )
    assert attribute.status == ContextStatus.UNKNOWN
    assert attribute.value is None

def test_known_context_without_value_is_rejected():
    with pytest.raises(ValidationError):
        ContextAttribute(
            status=ContextStatus.KNOWN
        )


def test_unknown_context_with_value_is_rejected():
    with pytest.raises(ValidationError):
        ContextAttribute(
            status=ContextStatus.UNKNOWN,
            value="Family gathering",
        )


def test_missing_context_differs_from_unknown_context():
    experience = Experience(
        narrative = "I declined a family invitation. ",
        country = "Egypt", 
        context = {
            "previous_invitations": ContextAttribute(
                status = ContextStatus.UNKNOWN
            )
        },
    )
    assert "previous_invitations" in experience.context
    assert(
        experience.context["previous_invitations"].status
        == ContextStatus.UNKNOWN
    )
    assert "relationship_history" not in experience.context

def test_context_can_reference_evidence():
    experience = Experience(
        narrative = "My manager raised their voice. ", 
        country = "UK", 
        evidence = [
            Evidence(
                id = "e1", 
                type = EvidenceType.OBSERVATION, 
                content = "My manager raised their voice. ",
            ),
        ],
        context = {
            "communication_style": ContextAttribute(
                value = "Raised voice", 
                evidence_ids = ["e1"],
            ),
        },
    )
    assert experience.context["communication_style"].evidence_ids == ["e1"]

def test_context_cannot_reference_missing_evidence():
    with pytest.raises(ValidationError):
        Experience(
            narrative = "My manager raised their voice. ", 
            country = "UK", 
            context = {
                "communication_style": ContextAttribute(
                    value = "Raised voice", 
                    evidence_ids = ["nonexistent"],
                ),
            },
        )

def test_duplicate_evidence_ids_are_rejected():
    with pytest.raises(ValidationError):
        Experience(
            narrative = "A social interaction. ", 
            country = "Egypt", 
            evidence = [
                Evidence(
                    id = "e1",
                    type = EvidenceType.OBSERVATION,
                    content = "Someone entered the room. ",
                ),
                Evidence(
                    id = "e1", 
                    type = EvidenceType.INTERPRETATION, 
                    content = "I thought they were upset. ",
                ),
            ],
        )



