from typing import Any 
from pydantic import BaseModel, ConfigDict, Field
from unwritten_rules.domain.experience import Experience

class PreprocessedExperience(BaseModel):
    model_config = ConfigDict(extra = "forbid")

    experience: Experience
    original_narrative: str
    retrieval_text: str
    content_fingerprint: str

class PreprocessingError(BaseModel):
    model_config = ConfigDict(extra = "forbid")
    record_index: int
    errors: list[dict[str, Any]] = Field(default_factory = list)

class PreprocessingResult(BaseModel):
    model_config = ConfigDict(extra = "forbid")

    valid_records: list[PreprocessedExperience] = Field(
        default_factory = list
    )
    invalid_records: list[PreprocessingError] = Field(
        default_factory = list 
    )
    duplicate_indices: dict[str, list[int]] = Field(
        default_factory = dict
    )
