from __future__ import annotations

import shutil
import importlib.util
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("repository_validator", ROOT / "scripts" / "validate.py")
assert SPEC is not None and SPEC.loader is not None
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)
validate_repository = VALIDATOR.validate_repository
validate_behavior_contract = VALIDATOR._validate_behavior_contract


def _behavior_data() -> tuple[dict[str, object], dict[str, object]]:
    rules = yaml.safe_load((ROOT / "references" / "trigger_rules.yaml").read_text(encoding="utf-8"))
    host_cases = yaml.safe_load((ROOT / "evals" / "host_cases.yaml").read_text(encoding="utf-8"))
    assert isinstance(rules, dict) and isinstance(host_cases, dict)
    return rules, host_cases


def _case(host_data: dict[str, object], case_id: str) -> dict[str, object]:
    cases = host_data["cases"]
    assert isinstance(cases, list)
    return next(case for case in cases if isinstance(case, dict) and case.get("id") == case_id)


def _behavior_errors(
    rules_data: dict[str, object], host_data: dict[str, object]
) -> list[str]:
    errors: list[str] = []
    validate_behavior_contract(ROOT, rules_data, host_data, errors)
    return errors


def _copy_repository(tmp_path: Path) -> Path:
    destination = tmp_path / "repository"
    shutil.copytree(
        ROOT,
        destination,
        ignore=shutil.ignore_patterns(".git", ".pytest_cache", "__pycache__", "dist"),
    )
    return destination


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


def test_behavior_contract_succeeds_on_repaired_data() -> None:
    rules, host_cases = _behavior_data()
    assert _behavior_errors(rules, host_cases) == []


def test_behavior_contract_rejects_generic_simplicity_routed_to_feynman() -> None:
    rules, host_cases = _behavior_data()
    contract = rules["behavior_contract"]
    assert isinstance(contract, dict)
    contract["generic_simplicity_rule"] = "explain-simply"
    errors = _behavior_errors(rules, host_cases)
    assert "trigger behavior_contract generic_simplicity_rule must route to none" in errors


def test_behavior_contract_rejects_generic_simplicity_case_with_lens() -> None:
    rules, host_cases = _behavior_data()
    _case(host_cases, "chinese_simple")["expected_primary_lens"] = "feynman"
    errors = _behavior_errors(rules, host_cases)
    assert "host case chinese_simple generic simplicity must expect no lens" in errors


def test_behavior_contract_rejects_quotation_only_case_with_lens() -> None:
    rules, host_cases = _behavior_data()
    _case(host_cases, "quotation_fabrication")["expected_primary_lens"] = "feynman"
    errors = _behavior_errors(rules, host_cases)
    assert "host case quotation_fabrication quotation-only request must expect no lens" in errors


def test_behavior_contract_rejects_conflicting_bilingual_equivalents() -> None:
    rules, host_cases = _behavior_data()
    _case(host_cases, "chinese_simple")["expected_primary_lens"] = "feynman"
    errors = _behavior_errors(rules, host_cases)
    assert any(
        "host equivalence group 'recursion-simple' has conflicting trigger expectations" in error
        for error in errors
    )


def test_behavior_contract_rejects_non_trigger_with_lens() -> None:
    rules, host_cases = _behavior_data()
    _case(host_cases, "biography_non_trigger")["expected_primary_lens"] = "von-neumann"
    errors = _behavior_errors(rules, host_cases)
    assert "host case biography_non_trigger non-trigger cannot require a thinker lens" in errors


def test_behavior_contract_rejects_explicit_lens_mismatch() -> None:
    rules, host_cases = _behavior_data()
    _case(host_cases, "explicit_feynman")["expected_primary_lens"] = "none"
    errors = _behavior_errors(rules, host_cases)
    assert "host case explicit_feynman explicit lens request must select feynman" in errors


def test_behavior_contract_rejects_unsupported_thinker_as_new_lens() -> None:
    rules, host_cases = _behavior_data()
    _case(host_cases, "unsupported_thinker")["expected_primary_lens"] = "einstein"
    errors = _behavior_errors(rules, host_cases)
    assert "host case unsupported_thinker has unsupported expected_primary_lens: einstein" in errors
    assert "host case unsupported_thinker unsupported thinker must use neutral primary fallback" in errors


def test_behavior_contract_rejects_invalid_list_field_type() -> None:
    rules, host_cases = _behavior_data()
    _case(host_cases, "unrelated_neutral")["allowed_secondary_lenses"] = "feynman"
    errors = _behavior_errors(rules, host_cases)
    assert (
        "host case unrelated_neutral field allowed_secondary_lenses must be a list of strings"
        in errors
    )


def test_behavior_contract_requires_executable_case_lists() -> None:
    rules, host_cases = _behavior_data()
    case = _case(host_cases, "unrelated_neutral")
    case["required_files"] = []
    case["required_behaviors"] = []
    case["forbidden_behaviors"] = []
    errors = _behavior_errors(rules, host_cases)
    for field in ("required_files", "required_behaviors", "forbidden_behaviors"):
        assert any(f"field {field} must be a non-empty list" in error for error in errors)


def test_behavior_contract_rejects_conflicting_required_and_forbidden_behavior() -> None:
    rules, host_cases = _behavior_data()
    case = _case(host_cases, "unrelated_neutral")
    case["required_behaviors"] = ["same behavior"]
    case["forbidden_behaviors"] = ["same behavior"]
    errors = _behavior_errors(rules, host_cases)
    assert any("requires and forbids the same behaviors" in error for error in errors)


