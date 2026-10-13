from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from unwritten_rules.domain.inference import AIInference

class ExperienceAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")
    experience_id: UUID
    inferences: list[AIInference] = Field(default_factory=list)

    