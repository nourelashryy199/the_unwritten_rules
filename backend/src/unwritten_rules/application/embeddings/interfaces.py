
from typing import Protocol


class EmbeddingModel(Protocol):

    @property
    def dimensions(self) -> int:
        ...

    def encode(
        self,
        texts: list[str],
        batch_size: int,
    ) -> list[list[float]]:
        ...
