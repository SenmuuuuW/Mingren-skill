from __future__ import annotations

import hashlib
import importlib.util
import shutil
import sys
import zipfile
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("bundle_builder", ROOT / "scripts" / "build_skill_bundle.py")
assert SPEC is not None and SPEC.loader is not None
BUNDLE_BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUNDLE_BUILDER
SPEC.loader.exec_module(BUNDLE_BUILDER)
build_skill_bundle = BUNDLE_BUILDER.build_skill_bundle


def test_manifest_declares_offline_runtime_and_consistent_version() -> None:
    manifest = yaml.safe_load((ROOT / "skill-manifest.yaml").read_text(encoding="utf-8"))
    assert manifest["version"] == "0.1.0"
    assert manifest["supported_lenses"] == ["feynman", "socrates", "von-neumann", "laozi"]
    assert manifest["network_required"] is False
    assert manifest["api_key_required"] is False
    assert manifest["backend_required"] is False


def test_bundle_is_allowlisted_and_reproducible(tmp_path: Path) -> None:
    first = build_skill_bundle(ROOT, tmp_path / "first")
    second = build_skill_bundle(ROOT, tmp_path / "second")
    assert hashlib.sha256(first.zip_path.read_bytes()).digest() == hashlib.sha256(second.zip_path.read_bytes()).digest()
    forbidden = {"src", "tests", "scripts", ".git", ".venv", "__pycache__"}
    assert all(not (forbidden & set(Path(name).parts)) for name in first.files)
    assert "SKILL.md" in first.files
    assert "MANIFEST.sha256" in first.files
    with zipfile.ZipFile(first.zip_path) as archive:
        names = archive.namelist()
    assert "mingren-skill/SKILL.md" in names
    assert all("__pycache__" not in name for name in names)


def test_checksum_manifest_matches_bundle_files(tmp_path: Path) -> None:
    result = build_skill_bundle(ROOT, tmp_path / "output")
    for line in result.checksum_manifest.read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        assert hashlib.sha256((result.bundle_dir / relative).read_bytes()).hexdigest() == digest


def test_missing_runtime_dependency_is_rejected(tmp_path: Path) -> None:
    root = tmp_path / "source"
    root.mkdir()
    shutil.copyfile(ROOT / "skill-manifest.yaml", root / "skill-manifest.yaml")
    with pytest.raises(FileNotFoundError, match="runtime dependency is missing"):
        build_skill_bundle(root, tmp_path / "output")