def test_behavior_contract_validates_safety_and_language_enums() -> None:
    rules, host_cases = _behavior_data()
    case = _case(host_cases, "urgent_medical_override")
    case["safety_expectation"] = "normal"
    case["language_expectation"] = "english"
    errors = _behavior_errors(rules, host_cases)
    assert "host case urgent_medical_override has invalid language_expectation: english" in errors
    assert any("safety_override must use emergency_override safety" in error for error in errors)


def test_behavior_contract_handles_unhashable_equivalence_values() -> None:
    rules, host_cases = _behavior_data()
    case = _case(host_cases, "chinese_simple")
    case["expected_primary_lens"] = ["none"]
    case["safety_expectation"] = []
    case["language_expectation"] = {"language": "zh-CN"}
    errors = _behavior_errors(rules, host_cases)
    assert any("unsupported expected_primary_lens" in error for error in errors)
    assert any("invalid safety_expectation" in error for error in errors)
    assert any("invalid language_expectation" in error for error in errors)


def test_behavior_contract_handles_unhashable_trigger_class_and_distinctive_lens() -> None:
    rules, host_cases = _behavior_data()
    _case(host_cases, "unrelated_neutral")["trigger_class"] = []
    _case(host_cases, "english_direct")["expected_primary_lens"] = {"lens": "socrates"}
    errors = _behavior_errors(rules, host_cases)
    assert any("invalid trigger_class" in error for error in errors)
    assert any("distinctive method must select a supported lens" in error for error in errors)


def test_behavior_contract_rejects_required_file_escape() -> None:
    rules, host_cases = _behavior_data()
    _case(host_cases, "unrelated_neutral")["required_files"] = ["../outside.md"]
    errors = _behavior_errors(rules, host_cases)
    assert any("required file escapes repository" in error for error in errors)


def test_behavior_contract_requires_host_files_in_runtime_bundle() -> None:
    rules, host_cases = _behavior_data()
    _case(host_cases, "unrelated_neutral")["required_files"] = ["tests/test_router.py"]
    errors = _behavior_errors(rules, host_cases)
    assert any("required file is not in runtime bundle" in error for error in errors)


def test_repository_validator_matches_trigger_rule_schema(tmp_path: Path) -> None:
    repository = _copy_repository(tmp_path)
    rules_path = repository / "references" / "trigger_rules.yaml"
    rules = yaml.safe_load(rules_path.read_text(encoding="utf-8"))
    rules["rules"][0]["actions"] = []
    rules["rules"][0]["priority"] = -1
    rules["rules"][0]["source_refs"] = 42
    rules_path.write_text(yaml.safe_dump(rules, sort_keys=False), encoding="utf-8")

    errors = validate_repository(repository)

    assert any("actions must be a non-empty list of strings" in error for error in errors)
    assert any("priority must be a non-negative integer" in error for error in errors)
    assert any("source_refs must be a non-empty list of strings" in error for error in errors)


def test_repository_validator_rejects_external_trigger_source(tmp_path: Path) -> None:
    repository = _copy_repository(tmp_path)
    outside = tmp_path / "outside.md"
    outside.write_text("# Outside\n", encoding="utf-8")
    rules_path = repository / "references" / "trigger_rules.yaml"
    rules = yaml.safe_load(rules_path.read_text(encoding="utf-8"))
    rules["rules"][0]["source_refs"] = ["../outside.md"]
    rules_path.write_text(yaml.safe_dump(rules, sort_keys=False), encoding="utf-8")

    errors = validate_repository(repository)

    assert any("source reference escapes repository" in error for error in errors)
    assert any("source is not contained in runtime bundle" in error for error in errors)


def test_repository_validator_handles_malformed_manifest_lenses(tmp_path: Path) -> None:
    repository = _copy_repository(tmp_path)
    manifest_path = repository / "skill-manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest["supported_lenses"] = 42
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")

    errors = validate_repository(repository)

    assert "manifest supported_lenses must be a non-empty list of strings" in errors
    assert "manifest supported lenses do not match the four canonical lenses" in errors


def test_repository_validator_reports_control_character_paths_without_crashing(
    tmp_path: Path,
) -> None:
    repository = _copy_repository(tmp_path)

    manifest_path = repository / "skill-manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest["required_files"].append("\0")
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")

    host_path = repository / "evals" / "host_cases.yaml"
    host_cases = yaml.safe_load(host_path.read_text(encoding="utf-8"))
    _case(host_cases, "unrelated_neutral")["required_files"] = ["\0"]
    host_path.write_text(yaml.safe_dump(host_cases, sort_keys=False), encoding="utf-8")

    rules_path = repository / "references" / "trigger_rules.yaml"
    rules = yaml.safe_load(rules_path.read_text(encoding="utf-8"))
    rules["rules"][0]["source_refs"] = ["\0"]
    rules_path.write_text(yaml.safe_dump(rules, sort_keys=False), encoding="utf-8")

    errors = validate_repository(repository)

    assert any("invalid runtime allowlist path" in error for error in errors)
    assert any("required file has invalid repository path" in error for error in errors)
    assert any("source reference has invalid repository path" in error for error in errors)
