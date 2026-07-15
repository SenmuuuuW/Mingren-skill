from __future__ import annotations

import shutil
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("repository_validator", ROOT / "scripts" / "validate.py")
assert SPEC is not None and SPEC.loader is not None
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)
validate_repository = VALIDATOR.validate_repository


def test_validator_succeeds_on_repository() -> None:
    assert validate_repository(ROOT) == []


def test_validator_reports_missing_required_files(tmp_path: Path) -> None:
    errors = validate_repository(tmp_path)
    assert "missing required file: README.md" in errors
    assert "missing required file: references/trigger_rules.yaml" in errors


def test_validator_reports_failure_taxonomy_gap(tmp_path: Path) -> None:
    for relative in (
        "README.md", "CHANGELOG.md", "AGENTS.md", "pyproject.toml",
        "references/distillation_framework.md", "references/safety_boundaries.md",
        "references/trigger_rules.yaml", "evals/cases.yaml",
    ):
        source = ROOT / relative
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(source, target)
    taxonomy = tmp_path / "evals" / "failure_taxonomy.md"
    taxonomy.write_text("# Failure Taxonomy\n\n## F01 Only one\n", encoding="utf-8")
    errors = validate_repository(tmp_path)
    assert any("failure taxonomy missing categories" in error for error in errors)
