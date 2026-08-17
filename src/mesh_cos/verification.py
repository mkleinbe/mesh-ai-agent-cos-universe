from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class VerificationResult:
    passed: bool
    evidence: list[str] = field(default_factory=list)
    reason: str = ""
