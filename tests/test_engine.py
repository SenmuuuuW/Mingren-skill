from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from mingren_skill.engine import MingrenSkillEngine
from mingren_skill.loaders import load_trigger_rules


ROOT = Path(__file__).resolve().parents[1]


def engine() -> MingrenSkillEngine:
    return MingrenSkillEngine(load_trigger_rules(root=ROOT))


def test_engine_result_is_structured_plan_not_persona_answer() -> None:
    result = engine().plan("Explain recursion simply")
    data = asdict(result)
    assert data["selected_primary_lens"] == "feynman"
    assert data["matched_rule_ids"] == ["explain-simply"]
    assert data["actions"]
    assert data["avoid"]
    assert data["exit_conditions"]
    assert "I am Feynman" not in str(data)


def test_safety_precedence_is_merged_into_plan() -> None:
    result = engine().plan("Explain medication dosing simply for this patient")
    assert result.safety.risk_level == "medium"
    assert result.actions[0].startswith("prioritize factual correctness")
    assert any("professional authority" in item for item in result.avoid)
    assert "explain-simply" in result.matched_rule_ids


def test_default_direct_explanation() -> None:
    result = engine().plan("Convert 2 kilometers to meters")
    assert result.selected_primary_lens == "none"
    assert result.matched_rule_ids == ["default-direct-explanation"]


def test_conflict_resolution_does_not_duplicate_actions() -> None:
    result = engine().plan("Explain this simply but preserve exact technical precision")
    assert "detect-lens-conflict" in result.matched_rule_ids
    assert len(result.actions) == len(set(result.actions))
    assert "Conflict logic" in result.debug_explanation
