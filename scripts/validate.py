#!/usr/bin/env python3
"""Validate repository structure, research records, YAML, and evaluation fixtures."""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import re
import sys
import tempfile
import tomllib
import unicodedata
from pathlib import Path
from typing import Sequence

import yaml

REQUIRED_FILES = (
    "README.md", "CHANGELOG.md", "AGENTS.md", "pyproject.toml",
    "SKILL.md", "skill-manifest.yaml", "README.zh-CN.md",
    "docs/runtime_contract.md", "docs/installation.md",
    "docs/requirements_traceability.md",
    "docs/behavior_alignment_review.md",
    "references/distillation_framework.md", "references/safety_boundaries.md",
    "references/trigger_rules.yaml", "evals/failure_taxonomy.md", "evals/cases.yaml",
    "evals/host_cases.yaml", "evals/manual_evaluation.md",
    "references/thinkers/feynman.md", "references/thinkers/socrates.md",
    "references/thinkers/von-neumann.md", "references/thinkers/laozi.md",
    "src/mingren_skill/__init__.py", "src/mingren_skill/models.py",
    "src/mingren_skill/loaders.py", "src/mingren_skill/router.py",
    "src/mingren_skill/engine.py", "src/mingren_skill/safety.py",
    "src/mingren_skill/language.py", "src/mingren_skill/prompt_builder.py",
    "src/mingren_skill/response_validator.py",
    "src/mingren_skill/__main__.py", "scripts/validate.py", "scripts/build_skill_bundle.py",
    "scripts/__init__.py",
    "tests/test_loaders.py", "tests/test_router.py", "tests/test_engine.py",
    "tests/test_safety.py", "tests/test_validation.py", "tests/test_language.py",
    "tests/test_prompt_builder.py", "tests/test_response_validator.py", "tests/test_cli.py",
    "tests/test_bundle_builder.py",
)
THINKER_HEADINGS = (
    "Source basis", "Core worldview", "Thinking pattern", "Teaching style",
    "Explanation method", "Questioning method", "Best subjects", "Weak subjects",
    "Trigger phrases", "Response structure", "Example response", "Safety boundaries",
)
RULE_FIELDS = {
    "id", "description", "triggers", "primary_lens", "secondary_lenses", "actions",
    "avoid", "exit_conditions", "safety_notes", "confidence", "source_refs", "priority",
}
RULE_LIST_FIELDS = {
    "triggers", "secondary_lenses", "actions", "avoid", "exit_conditions",
    "safety_notes", "source_refs",
}
RULE_STRING_FIELDS = {"id", "description", "primary_lens", "confidence"}
CASE_FIELDS = {
    "id", "input", "expected_rules", "forbidden_rules", "expected_primary_lens",
    "expected_safety_behavior", "notes",
}
CONFIDENCE = {"high", "medium", "low", "provisional"}
FAILURE_IDS = {f"F{number:02d}" for number in range(1, 21)}
TODO_FIELDS = ("claim", "preferred source type", "verification needed", "current confidence")
SNAPSHOT_FIELDS = {"input", "selected_lenses", "applied_rules", "required_fragments"}
HOST_CASE_FIELDS = {
    "id", "user_input", "required_files", "expected_primary_lens",
    "allowed_secondary_lenses", "required_behaviors", "forbidden_behaviors",
    "safety_expectation", "language_expectation", "notes", "trigger_class",
    "requested_lenses", "equivalence_group",
}
SUPPORTED_LENSES = {"feynman", "socrates", "von-neumann", "laozi"}
CANONICAL_LENSES = SUPPORTED_LENSES | {"none"}
HOST_TRIGGER_CLASSES = {
    "neutral", "generic_simplicity", "explicit_lens", "distinctive_method",
    "multi_lens", "unsupported_thinker", "quotation_only", "non_trigger",
    "safety_override", "instruction_integrity",
}
HOST_LIST_FIELDS = {
    "required_files", "allowed_secondary_lenses", "required_behaviors",
    "forbidden_behaviors", "requested_lenses",
}
HOST_NONEMPTY_LIST_FIELDS = {
    "required_files", "required_behaviors", "forbidden_behaviors",
}
HOST_STRING_FIELDS = {
    "id", "user_input", "expected_primary_lens", "safety_expectation",
    "language_expectation", "notes", "trigger_class",
}
HOST_SAFETY_EXPECTATIONS = {
    "normal", "emergency_override", "instruction_integrity", "source_integrity",
}
HOST_LANGUAGE_EXPECTATIONS = {"en", "zh-CN", "zh-CN-mixed"}
NON_TRIGGER_CLASSES = {
    "neutral", "generic_simplicity", "unsupported_thinker", "quotation_only",
    "non_trigger", "instruction_integrity",
}
BEHAVIOR_CONTRACT_FIELDS = {
    "canonical_no_lens", "generic_simplicity_rule", "quotation_only_rule",
    "explicit_feynman_rule",
}
FORBIDDEN_BUNDLE_PARTS = {
    ".git", ".venv", "venv", "__pycache__", ".pytest_cache", "tests",
    "scripts", "src", "build", "dist", ".env",
}
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def _load_yaml(path: Path, errors: list[str]) -> object | None:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, yaml.YAMLError) as exc:
        errors.append(f"cannot parse YAML {path}: {exc}")
        return None


