"""Typed domain models and local validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar

ALLOWED_CONFIDENCE = frozenset({"high", "medium", "low", "provisional"})


class ModelValidationError(ValueError):
    """Raised when structured project data violates the model contract."""


def _require_text(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ModelValidationError(f"{field_name} must be a non-empty string")


def _require_text_list(value: list[str], field_name: str, *, allow_empty: bool = False) -> None:
    if not isinstance(value, list) or (not value and not allow_empty):
        raise ModelValidationError(f"{field_name} must be a{' possibly empty' if allow_empty else ' non-empty'} list")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise ModelValidationError(f"{field_name} must contain only non-empty strings")


@dataclass(frozen=True, slots=True)
class TriggerRule:
    id: str
    description: str
    triggers: list[str]
    primary_lens: str
    secondary_lenses: list[str]
    actions: list[str]
    avoid: list[str]
    exit_conditions: list[str]
    safety_notes: list[str]
    confidence: str
    source_refs: list[str]
    priority: int

    REQUIRED_FIELDS: ClassVar[tuple[str, ...]] = (
        "id", "description", "triggers", "primary_lens", "secondary_lenses",
        "actions", "avoid", "exit_conditions", "safety_notes", "confidence",
        "source_refs", "priority",
    )

    def __post_init__(self) -> None:
        for name in ("id", "description", "primary_lens"):
            _require_text(getattr(self, name), name)
        for name in ("triggers", "actions", "avoid", "exit_conditions", "safety_notes", "source_refs"):
            _require_text_list(getattr(self, name), name)
        _require_text_list(self.secondary_lenses, "secondary_lenses", allow_empty=True)
        if self.confidence not in ALLOWED_CONFIDENCE:
            raise ModelValidationError(
                f"confidence must be one of {sorted(ALLOWED_CONFIDENCE)}; got {self.confidence!r}"
            )
        if not isinstance(self.priority, int) or isinstance(self.priority, bool) or self.priority < 0:
            raise ModelValidationError("priority must be a non-negative integer")

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "TriggerRule":
        missing = [name for name in cls.REQUIRED_FIELDS if name not in value]
        if missing:
            raise ModelValidationError(f"missing required fields: {', '.join(missing)}")
        try:
            return cls(**{name: value[name] for name in cls.REQUIRED_FIELDS})
        except TypeError as exc:
            raise ModelValidationError(f"invalid rule structure: {exc}") from exc


@dataclass(frozen=True, slots=True)
class TriggerMatch:
    rule: TriggerRule
    strength: int
    matched_signals: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class LensSelection:
    primary_lens: str
    secondary_lenses: list[str]
    matches: list[TriggerMatch]
    conflict_detected: bool
    debug_explanation: str


@dataclass(frozen=True, slots=True)
class SafetyDecision:
    allowed: bool
    risk_level: str
    applicable_boundaries: list[str]
    required_behavior: list[str]
    prohibited_behavior: list[str]


@dataclass(frozen=True, slots=True)
class EngineResult:
    selected_primary_lens: str
    secondary_lenses: list[str]
    matched_rule_ids: list[str]
    actions: list[str]
    avoid: list[str]
    exit_conditions: list[str]
    safety_notes: list[str]
    confidence: str
    debug_explanation: str
    safety: SafetyDecision
