
from typing import Any

from pydantic import ValidationError

from unwritten_rules.domain.experience import Experience
from unwritten_rules.application.preprocessing.models import (
    PreprocessingError,
)


class ExperienceValidator:
    def validate(
        self,
        record: dict[str, Any],
        record_index: int,
    ) -> tuple[Experience | None, PreprocessingError | None]:
        try:
            experience = Experience.model_validate(record)
            return experience, None

        except ValidationError as exc:
            error = PreprocessingError(
                record_index=record_index,
                errors=exc.errors(
                    include_url=False,
                    include_context=False,
                    include_input=False,
                ),
            )
            return None, error
