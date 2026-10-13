from pydantic import BaseModel, ConfigDict, Field, field_validator

class AIInference(BaseModel):
    model_config = ConfigDict(extra="forbid")
    content: str = Field(min_length= 1)
    model_name: str = Field(min_length=1)

    supporting_evidence_ids: list[str] = Field(
        default_factory = list
    )
    @field_validator("content", "model_name")
    @classmethod
    def reject_blank_fields(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("This field cannot be blank.")
        return value

    