
import math

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


class EmbeddingConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    dimensions: int = Field(default=384, gt=0)
    batch_size: int = Field(default=32, gt=0)

    @field_validator("model_name")
    @classmethod
    def validate_model_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Model name cannot be blank.")
        return value


class EmbeddedExperience(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_id: str
    embedding: list[float]
    model_name: str
    dimensions: int = Field(gt=0)

    @field_validator("record_id", "model_name")
    @classmethod
    def validate_nonempty_string(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Field cannot be blank.")
        return value

    @field_validator("embedding")
    @classmethod
    def validate_embedding(cls, value: list[float]) -> list[float]:
        if not value:
            raise ValueError("Embedding cannot be empty.")

        if not all(math.isfinite(component) for component in value):
            raise ValueError(
                "Embedding must contain only finite values."
            )

        return value

    @model_validator(mode="after")
    def validate_dimensions(self):
        if len(self.embedding) != self.dimensions:
            raise ValueError(
                "Embedding length does not match declared dimensions."
            )

        return self
