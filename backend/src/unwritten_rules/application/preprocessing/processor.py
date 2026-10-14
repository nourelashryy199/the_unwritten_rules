import hashlib
import json
from collections import defaultdict
from typing import Any

from unwritten_rules.application.preprocessing.models import(
    PreprocessedExperience, 
    PreprocessingResult,
)
from unwritten_rules.application.preprocessing.validator import(
    ExperienceValidator,
)
from unwritten_rules.domain.experience import Experience

class ExperienceProcessor: 
    def __init__(self, validator: ExperienceValidator | None = None):
        self.validator = validator or ExperienceValidator()
    def process(
            self, 
            records: list[dict[str, Any]],
    ) -> PreprocessingResult:
        result = PreprocessingResult()
        fingerprints: dict[str, list[int]] = defaultdict(list)

        for index, record in enumerate(records):
            experience, error = self.validator.validate(
                record,
                record_index=index, 
            )
            if error is not None: 
                result.invalid_records.append(error)
                continue
            if experience is None: 
                raise RuntimeError(
                    "Validator returned neither an experience nor an error. "
                )
            retrieval_text = self._build_retrieval_text(experience)
            fingerprint = self._fingerprint(experience)

            result.valid_records.append(
                PreprocessedExperience(
                    experience = experience, 
                    original_narrative = experience.narrative,
                    retrieval_text = retrieval_text,
                    content_fingerprint= fingerprint,
                )
            )
            fingerprints[fingerprint].append(index)
        result.duplicate_indices = {
            fingerprint: indices
            for fingerprint, indices in fingerprints.items()
            if len(indices) > 1
        }
        return result

    @staticmethod
    def _build_retrieval_text(experience: Experience) -> str: 
        parts = [
            f"Narrative: {experience.narrative}",
            f"Country: {experience.country}",
        ]
        for name, attribute in sorted(experience.context.items()):
            if attribute.status == "known":
                parts.append(f"{name}: {attribute.value}")
            else:
                parts.append(f"{name}: unknown")
        return "\n".join(parts)

    @staticmethod
    def _fingerprint(experience: Experience) -> str: 
        content = {
            "narrative": experience.narrative,
            "country": experience.country,
            "context": {
                name: attribute.model_dump(mode = "json")
                for name, attribute in sorted(experience.context.items())
            },
            "evidence": [
                item.model_dump(mode="json")
                for item in experience.evidence
            ],
        }
        canonical_json = json.dumps(
            content, 
            sort_keys = True, 
            ensure_ascii = False, 
            separators = (",", ";"),
        )
        return hashlib.sha256(
            canonical_json.encode("utf-8")
        ).hexdigest()