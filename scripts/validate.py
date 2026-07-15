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
    "safety_expectation", "language_expectation", "notes",
}
SUPPORTED_LENSES = {"feynman", "socrates", "von-neumann", "laozi"}
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
    for relative in required:
        if not (root / relative).is_file():
            errors.append(f"manifest required file is missing: {relative}")
    for relative in runtime_files:
        parts = Path(relative).parts
        if Path(relative).is_absolute() or ".." in parts:
            errors.append(f"invalid runtime allowlist path: {relative}")
        if any(part in FORBIDDEN_BUNDLE_PARTS or part.endswith(".egg-info") for part in parts):
            errors.append(f"development-only path in runtime allowlist: {relative}")
    _validate_markdown_links(root, runtime_files, errors)

    manifest_lenses = set(manifest.get("supported_lenses", []))
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
                yaml_lenses.update(item for item in rule.get("secondary_lenses", []) if isinstance(item, str))
        unknown = yaml_lenses - SUPPORTED_LENSES
        if unknown:
            errors.append(f"trigger rules contain unsupported lenses: {', '.join(sorted(unknown))}")

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
    for phrase in ("no api key", "does not call an external model api"):
        if phrase not in runtime_docs:
            errors.append(f"runtime documentation is missing no-API statement: {phrase}")
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
    skill_match = re.search(r"^version:\s*([^\s]+)", skill_text, re.MULTILINE)
    versions = {project_version, manifest.get("version"), package_match.group(1) if package_match else None, skill_match.group(1) if skill_match else None}
    if versions != {"0.1.0"}:
        errors.append(f"version values are inconsistent: {sorted(str(item) for item in versions)}")
    if not re.search(r"^## (?:v|\[)0\.1\.0", (root / "CHANGELOG.md").read_text(encoding="utf-8"), re.MULTILINE):
        errors.append("CHANGELOG.md does not contain version 0.1.0")

    host_data = _load_yaml(root / "evals/host_cases.yaml", errors)
    if not isinstance(host_data, dict) or not isinstance(host_data.get("cases"), list):
        errors.append("host_cases.yaml must contain a top-level cases list")
    else:
        host_cases = host_data["cases"]
        if len(host_cases) < 15:
            errors.append("host_cases.yaml must contain at least 15 cases")
        seen: set[str] = set()
        for index, case in enumerate(host_cases):
            if not isinstance(case, dict):
                errors.append(f"host case {index} is not a mapping")
                continue
            missing = HOST_CASE_FIELDS - case.keys()
            if missing:
                errors.append(f"host case {index} missing fields: {', '.join(sorted(missing))}")
            case_id = case.get("id")
            if not isinstance(case_id, str) or not case_id:
                errors.append(f"host case {index} has invalid ID")
            elif case_id in seen:
                errors.append(f"duplicate host case ID: {case_id}")
            else:
                seen.add(case_id)
            for relative in case.get("required_files", []):
                if not isinstance(relative, str) or not (root / relative).is_file():
                    errors.append(f"host case {case_id or index} references missing file: {relative}")

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
                rule_id = rule.get("id")
                if rule_id in seen:
                    errors.append(f"duplicate trigger rule ID: {rule_id}")
                if isinstance(rule_id, str):
                    seen.add(rule_id)
                if rule.get("confidence") not in CONFIDENCE:
                    errors.append(f"trigger rule {rule_id or index} has invalid confidence")
                for source_ref in rule.get("source_refs", []):
                    relative, _, anchor = source_ref.partition("#")
                    source = root / relative
                    if not source.is_file():
                        errors.append(f"trigger rule {rule_id} references missing source: {relative}")
                    elif anchor:
                        anchors = {
                            _anchor(line.lstrip("#").strip())
                            for line in source.read_text(encoding="utf-8").splitlines()
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
                if case_id in case_ids:
                    errors.append(f"duplicate evaluation case ID: {case_id}")
                if isinstance(case_id, str):
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
        for term in ("promptpackage", "response validation"):
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
