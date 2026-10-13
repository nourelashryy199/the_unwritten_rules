import pytest
from pydantic import ValidationError

from unwritten_rules.domain.evidence import Evidence, EvidenceType
from unwritten_rules.domain.experience import Experience
from unwritten_rules.domain.experience_analysis import ExperienceAnalysis
from unwritten_rules.domain.inference import AIInference

def test_create_ai_inferece():
    inference = AIInference(
        content = "The colleague may have been distracted. ",
        model_name="example-model",
        supporting_evidence_ids=["e1"],
    )
    assert inference.content == (
        "The colleague may have been distracted. "
    )
    assert inference.model_name == "example-model"
    assert inference.supporting_evidence_ids == ["e1"]

def test_ai_inference_requires_content():
    with pytest.raises(ValidationError):
        AIInference(
            content = "",
            model_name="example-model",
        )

def test_ai_inference_requires_model_name():
    with pytest.raises(ValidationError):
        AIInference(
            content = "A possible explanation. ",
            model_name = " ",
        )

def test_analysis_references_experience():
    experience = Experience(
        narrative = "My colleague looked away when I greeted them. ",
        country = "UK",
        evidence = [
            Evidence(
                id = "e1",
                type = EvidenceType.OBSERVATION,
                content = "My colleague looked away. ",
            )
        ],
    )
    analysis = ExperienceAnalysis(
        experience_id = experience.id,
        inferences = [
            AIInference(
                content = "The colleague may have been distracted. ",
                model_name = "example-model",
                supporting_evidence_ids= ["e1"],
            )
        ],
    )
    assert analysis.experience_id == experience.id
    assert len(analysis.inferences) == 1

def test_ai_analysis_does_not_modify_original_experience():
    experience = Experience(
        narrative = "My colleague ignored my greeting. ",
        country = "UK",
    )
    original_narrative = experience.narrative

    analysis = ExperienceAnalysis(
        experience_id = experience.id,
        inferences=[
            AIInference(
                content = "The colleague may not have heard the greeting. ",
                model_name = "example-model",
            )
        ],
    )
    assert experience.narrative == original_narrative
    assert len(analysis.inferences) == 1
    assert experience.model_dump().get("inferences") is None
