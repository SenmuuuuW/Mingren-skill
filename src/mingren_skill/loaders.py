"""Strict filesystem loaders for rules, research, and evaluation data."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from mingren_skill.models import ModelValidationError, TriggerRule


class DataLoadError(ValueError):
    """Raised when a project data file cannot be loaded safely."""


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_yaml(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)
    except FileNotFoundError as exc:
        raise DataLoadError(f"YAML file does not exist: {path}") from exc
    except OSError as exc:
        raise DataLoadError(f"cannot read YAML file {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise DataLoadError(f"malformed YAML in {path}: {exc}") from exc


def load_trigger_rules(path: Path | None = None, *, root: Path | None = None) -> list[TriggerRule]:
    root = (root or project_root()).resolve()
    path = (path or root / "references" / "trigger_rules.yaml").resolve()
    data = _load_yaml(path)
    if not isinstance(data, dict) or not isinstance(data.get("rules"), list):
        raise DataLoadError(f"{path} must contain a top-level 'rules' list")
    if not data["rules"]:
        raise DataLoadError(f"{path} contains no trigger rules")

    rules: list[TriggerRule] = []
    seen: set[str] = set()
    for index, raw_rule in enumerate(data["rules"]):
        if not isinstance(raw_rule, dict):
            raise DataLoadError(f"rule at index {index} must be a mapping")
        try:
            rule = TriggerRule.from_mapping(raw_rule)
        except ModelValidationError as exc:
            raise DataLoadError(f"invalid rule at index {index}: {exc}") from exc
        if rule.id in seen:
            raise DataLoadError(f"duplicate trigger rule ID: {rule.id}")
        seen.add(rule.id)
        _verify_source_refs(rule, root)
        rules.append(rule)
    return rules


def _verify_source_refs(rule: TriggerRule, root: Path) -> None:
    for reference in rule.source_refs:
        relative_path, _, anchor = reference.partition("#")
        source_path = root / relative_path
        if not source_path.is_file():
            raise DataLoadError(f"rule {rule.id!r} references missing source file: {relative_path}")
        if anchor:
            content = source_path.read_text(encoding="utf-8")
            anchors = {_heading_anchor(line) for line in content.splitlines() if line.startswith("#")}
            if anchor not in anchors:
                raise DataLoadError(f"rule {rule.id!r} references missing source anchor: {reference}")


def _heading_anchor(line: str) -> str:
    heading = line.lstrip("#").strip().lower()
    normalized = "".join(character for character in heading if character.isalnum() or character in " -")
    return "-".join(normalized.split())


def load_thinker_markdown(name: str, *, root: Path | None = None) -> str:
    if not name or any(character not in "abcdefghijklmnopqrstuvwxyz-" for character in name):
        raise DataLoadError(f"invalid thinker name: {name!r}")
    path = (root or project_root()) / "references" / "thinkers" / f"{name}.md"
    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise DataLoadError(f"thinker research file does not exist: {path}") from exc
    if not content.strip():
        raise DataLoadError(f"thinker research file is empty: {path}")
    return content


def load_evaluation_cases(path: Path | None = None, *, root: Path | None = None) -> list[dict[str, Any]]:
    root = root or project_root()
    path = path or root / "evals" / "cases.yaml"
    data = _load_yaml(path)
    if not isinstance(data, dict) or not isinstance(data.get("cases"), list):
        raise DataLoadError(f"{path} must contain a top-level 'cases' list")
    required = {
        "id", "input", "expected_rules", "forbidden_rules", "expected_primary_lens",
        "expected_safety_behavior", "notes",
    }
    for index, case in enumerate(data["cases"]):
        if not isinstance(case, dict):
            raise DataLoadError(f"evaluation case at index {index} must be a mapping")
        missing = sorted(required - case.keys())
        if missing:
            raise DataLoadError(f"evaluation case at index {index} missing fields: {', '.join(missing)}")
    return data["cases"]
