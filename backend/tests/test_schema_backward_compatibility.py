from unwritten_rules.domain.experience import Experience
from unwritten_rules.domain.moderation import ModerationStatus


def test_legacy_text_only_experience_remains_valid():
    experience = Experience(
        narrative="My friend seemed upset when I declined an invitation.",
        country="United Kingdom",
    )

    assert experience.context == {}
    assert experience.evidence == []
    assert experience.moderation_status == ModerationStatus.PENDING
    assert experience.narrative == (
        "My friend seemed upset when I declined an invitation."
    )


def test_legacy_experience_survives_serialization_round_trip():
    original = Experience(
        narrative="My colleague did not respond to my greeting.",
        country="United Kingdom",
    )

    serialized = original.model_dump(mode="json")
    restored = Experience.model_validate(serialized)

    assert restored.id == original.id
    assert restored.created_at == original.created_at
    assert restored.updated_at == original.updated_at
    assert restored.narrative == original.narrative
    assert restored.country == original.country
    assert restored.context == {}
    assert restored.evidence == []
    assert restored.moderation_status == original.moderation_status