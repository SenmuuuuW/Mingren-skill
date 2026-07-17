"""Main orchestration for structured thinker-lens plans."""

from __future__ import annotations

from collections.abc import Iterable

from mingren_skill.loaders import load_trigger_rules
from mingren_skill.models import EngineResult, TriggerMatch, TriggerRule
from mingren_skill.router import DeterministicRouter
from mingren_skill.safety import evaluate_safety

CONFIDENCE_RANK = {"provisional": 0, "low": 1, "medium": 2, "high": 3}


def _unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(values))


class MingrenSkillEngine:
    def __init__(self, rules: list[TriggerRule] | None = None):
        self.rules = rules or load_trigger_rules()
        self.router = DeterministicRouter(self.rules)

    def plan(self, user_input: str) -> EngineResult:
        if not isinstance(user_input, str) or not user_input.strip():
            raise ValueError("user_input must be a non-empty string")
        safety = evaluate_safety(user_input)
        selection = self.router.route(user_input)
        matches = self._compatible_matches(selection.matches, selection.primary_lens)

        actions = _unique(action for match in matches for action in match.rule.actions)
        avoid = _unique(item for match in matches for item in match.rule.avoid)
        exits = _unique(item for match in matches for item in match.rule.exit_conditions)
        safety_notes = _unique(
            [note for match in matches for note in match.rule.safety_notes]
            + safety.required_behavior
            + safety.prohibited_behavior
        )
        if safety.applicable_boundaries:
            actions = _unique(safety.required_behavior + actions)
            avoid = _unique(safety.prohibited_behavior + avoid)

        confidence = min(
            (match.rule.confidence for match in matches),
            key=lambda value: CONFIDENCE_RANK[value],
        )
        explanation = selection.debug_explanation
        if selection.conflict_detected:
            explanation += " Conflict logic retained only compatible actions and safety precedence."
        if safety.applicable_boundaries:
            explanation += (
                " Safety classifier is a transparent keyword-based first version, not a complete "
                "professional classifier; its boundaries take precedence."
            )

        return EngineResult(
            selected_primary_lens=selection.primary_lens,
            secondary_lenses=selection.secondary_lenses,
            matched_rule_ids=[match.rule.id for match in matches],
            actions=actions,
            avoid=avoid,
            exit_conditions=exits,
            safety_notes=safety_notes,
            confidence=confidence,
            debug_explanation=explanation,
            safety=safety,
        )

    @staticmethod
    def _compatible_matches(matches: list[TriggerMatch], primary_lens: str) -> list[TriggerMatch]:
        conflict = [match for match in matches if match.rule.id == "detect-lens-conflict"]
        substantive = [
            match for match in matches
            if match.rule.primary_lens in {primary_lens, "none"}
        ]
        return _unique_matches(conflict + substantive)


def _unique_matches(matches: list[TriggerMatch]) -> list[TriggerMatch]:
    seen: set[str] = set()
    result: list[TriggerMatch] = []
    for match in matches:
        if match.rule.id not in seen:
            seen.add(match.rule.id)
            result.append(match)
    return result
