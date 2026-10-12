from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from unwritten_rules.domain.context import ContextAttribute
from unwritten_rules.domain.evidence import Evidence

class Experience(BaseModel):

    model_config = ConfigDict(extra = "forbid")

    narrative: str = Field(min_length = 1)
    country: str = Field(min_length = 1)

    context: dict[str, ContextAttribute] = Field(default_factory = dict)
    evidence: list[Evidence] = Field(default_factory = list)

    @field_validator("narrative", "country")
    @classmethod

    def reject_blank_required_fields(cls, value: str) -> str: 
        if not value.strip():
            raise ValueError("This field cannot be blank. ")
        return value

    @model_validator(mode = "after")
    def validate_evidence_references(self):
        evidence_ids = [item.id for item in self.evidence if item.id is not None]

        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError("Evidence IDs must be unique. ")

        available_ids = set(evidence_ids)

        for attribute in self.context.values():
            for evidence_id in attribute.evidence_ids: 
                if evidence_id not in available_ids:
                    raise ValueError(
                        f"Unknown evidence reference: {evidence_id}"
                    )
        return self