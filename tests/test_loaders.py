from __future__ import annotations

from pathlib import Path

import pytest

from mingren_skill.loaders import DataLoadError, load_trigger_rules


ROOT = Path(__file__).resolve().parents[1]


def test_loads_valid_rules_with_typed_priority() -> None:
    rules = load_trigger_rules(root=ROOT)
    assert len(rules) == 12
    assert {rule.id for rule in rules} >= {"explain-simply", "default-direct-explanation"}
    assert all(isinstance(rule.priority, int) for rule in rules)


def _write_project(tmp_path: Path, rules_yaml: str) -> Path:
    references = tmp_path / "references"
    references.mkdir()
    (references / "source.md").write_text("# Source\n\n## Method\n\nEvidence.\n", encoding="utf-8")
    (references / "trigger_rules.yaml").write_text(rules_yaml, encoding="utf-8")
    return tmp_path


def _rule(rule_id: str = "example", confidence: str = "high", source: str = "references/source.md#method") -> str:
    return f"""
  - id: {rule_id}
    description: Example rule
    triggers: [example]
    primary_lens: none
    secondary_lenses: []
    actions: [act]
    avoid: [avoid]
    exit_conditions: [done]
    safety_notes: [safe]
    confidence: {confidence}
    source_refs: [{source}]
    priority: 1
"""


def test_duplicate_ids_raise_clear_error(tmp_path: Path) -> None:
    root = _write_project(tmp_path, "rules:\n" + _rule() + _rule())
    with pytest.raises(DataLoadError, match="duplicate trigger rule ID: example"):
        load_trigger_rules(root=root)


def test_malformed_yaml_is_not_silently_ignored(tmp_path: Path) -> None:
    root = _write_project(tmp_path, "rules: [unterminated")
    with pytest.raises(DataLoadError, match="malformed YAML"):
        load_trigger_rules(root=root)


def test_unknown_confidence_is_rejected(tmp_path: Path) -> None:
    root = _write_project(tmp_path, "rules:\n" + _rule(confidence="certain"))
    with pytest.raises(DataLoadError, match="confidence must be one of"):
        load_trigger_rules(root=root)


def test_missing_source_reference_is_rejected(tmp_path: Path) -> None:
    root = _write_project(tmp_path, "rules:\n" + _rule(source="references/missing.md"))
    with pytest.raises(DataLoadError, match="references missing source file"):
        load_trigger_rules(root=root)
