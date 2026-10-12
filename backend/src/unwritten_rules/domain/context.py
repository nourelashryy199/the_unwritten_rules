
from enum import Enum
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field, 
    field_validator,
    model_validator,
)


class ContextStatus(str, Enum):
    KNOWN = "known"
    UNKNOWN = "unknown"


class ContextAttribute(BaseModel):
    """A contextual attribute supplied by the contributor."""

    model_config = ConfigDict(extra="forbid")

    status: ContextStatus = ContextStatus.KNOWN
    value: str | None = None
    source: Literal["contributor"] = "contributor"
    evidence_ids: list[str] = Field(default_factory=list)

    @field_validator("value")
    @classmethod
    def reject_blank_value(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("Context values cannot be blank.")
        return value

    @model_validator(mode="after")
    def validate_status_and_value(self):
        if self.status == ContextStatus.KNOWN and self.value is None:
            raise ValueError("Known context requires a value.")

        if self.status == ContextStatus.UNKNOWN and self.value is not None:
            raise ValueError("Unknown context must not have a value.")

        return self
