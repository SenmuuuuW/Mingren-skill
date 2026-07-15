from __future__ import annotations

from pathlib import Path

from mingren_skill.loaders import load_trigger_rules
from mingren_skill.router import DeterministicRouter


ROOT = Path(__file__).resolve().parents[1]


def router() -> DeterministicRouter:
    return DeterministicRouter(load_trigger_rules(root=ROOT))


def test_simple_explanation_routes_to_feynman() -> None:
    selection = router().route("Explain recursion simply")
    assert selection.primary_lens == "feynman"
    assert selection.matches[0].rule.id == "explain-simply"


def test_direct_question_does_not_force_socratic_questions() -> None:
    selection = router().route("What is a database index? Give me the answer directly")
    assert selection.primary_lens == "none"
    assert [match.rule.id for match in selection.matches] == ["default-direct-explanation"]


def test_conflicting_precision_and_simplicity_uses_conflict_rule() -> None:
    selection = router().route("Explain this simply but preserve exact technical precision")
    ids = [match.rule.id for match in selection.matches]
    assert selection.conflict_detected is True
    assert "detect-lens-conflict" in ids
    assert "explain-simply" in ids


def test_system_decomposition_beats_generic_fallback() -> None:
    selection = router().route("Break this system into modules and show the data flow")
    assert selection.primary_lens == "von-neumann"
    assert "decompose-complex-system" in [match.rule.id for match in selection.matches]