def _anchor(heading: str) -> str:
    cleaned = "".join(character for character in heading.lower() if character.isalnum() or character in " -")
    return "-".join(cleaned.split())


def _extract_string_set(path: Path, variable_name: str) -> set[str] | None:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return None
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == variable_name for target in node.targets):
            continue
        if not isinstance(node.value, ast.Call) or not node.value.args:
            return None
        try:
            value = ast.literal_eval(node.value.args[0])
        except (ValueError, TypeError):
            return None
        return set(value) if isinstance(value, (set, list, tuple)) else None
    return None


def _validate_markdown_links(root: Path, files: list[str], errors: list[str]) -> None:
    approved = {Path(item).as_posix() for item in files}
    for relative in sorted(approved):
        path = root / relative
        if path.suffix.lower() != ".md" or not path.is_file():
            continue
        for raw_target in MARKDOWN_LINK_RE.findall(path.read_text(encoding="utf-8")):
            target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            file_target = target.split("#", 1)[0]
            resolved = (path.parent / file_target).resolve()
            try:
                bundle_relative = resolved.relative_to(root).as_posix()
            except ValueError:
                errors.append(f"runtime link escapes repository: {relative} -> {target}")
                continue
            if bundle_relative not in approved and not any(item.startswith(bundle_relative.rstrip("/") + "/") for item in approved):
                errors.append(f"runtime link is not included in bundle: {relative} -> {target}")


def _is_string_list(value: object) -> bool:
    return isinstance(value, list) and all(
        isinstance(item, str) and bool(item.strip()) for item in value
    )


def _validated_relative_path(value: str) -> Path | None:
    if (
        not value
        or not value.strip()
        or "\\" in value
        or ":" in value
        or any(
            unicodedata.category(character) in {"Cc", "Cf", "Zl", "Zp"}
            for character in value
        )
    ):
        return None
    try:
        path = Path(value)
    except (OSError, TypeError, ValueError):
        return None
    if path.is_absolute() or ".." in path.parts or path == Path("."):
        return None
    return path


