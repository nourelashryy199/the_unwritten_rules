from pydantic import BaseModel, ConfigDict, Field, field_validator
from unwritten_rules.domain.context import ContextAttribute

class Experience(BaseModel):
    model_config = ConfigDict(extra = "forbid")

    narrative: str = Field(min_length = 1)
    country: str = Field(min_length = 1)

    context: dict[str, ContextAttribute] = Field(default_factory = dict)
    observation: str | None = None
    interpretation: str | None = None

    @field_validator("narrative", "country")
    @classmethod

    def reject_blank_fields(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("This field cannot be blank.")
        return value

