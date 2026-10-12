from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, field_validator

class EvidenceType(str, Enum):
    OBSERVATION = "observation"
    INTERPRETATION = "interpretation"
    UNKNOWN = "unknown"

class Evidence(BaseModel):
    model_config = ConfigDict(extra = "forbid")
    id: str | None = None
    type: EvidenceType
    content: str = Field(min_length = 1)

    @field_validator("content")
    @classmethod
    def reject_blank_content(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Evidence content cannot be blank. ")
        return value