def _validate_behavior_contract(
    root: Path,
    rules_data: object | None,
    host_data: object | None,
    errors: list[str],
    runtime_files: set[str] | None = None,
) -> None:
    """Check declared host expectations without attempting semantic prompt evaluation."""
    if runtime_files is None:
        manifest_errors: list[str] = []
        manifest = _load_yaml(root / "skill-manifest.yaml", manifest_errors)
        if isinstance(manifest, dict):
            required = manifest.get("required_files")
            optional = manifest.get("optional_files")
            if _is_string_list(required) and _is_string_list(optional):
                runtime_files = {
                    "skill-manifest.yaml",
                    *(Path(item).as_posix() for item in required),
                    *(Path(item).as_posix() for item in optional),
                }
    rule_by_id: dict[str, dict[str, object]] = {}
    contract_lenses: dict[str, object] = {}
    if isinstance(rules_data, dict) and isinstance(rules_data.get("rules"), list):
        rule_by_id = {
            rule["id"]: rule
            for rule in rules_data["rules"]
            if isinstance(rule, dict) and isinstance(rule.get("id"), str)
        }
        contract = rules_data.get("behavior_contract")
        if not isinstance(contract, dict):
            errors.append("trigger_rules.yaml behavior_contract must be a mapping")
        else:
            missing = BEHAVIOR_CONTRACT_FIELDS - contract.keys()
            if missing:
                errors.append(
                    "trigger behavior_contract missing fields: "
                    + ", ".join(sorted(missing))
                )
            if contract.get("canonical_no_lens") != "none":
                errors.append("trigger behavior_contract canonical_no_lens must be 'none'")
            expected_lenses = {
                "generic_simplicity_rule": "none",
                "quotation_only_rule": "none",
                "explicit_feynman_rule": "feynman",
            }
            for field, expected_lens in expected_lenses.items():
                rule_id = contract.get(field)
                if not isinstance(rule_id, str) or not rule_id:
                    errors.append(f"trigger behavior_contract {field} must name a rule")
                    continue
                rule = rule_by_id.get(rule_id)
                if rule is None:
                    errors.append(
                        f"trigger behavior_contract {field} references unknown rule: {rule_id}"
                    )
                    continue
                actual_lens = rule.get("primary_lens")
                contract_lenses[field] = actual_lens
                if actual_lens != expected_lens:
                    errors.append(
                        f"trigger behavior_contract {field} must route to {expected_lens}"
                    )

    if not isinstance(host_data, dict) or not isinstance(host_data.get("cases"), list):
        errors.append("host_cases.yaml must contain a top-level cases list")
        return

    host_cases = host_data["cases"]
    if len(host_cases) < 15:
        errors.append("host_cases.yaml must contain at least 15 cases")
    seen: set[str] = set()
    groups: dict[str, list[tuple[object, ...]]] = {}
    for index, case in enumerate(host_cases):
        if not isinstance(case, dict):
            errors.append(f"host case {index} is not a mapping")
            continue
        missing = HOST_CASE_FIELDS - case.keys()
        if missing:
            errors.append(f"host case {index} missing fields: {', '.join(sorted(missing))}")

        case_id_value = case.get("id")
        case_label = case_id_value if isinstance(case_id_value, str) and case_id_value else str(index)
        for field in HOST_STRING_FIELDS:
            value = case.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"host case {case_label} field {field} must be a non-empty string")
        for field in HOST_LIST_FIELDS:
            value = case.get(field)
            if not _is_string_list(value) or (
                field in HOST_NONEMPTY_LIST_FIELDS and not value
            ):
                qualifier = "a non-empty" if field in HOST_NONEMPTY_LIST_FIELDS else "a"
                errors.append(
                    f"host case {case_label} field {field} must be {qualifier} list of strings"
                )

        if not isinstance(case_id_value, str) or not case_id_value.strip():
            errors.append(f"host case {index} has invalid ID")
        elif case_id_value in seen:
            errors.append(f"duplicate host case ID: {case_id_value}")
        else:
            seen.add(case_id_value)

        expected_lens = case.get("expected_primary_lens")
        if not isinstance(expected_lens, str) or expected_lens not in CANONICAL_LENSES:
            errors.append(
                f"host case {case_label} has unsupported expected_primary_lens: {expected_lens}"
            )
        allowed_raw = case.get("allowed_secondary_lenses")
        requested_raw = case.get("requested_lenses")
        allowed = allowed_raw if _is_string_list(allowed_raw) else []
        requested = requested_raw if _is_string_list(requested_raw) else []
        for label, lenses in (("secondary", allowed), ("requested", requested)):
            unknown = set(lenses) - SUPPORTED_LENSES
            if unknown:
                errors.append(
                    f"host case {case_label} has unsupported {label} lenses: "
                    + ", ".join(sorted(unknown))
                )
            if len(lenses) != len(set(lenses)):
                errors.append(f"host case {case_label} has duplicate {label} lenses")
        if expected_lens != "none" and expected_lens in allowed:
            errors.append(f"host case {case_label} repeats its primary lens as secondary")

        required_files = case.get("required_files")
        if _is_string_list(required_files):
            for relative in required_files:
                relative_path = Path(relative)
                if relative_path.is_absolute() or ".." in relative_path.parts:
                    errors.append(
                        f"host case {case_label} required file escapes repository: {relative}"
                    )
                    continue
                relative_path = _validated_relative_path(relative)
                if relative_path is None:
                    errors.append(
                        f"host case {case_label} required file has invalid repository path: {relative!r}"
                    )
                    continue
                try:
                    resolved = (root / relative_path).resolve()
                except (OSError, RuntimeError, ValueError):
                    errors.append(
                        f"host case {case_label} required file has invalid repository path: {relative!r}"
                    )
                    continue
                try:
                    resolved.relative_to(root)
                except ValueError:
                    errors.append(
                        f"host case {case_label} required file escapes repository: {relative}"
                    )
                    continue
                if (root / relative_path).is_symlink() or not resolved.is_file():
                    errors.append(f"host case {case_label} references missing file: {relative}")
                    continue
                if runtime_files is not None and relative_path.as_posix() not in runtime_files:
                    errors.append(
                        f"host case {case_label} required file is not in runtime bundle: {relative}"
                    )

        safety_expectation = case.get("safety_expectation")
        if (
            not isinstance(safety_expectation, str)
            or safety_expectation not in HOST_SAFETY_EXPECTATIONS
        ):
            errors.append(
                f"host case {case_label} has invalid safety_expectation: {safety_expectation}"
            )
        language_expectation = case.get("language_expectation")
        if (
            not isinstance(language_expectation, str)
            or language_expectation not in HOST_LANGUAGE_EXPECTATIONS
        ):
            errors.append(
                f"host case {case_label} has invalid language_expectation: {language_expectation}"
            )
        required_behaviors = case.get("required_behaviors")
        forbidden_behaviors = case.get("forbidden_behaviors")
        if _is_string_list(required_behaviors) and _is_string_list(forbidden_behaviors):
            overlap = set(required_behaviors) & set(forbidden_behaviors)
            if overlap:
                errors.append(
                    f"host case {case_label} requires and forbids the same behaviors: "
                    + ", ".join(sorted(overlap))
                )

        trigger_class = case.get("trigger_class")
        if not isinstance(trigger_class, str) or trigger_class not in HOST_TRIGGER_CLASSES:
            errors.append(f"host case {case_label} has invalid trigger_class: {trigger_class}")
        if isinstance(trigger_class, str) and trigger_class in NON_TRIGGER_CLASSES and expected_lens != "none":
            errors.append(f"host case {case_label} non-trigger cannot require a thinker lens")
        if trigger_class == "generic_simplicity":
            contract_lens = contract_lenses.get("generic_simplicity_rule", "none")
            if expected_lens != "none" or expected_lens != contract_lens:
                errors.append(f"host case {case_label} generic simplicity must expect no lens")
            if requested_raw != []:
                errors.append(f"host case {case_label} generic simplicity cannot request a lens")
        elif trigger_class == "quotation_only":
            contract_lens = contract_lenses.get("quotation_only_rule", "none")
            if expected_lens != "none" or expected_lens != contract_lens:
                errors.append(f"host case {case_label} quotation-only request must expect no lens")
            if requested_raw != []:
                errors.append(
                    f"host case {case_label} quotation-only classification cannot include an explicit teaching lens"
                )
            if safety_expectation != "source_integrity":
                errors.append(
                    f"host case {case_label} quotation-only request must use source_integrity safety"
                )
        elif trigger_class == "explicit_lens":
            if len(requested) != 1:
                errors.append(
                    f"host case {case_label} explicit lens request must declare exactly one requested lens"
                )
            elif expected_lens != requested[0]:
                errors.append(
                    f"host case {case_label} explicit lens request must select {requested[0]}"
                )
        elif trigger_class == "distinctive_method":
            if (
                not isinstance(expected_lens, str)
                or expected_lens not in SUPPORTED_LENSES
            ):
                errors.append(
                    f"host case {case_label} distinctive method must select a supported lens"
                )
            if requested_raw != []:
                errors.append(
                    f"host case {case_label} distinctive method must not declare an explicit requested lens"
                )
        elif trigger_class == "multi_lens":
            if len(requested) < 2:
                errors.append(
                    f"host case {case_label} multi-lens request must declare at least two lenses"
                )
            elif expected_lens not in requested:
                errors.append(
                    f"host case {case_label} multi-lens primary must be one of the requested lenses"
                )
            unrequested = set(allowed) - set(requested)
            if unrequested:
                errors.append(
                    f"host case {case_label} permits unrequested secondary lenses: "
                    + ", ".join(sorted(unrequested))
                )
        elif trigger_class == "unsupported_thinker":
            if expected_lens != "none":
                errors.append(
                    f"host case {case_label} unsupported thinker must use neutral primary fallback"
                )
            if requested_raw != []:
                errors.append(
                    f"host case {case_label} unsupported thinker cannot enter the supported lens list"
                )
        elif (
            isinstance(trigger_class, str)
            and trigger_class in {"safety_override", "instruction_integrity"}
        ):
            if expected_lens != "none":
                errors.append(f"host case {case_label} override must expect no lens")
            expected_safety = (
                "emergency_override"
                if trigger_class == "safety_override"
                else "instruction_integrity"
            )
            if safety_expectation != expected_safety:
                errors.append(
                    f"host case {case_label} {trigger_class} must use {expected_safety} safety"
                )

        equivalence_group = case.get("equivalence_group")
        if equivalence_group is not None and (
            not isinstance(equivalence_group, str) or not equivalence_group.strip()
        ):
            errors.append(
                f"host case {case_label} equivalence_group must be null or a non-empty string"
            )
        elif (
            isinstance(equivalence_group, str)
            and equivalence_group
            and isinstance(expected_lens, str)
            and isinstance(trigger_class, str)
        ):
            groups.setdefault(equivalence_group, []).append(
                (case_label, expected_lens, trigger_class, tuple(requested), tuple(allowed))
            )

    for group, members in groups.items():
        if len(members) < 2:
            errors.append(f"host equivalence group {group!r} must link at least two cases")
            continue
        signatures = {member[1:] for member in members}
        if len(signatures) != 1:
            case_ids = ", ".join(member[0] for member in members)
            errors.append(
                f"host equivalence group {group!r} has conflicting trigger expectations: {case_ids}"
            )


