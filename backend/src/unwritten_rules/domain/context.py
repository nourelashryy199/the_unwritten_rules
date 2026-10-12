from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

class ContextAttribute(BaseModel):
    model_config = ConfigDict(extra = "forbid")

    value: str = Field(min_length = 1)

    source: Literal["contributor"] = "contributor"

    @field_validator("value")
    @classmethod

    def reject_blank_value(cls, value: str) -> str: 
        if not value.strip():
            raise ValueError("Context values cannot be blank. ")
        return value

    