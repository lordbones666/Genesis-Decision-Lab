from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class PolicyResult:
    value: Any
    artifacts: dict[str, Any] = field(default_factory=dict)


class AlgorithmContract(Protocol):
    version: str

    def validate_cfg(self, cfg: dict[str, Any]) -> list[str]: ...

    def apply(
        self, state: dict[str, Any], evidence: dict[str, Any], cfg: dict[str, Any]
    ) -> PolicyResult: ...

    def explain(self, artifacts: dict[str, Any]) -> dict[str, Any]: ...