def _validate_runtime(root: Path, rules_data: object | None, errors: list[str]) -> None:
    manifest = _load_yaml(root / "skill-manifest.yaml", errors)
    if not isinstance(manifest, dict):
        errors.append("skill-manifest.yaml must contain a mapping")
        return
    required = manifest.get("required_files")
    optional = manifest.get("optional_files")
    if not isinstance(required, list) or not all(isinstance(item, str) for item in required):
        errors.append("manifest required_files must be a list of paths")
        return
    if not isinstance(optional, list) or not all(isinstance(item, str) for item in optional):
        errors.append("manifest optional_files must be a list of paths")
        return
    runtime_files = ["skill-manifest.yaml", *required, *optional]
    runtime_paths: dict[str, Path] = {}
    for relative in runtime_files:
        relative_path = _validated_relative_path(relative)
        if relative_path is None:
            errors.append(f"invalid runtime allowlist path: {relative}")
            continue
        runtime_paths[relative] = relative_path
        parts = relative_path.parts
        if any(
            part.casefold() in FORBIDDEN_BUNDLE_PARTS
            or part.casefold().endswith(".egg-info")
            for part in parts
        ):
            errors.append(f"development-only path in runtime allowlist: {relative}")
    runtime_file_set = {path.as_posix() for path in runtime_paths.values()}
    for relative in required:
        relative_path = runtime_paths.get(relative)
        if relative_path is None:
            continue
        try:
            exists = (root / relative_path).is_file()
        except (OSError, ValueError):
            exists = False
        if not exists:
            errors.append(f"manifest required file is missing: {relative}")
    _validate_markdown_links(root, list(runtime_paths), errors)

    manifest_lenses_raw = manifest.get("supported_lenses")
    if not _is_string_list(manifest_lenses_raw) or not manifest_lenses_raw:
        errors.append("manifest supported_lenses must be a non-empty list of strings")
        manifest_lenses: set[str] = set()
    else:
        manifest_lenses = set(manifest_lenses_raw)
        if len(manifest_lenses) != len(manifest_lenses_raw):
            errors.append("manifest supported_lenses must not contain duplicates")
    if manifest_lenses != SUPPORTED_LENSES:
        errors.append("manifest supported lenses do not match the four canonical lenses")
    reference_lenses = {path.stem for path in (root / "references" / "thinkers").glob("*.md")}
    if reference_lenses != SUPPORTED_LENSES:
        errors.append("thinker reference files do not match the four canonical lenses")
    skill_text = (root / "SKILL.md").read_text(encoding="utf-8") if (root / "SKILL.md").is_file() else ""
    for lens in SUPPORTED_LENSES:
        if lens.replace("-", " ").lower() not in skill_text.lower() and lens.lower() not in skill_text.lower():
            errors.append(f"SKILL.md does not declare supported lens: {lens}")
    if isinstance(rules_data, dict) and isinstance(rules_data.get("rules"), list):
        yaml_lenses: set[str] = set()
        for rule in rules_data["rules"]:
            if isinstance(rule, dict):
                primary = rule.get("primary_lens")
                if isinstance(primary, str) and primary != "none":
                    yaml_lenses.add(primary)
                secondary = rule.get("secondary_lenses")
                if isinstance(secondary, list):
                    yaml_lenses.update(item for item in secondary if isinstance(item, str))
        unknown = yaml_lenses - SUPPORTED_LENSES
        if unknown:
            errors.append(f"trigger rules contain unsupported lenses: {', '.join(sorted(unknown))}")
        for rule in rules_data["rules"]:
            if not isinstance(rule, dict):
                continue
            source_refs = rule.get("source_refs")
            for source_ref in source_refs if _is_string_list(source_refs) else []:
                relative, _, _ = source_ref.partition("#")
                relative_path = Path(relative)
                if (
                    relative_path.is_absolute()
                    or ".." in relative_path.parts
                    or relative_path.as_posix() not in runtime_file_set
                ):
                    errors.append(
                        f"trigger rule {rule.get('id')} source is not contained in runtime bundle: {relative}"
                    )

    mandatory_skill_phrases = (
        "## Runtime contract", "## Trigger detection", "## Response workflow",
        "## Exit and completion rules", "## Safety", "## Output style",
        "## Failure prevention", "## Reference loading", "unsupported thinker",
        "does not call an external model api",
    )
    lower_skill = skill_text.lower()
    for phrase in mandatory_skill_phrases:
        if phrase.lower() not in lower_skill:
            errors.append(f"critical runtime rule missing from SKILL.md: {phrase}")

    for flag in ("network_required", "api_key_required", "backend_required"):
        if manifest.get(flag) is not False:
            errors.append(f"manifest {flag} must be false")
    runtime_docs = "\n".join(
        (root / path).read_text(encoding="utf-8")
        for path in ("SKILL.md", "docs/runtime_contract.md", "docs/installation.md")
        if (root / path).is_file()
    ).lower()
    no_api_key_claim = re.search(
        r"(?:no api key|without (?:an? )?api key|does not require[^.\n]{0,160}api key)",
        runtime_docs,
    )
    if no_api_key_claim is None:
        errors.append("runtime documentation is missing a no-API-key statement")
    if "does not call an external model api" not in runtime_docs:
        errors.append(
            "runtime documentation is missing no-API statement: "
            "does not call an external model api"
        )
    forbidden_config = re.compile(r"OPENAI_API_KEY|ANTHROPIC_API_KEY|DEEPSEEK_API_KEY|MODEL_ENDPOINT|requests\.post|httpx\.", re.I)
    for relative in runtime_files:
        path = root / relative
        if path.is_file() and forbidden_config.search(path.read_text(encoding="utf-8", errors="ignore")):
            errors.append(f"provider or API configuration found in runtime file: {relative}")

    try:
        project_version = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    except (OSError, KeyError, tomllib.TOMLDecodeError):
        project_version = None
        errors.append("cannot read project version from pyproject.toml")
    package_text = (root / "src/mingren_skill/__init__.py").read_text(encoding="utf-8")
    package_match = re.search(r'__version__\s*=\s*["\']([^"\']+)', package_text)
    version_values = [
        project_version,
        manifest.get("version"),
        package_match.group(1) if package_match else None,
    ]
    if any(not isinstance(value, str) or not value for value in version_values):
        errors.append(
            f"version values must be non-empty strings: "
            f"{sorted(str(item) for item in version_values)}"
        )
    elif set(version_values) != {"0.1.0"}:
        errors.append(
            f"version values are inconsistent: {sorted(set(version_values))}"
        )
    if not re.search(r"^## (?:v|\[)0\.1\.0", (root / "CHANGELOG.md").read_text(encoding="utf-8"), re.MULTILINE):
        errors.append("CHANGELOG.md does not contain version 0.1.0")

    host_data = _load_yaml(root / "evals/host_cases.yaml", errors)
    _validate_behavior_contract(root, rules_data, host_data, errors, runtime_file_set)

    try:
        builder_path = root / "scripts" / "build_skill_bundle.py"
        spec = importlib.util.spec_from_file_location("mingren_bundle_builder", builder_path)
        if spec is None or spec.loader is None:
            raise OSError(f"cannot load bundle builder: {builder_path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        build_skill_bundle = module.build_skill_bundle
        with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
            first = build_skill_bundle(root, Path(first_dir))
            second = build_skill_bundle(root, Path(second_dir))
            if hashlib.sha256(first.zip_path.read_bytes()).digest() != hashlib.sha256(second.zip_path.read_bytes()).digest():
                errors.append("generated runtime bundle is not reproducible")
    except (OSError, ValueError, yaml.YAMLError) as exc:
        errors.append(f"cannot reproduce runtime bundle: {exc}")


def validate_repository(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        path = root / relative
        if not path.is_file():
            errors.append(f"missing required file: {relative}")
        elif not path.read_text(encoding="utf-8").strip():
            errors.append(f"required file is empty: {relative}")

    for path in root.rglob("*.md"):
        if "lorem ipsum" in path.read_text(encoding="utf-8").lower():
            errors.append(f"placeholder filler found in {path.relative_to(root)}")

    for thinker in ("feynman", "socrates", "von-neumann", "laozi"):
        path = root / "references" / "thinkers" / f"{thinker}.md"
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        for heading in THINKER_HEADINGS:
            pattern = rf"^## {re.escape(heading)}\s*$\n(?=\s*\S)"
            if not re.search(pattern, content, re.MULTILINE):
                errors.append(f"missing or empty heading {heading!r} in {path.relative_to(root)}")
        for block in content.split("TODO-SOURCE:")[1:]:
            limited = block.split("\n## ", 1)[0].split("\n### ", 1)[0]
            for field in TODO_FIELDS:
                if not re.search(rf"^- {re.escape(field)}:\s*\S", limited, re.MULTILINE):
                    errors.append(f"incomplete TODO-SOURCE field {field!r} in {path.relative_to(root)}")

    rules_path = root / "references" / "trigger_rules.yaml"
    rules_data = _load_yaml(rules_path, errors)
    if rules_data is not None:
        if not isinstance(rules_data, dict) or not isinstance(rules_data.get("rules"), list):
            errors.append("trigger_rules.yaml must contain a top-level rules list")
        else:
            seen: set[str] = set()
            for index, rule in enumerate(rules_data["rules"]):
                if not isinstance(rule, dict):
                    errors.append(f"trigger rule {index} is not a mapping")
                    continue
                missing = RULE_FIELDS - rule.keys()
                if missing:
                    errors.append(f"trigger rule {index} missing fields: {', '.join(sorted(missing))}")
                for field in RULE_STRING_FIELDS:
                    value = rule.get(field)
                    if not isinstance(value, str) or not value.strip():
                        errors.append(
                            f"trigger rule {index} field {field} must be a non-empty string"
                        )
                for field in RULE_LIST_FIELDS:
                    value = rule.get(field)
                    if not _is_string_list(value) or (field != "secondary_lenses" and not value):
                        errors.append(
                            f"trigger rule {rule.get('id') or index} field {field} must be "
                            + ("a list of strings" if field == "secondary_lenses" else "a non-empty list of strings")
                        )
                rule_id = rule.get("id")
                if isinstance(rule_id, str) and rule_id in seen:
                    errors.append(f"duplicate trigger rule ID: {rule_id}")
                if isinstance(rule_id, str):
                    seen.add(rule_id)
                confidence = rule.get("confidence")
                if not isinstance(confidence, str) or confidence not in CONFIDENCE:
                    errors.append(f"trigger rule {rule_id or index} has invalid confidence")
                if (
                    not isinstance(rule.get("priority"), int)
                    or isinstance(rule.get("priority"), bool)
                    or rule["priority"] < 0
                ):
                    errors.append(
                        f"trigger rule {rule_id or index} priority must be a non-negative integer"
                    )
                primary_lens = rule.get("primary_lens")
                if not isinstance(primary_lens, str) or primary_lens not in CANONICAL_LENSES:
                    errors.append(
                        f"trigger rule {rule_id or index} has unsupported primary lens: {primary_lens}"
                    )
                secondary_lenses = rule.get("secondary_lenses")
                if _is_string_list(secondary_lenses):
                    unknown = set(secondary_lenses) - SUPPORTED_LENSES
                    if unknown:
                        errors.append(
                            f"trigger rule {rule_id or index} has unsupported secondary lenses: "
                            + ", ".join(sorted(unknown))
                        )
                    if len(secondary_lenses) != len(set(secondary_lenses)):
                        errors.append(
                            f"trigger rule {rule_id or index} has duplicate secondary lenses"
                        )
                    if primary_lens != "none" and primary_lens in secondary_lenses:
                        errors.append(
                            f"trigger rule {rule_id or index} repeats its primary lens as secondary"
                        )
                source_refs = rule.get("source_refs")
                for source_ref in source_refs if _is_string_list(source_refs) else []:
                    relative, _, anchor = source_ref.partition("#")
                    relative_path = Path(relative)
                    if relative_path.is_absolute() or ".." in relative_path.parts:
                        errors.append(
                            f"trigger rule {rule_id} source reference escapes repository: {relative}"
                        )
                        continue
                    relative_path = _validated_relative_path(relative)
                    if relative_path is None:
                        errors.append(
                            f"trigger rule {rule_id} source reference has invalid repository path: {relative!r}"
                        )
                        continue
                    source = root / relative_path
                    try:
                        resolved_source = source.resolve()
                    except (OSError, RuntimeError, ValueError):
                        errors.append(
                            f"trigger rule {rule_id} source reference has invalid repository path: {relative!r}"
                        )
                        continue
                    try:
                        resolved_source.relative_to(root)
                    except ValueError:
                        errors.append(
                            f"trigger rule {rule_id} source reference escapes repository: {relative}"
                        )
                        continue
                    if source.is_symlink() or not resolved_source.is_file():
                        errors.append(f"trigger rule {rule_id} references missing source: {relative}")
                    elif anchor:
                        anchors = {
                            _anchor(line.lstrip("#").strip())
                            for line in resolved_source.read_text(encoding="utf-8").splitlines()
                            if line.startswith("#")
                        }
                        if anchor not in anchors:
                            errors.append(f"trigger rule {rule_id} references missing anchor: {source_ref}")

    _validate_runtime(root, rules_data, errors)

    taxonomy = root / "evals" / "failure_taxonomy.md"
    if taxonomy.is_file():
        found = set(re.findall(r"^## (F\d{2})\b", taxonomy.read_text(encoding="utf-8"), re.MULTILINE))
        missing = FAILURE_IDS - found
        if missing:
            errors.append(f"failure taxonomy missing categories: {', '.join(sorted(missing))}")

    cases_data = _load_yaml(root / "evals" / "cases.yaml", errors)
    if cases_data is not None:
        if not isinstance(cases_data, dict) or not isinstance(cases_data.get("cases"), list):
            errors.append("cases.yaml must contain a top-level cases list")
        else:
            case_ids: set[str] = set()
            for index, case in enumerate(cases_data["cases"]):
                if not isinstance(case, dict):
                    errors.append(f"evaluation case {index} is not a mapping")
                    continue
                missing = CASE_FIELDS - case.keys()
                if missing:
                    errors.append(f"evaluation case {index} missing fields: {', '.join(sorted(missing))}")
                case_id = case.get("id")
                if not isinstance(case_id, str) or not case_id:
                    errors.append(f"evaluation case {index} has invalid ID")
                elif case_id in case_ids:
                    errors.append(f"duplicate evaluation case ID: {case_id}")
                else:
                    case_ids.add(case_id)

    snapshots = root / "evals" / "prompt_snapshots"
    if not snapshots.is_dir():
        errors.append("missing prompt snapshot directory: evals/prompt_snapshots")
    else:
        snapshot_paths = sorted(snapshots.glob("*.yaml"))
        if len(snapshot_paths) < 7:
            errors.append("prompt snapshot directory must contain at least 7 YAML snapshots")
        for path in snapshot_paths:
            data = _load_yaml(path, errors)
            if not isinstance(data, dict):
                errors.append(f"prompt snapshot is not a mapping: {path.relative_to(root)}")
                continue
            missing = SNAPSHOT_FIELDS - data.keys()
            if missing:
                errors.append(f"prompt snapshot {path.name} missing fields: {', '.join(sorted(missing))}")
            for field in SNAPSHOT_FIELDS:
                value = data.get(field)
                if value is None or value == "" or value == []:
                    if field != "selected_lenses":
                        errors.append(f"prompt snapshot {path.name} has empty field: {field}")

    models_path = root / "src" / "mingren_skill" / "models.py"
    output_modes = _extract_string_set(models_path, "ALLOWED_OUTPUT_MODES") if models_path.is_file() else None
    if output_modes != {"final_answer", "prompt_preview", "debug"}:
        errors.append("ALLOWED_OUTPUT_MODES must contain final_answer, prompt_preview, and debug")
    severities = _extract_string_set(models_path, "ALLOWED_ISSUE_SEVERITIES") if models_path.is_file() else None
    if severities != {"error", "warning", "info"}:
        errors.append("ALLOWED_ISSUE_SEVERITIES must contain error, warning, and info")

    readme = root / "README.md"
    if readme.is_file():
        readme_text = readme.read_text(encoding="utf-8")
        for command in ("mingren-skill plan", "mingren-skill prompt", "mingren-skill validate-response"):
            if command not in readme_text:
                errors.append(f"README.md does not document CLI command: {command}")
    traceability = root / "docs" / "requirements_traceability.md"
    if traceability.is_file():
        trace_text = traceability.read_text(encoding="utf-8").lower()
        for term in ("prompt_builder.py", "response_validator.py"):
            if term not in trace_text:
                errors.append(f"requirements traceability is missing prompt-layer term: {term}")
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    errors = validate_repository(args.root)
    if errors:
        print(f"Validation failed with {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Validation passed: repository structure, sources, rules, and cases are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
