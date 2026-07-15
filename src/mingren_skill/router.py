"""Deterministic and inspectable first-version trigger router."""

from __future__ import annotations

import re
from collections.abc import Iterable

from mingren_skill.models import LensSelection, TriggerMatch, TriggerRule

PATTERNS: dict[str, tuple[str, ...]] = {
    "explain-simply": (r"\bexplain\b.*\b(simple|simply|plain|beginner)", r"\beli5\b", r"\bwhat does\b.*\bmean\b"),
    "expose-understanding-gap": (r"\bi (still )?don'?t understand\b", r"\bwhere am i going wrong\b", r"\bmissing step\b"),
    "clarify-definition": (r"\bdefine\b", r"\bwhat (exactly )?do(es| you) .* mean\b", r"\bambiguous\b"),
    "challenge-assumption": (r"\bassum(e|ption|ing)\b", r"\bhidden premise\b", r"\bchallenge (this|my|the)\b"),
    "test-with-counterexample": (r"\bcounterexample\b", r"\b(always|never|all|none)\b", r"\bdoes this hold\b"),
    "decompose-complex-system": (r"\b(break|split|decompose)\b.*\b(system|modules?|components?)\b", r"\barchitecture\b", r"\bdata flow\b"),
    "change-representation": (r"\b(diagram|table|graph|state machine|equation|flowchart)\b", r"\banother representation\b", r"\bturn .* into\b.*\b(model|table|graph)\b"),
    "identify-structure": (r"\b(pattern|invariant|isomorphic|structural similarity|analogy)\b", r"\bsame structure\b"),
    "analyze-dynamic-change": (r"\b(feedback loop|trend|second-order|dynamic|over time|unintended consequence)\b", r"\bwhat changes if\b"),
    "minimize-unnecessary-intervention": (r"\b(minimum|minimal|least|smallest)\b.*\b(intervention|change|action)\b", r"\bdo nothing\b", r"\bnon-intervention\b"),
    "detect-lens-conflict": (r"\bconflicting lenses?\b", r"\bsimpl(?:e|y|ify)\b.*\b(precise|precision|exact)\b", r"\bquestion.*direct answer\b"),
}

COMPATIBLE_LENS_PAIRS = {
    frozenset({"feynman", "socrates"}),
    frozenset({"von-neumann", "laozi"}),
}


class DeterministicRouter:
    def __init__(self, rules: Iterable[TriggerRule]):
        self.rules = {rule.id: rule for rule in rules}
        missing = set(PATTERNS) - self.rules.keys()
        if missing:
            raise ValueError(f"router is missing configured rules: {', '.join(sorted(missing))}")
        if "default-direct-explanation" not in self.rules:
            raise ValueError("router requires default-direct-explanation")

    def route(self, user_input: str) -> LensSelection:
        text = " ".join(user_input.lower().split())
        matches: list[TriggerMatch] = []
        for rule_id, patterns in PATTERNS.items():
            signals = [pattern for pattern in patterns if re.search(pattern, text, re.IGNORECASE)]
            if signals:
                rule = self.rules[rule_id]
                strength = len(signals) * 10 + rule.priority
                matches.append(TriggerMatch(rule=rule, strength=strength, matched_signals=signals))

        if not matches:
            default = self.rules["default-direct-explanation"]
            return LensSelection(
                primary_lens=default.primary_lens,
                secondary_lenses=[],
                matches=[TriggerMatch(default, default.priority, ["no clear lens signal"])],
                conflict_detected=False,
                debug_explanation="No specific trigger matched; selected direct explanation fallback.",
            )

        matches.sort(key=lambda match: (-match.strength, -match.rule.priority, match.rule.id))
        conflict = self._has_conflict(matches)
        if conflict and all(match.rule.id != "detect-lens-conflict" for match in matches):
            rule = self.rules["detect-lens-conflict"]
            matches.insert(0, TriggerMatch(rule, 10_000 + rule.priority, ["incompatible candidate lenses"]))

        primary_match = next(
            (match for match in matches if match.rule.primary_lens != "none"),
            matches[0],
        )
        secondary: list[str] = []
        for match in matches:
            lens = match.rule.primary_lens
            if lens not in {"none", primary_match.rule.primary_lens} and lens not in secondary:
                if frozenset({lens, primary_match.rule.primary_lens}) in COMPATIBLE_LENS_PAIRS:
                    secondary.append(lens)
        for lens in primary_match.rule.secondary_lenses:
            if lens != primary_match.rule.primary_lens and lens not in secondary:
                secondary.append(lens)

        return LensSelection(
            primary_lens=primary_match.rule.primary_lens,
            secondary_lenses=secondary,
            matches=matches,
            conflict_detected=conflict,
            debug_explanation=(
                f"Matched {', '.join(match.rule.id for match in matches)}; "
                f"ranked by transparent pattern strength and rule priority."
            ),
        )

    @staticmethod
    def _has_conflict(matches: list[TriggerMatch]) -> bool:
        if any(match.rule.id == "detect-lens-conflict" for match in matches):
            return True
        lenses = {match.rule.primary_lens for match in matches if match.rule.primary_lens != "none"}
        if len(lenses) < 2:
            return False
        return any(
            frozenset({left, right}) not in COMPATIBLE_LENS_PAIRS
            for left in lenses for right in lenses if left != right
        )
