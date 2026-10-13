from unwritten_rules.domain.context import(
    ContextAttribute, 
    ContextStatus,
)
from unwritten_rules.domain.evidence import(
    Evidence, 
    EvidenceType,
)
from unwritten_rules.domain.experience import Experience
from unwritten_rules.domain.experience_analysis import ExperienceAnalysis
from unwritten_rules.domain.inference import AIInference
from unwritten_rules.domain.moderation import ModerationStatus


def test_representative_experience_schema():
    original_narrative = (
        "I greeted my colleague during a meeting, "
        "but she looked away without responding. "
        "I thought she was upset with me."
    )
    experience = Experience(
        narrative = original_narrative,
        country = "United Kingdom",
        context={
            "setting": ContextAttribute(
                value = "Workplace meeting",
                evidence_ids=["e1"],
            ),
            "interpersonal_relationship": ContextAttribute(
                value = "Colleagues",
            ),
            "colleague_intention": ContextAttribute(
                status=ContextStatus.UNKNOWN,
            ),
        },
        evidence = [
            Evidence(
                id = "e1",
                type = EvidenceType.OBSERVATION,
                content = (
                    "My colleague looked away "
                    "without responding."
                ),
            ),
            Evidence(
                id = "e2",
                type = EvidenceType.INTERPRETATION,
                content = "I thought she was upset with me. ",
            ),
        ],
    )
    analysis = ExperienceAnalysis(
        experience_id=experience.id,
        inferences = [
            AIInference(
                content = "The colleague may have been distracted. ",
                model_name="example-model",
                supporting_evidence_ids=["e1"],
            )
        ],
    )
    assert experience.narrative == original_narrative
    assert experience.moderation_status == ModerationStatus.PENDING

    assert experience.context["colleague_intention"].status == (
        ContextStatus.UNKNOWN
    )
    assert "previous_conflicts" is not experience.context

    assert experience.evidence[0].type == EvidenceType.OBSERVATION
    assert experience.evidence[1].type == EvidenceType.INTERPRETATION

    assert analysis.experience_id == experience.id
    assert len(analysis.inferences) == 1
    assert experience.model_dump().get("inferences") is None
    