from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, field_validator
from unwritten_rules.domain.experience import Experience

class ComparisonType(str, Enum):
    SAME_BEHAVIOUR_DIFFERENT_EXPECTATIONS = (
        "same_behaviour_different_expectations"
    )
    DIFFERENT_BEHAVIOURS_SAME_EXPECTATION = (
        "different_behaviours_same_expectation"
    )

class SyntheticExperienceRecord(BaseModel):
    model_config = ConfigDict(extra = "forbid")
    record_id: str = Field(pattern = r"^SYN-\d{3}$")
    record_type: str = Field(pattern = r"^synthetic$")
    pair_id: str = Field(pattern = r"^PAIR-\d{3}$")
    comparison_type: ComparisonType
    expectation_label: str
    experience: Experience

    @field_validator("expectation_label")
    @classmethod
    def validate_expectation_label(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Expectation label cannot be empty. ")
        return value
    