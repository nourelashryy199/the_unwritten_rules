from pydantic import BaseModel, ConfigDict, Field, field_validator


class RetrievalResult(BaseModel):

    model_config = ConfigDict(extra="forbid")

    record_id: str
    similarity_score: float = Field(ge=-1.0, le=1.0)
    rank: int = Field(gt=0)

    @field_validator("record_id")
    @classmethod
    def validate_record_id(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Record ID cannot be blank.")
        return value


class RetrievalConfig(BaseModel):

    model_config = ConfigDict(extra="forbid")

    top_k: int = Field(default=5, gt=0)