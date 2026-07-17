from __future__ import annotations

import hashlib
import importlib.util
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
MISSING = object()


def _write_manifest(
    root: Path,
    *,
    entry_file: object = "SKILL.md",
    required_files: object = None,
    optional_files: object = None,
) -> None:
    manifest: dict[str, object] = {
        "required_files": ["SKILL.md"] if required_files is None else required_files,
        "optional_files": [] if optional_files is None else optional_files,
    }
    if entry_file is not MISSING:
        manifest["entry_file"] = entry_file
    (root / "skill-manifest.yaml").write_text(
        yaml.safe_dump(manifest, sort_keys=False),
        encoding="utf-8",
    )


def _make_source(tmp_path: Path, skill_text: str = "# Test Skill\n") -> Path:
    root = tmp_path / "source"
    root.mkdir()
    (root / "SKILL.md").write_text(skill_text, encoding="utf-8")
    _write_manifest(root)
    return root


def test_manifest_declares_offline_runtime_and_consistent_version() -> None:
    manifest = yaml.safe_load((ROOT / "skill-manifest.yaml").read_text(encoding="utf-8"))
    assert manifest["version"] == "0.1.0"
    assert manifest["entry_file"] == "SKILL.md"
    assert "LICENSE" in manifest["required_files"]
    assert "LICENSE" not in manifest["optional_files"]
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
        metadata = archive.getinfo("mingren-skill/SKILL.md")
    assert "mingren-skill/SKILL.md" in names
    assert all("__pycache__" not in name for name in names)
    assert metadata.date_time == (1980, 1, 1, 0, 0, 0)
    assert metadata.create_system == 3
    assert (metadata.external_attr >> 16) & 0o777 == 0o644


def test_checksum_manifest_matches_bundle_files(tmp_path: Path) -> None:
    result = build_skill_bundle(ROOT, tmp_path / "output")
    for line in result.checksum_manifest.read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        assert hashlib.sha256((result.bundle_dir / relative).read_bytes()).hexdigest() == digest


def test_normal_allowlisted_files_are_bundled(tmp_path: Path) -> None:
    root = _make_source(tmp_path)
    reference = root / "references" / "note.md"
    reference.parent.mkdir()
    reference.write_text("# Note\n", encoding="utf-8")
    _write_manifest(root, required_files=["SKILL.md", "references/note.md"])

    result = build_skill_bundle(root, tmp_path / "output")

    assert "SKILL.md" in result.files
    assert "references/note.md" in result.files
    assert "skill-manifest.yaml" in result.files


def test_parent_traversal_is_rejected(tmp_path: Path) -> None:
    root = _make_source(tmp_path)
    (tmp_path / "outside.md").write_text("outside\n", encoding="utf-8")
    _write_manifest(root, required_files=["SKILL.md", "../outside.md"])

    with pytest.raises(ValueError, match="parent traversal"):
        build_skill_bundle(root, tmp_path / "output")


def test_absolute_source_path_is_rejected(tmp_path: Path) -> None:
    root = _make_source(tmp_path)
    outside = tmp_path / "outside.md"
    outside.write_text("outside\n", encoding="utf-8")
    _write_manifest(root, required_files=["SKILL.md", str(outside)])

    with pytest.raises(ValueError, match="relative to the repository"):
        build_skill_bundle(root, tmp_path / "output")


def test_external_symlink_is_rejected(tmp_path: Path) -> None:
    root = _make_source(tmp_path)
    outside = tmp_path / "outside.md"
    outside.write_text("outside\n", encoding="utf-8")
    (root / "linked.md").symlink_to(outside)
    _write_manifest(root, required_files=["SKILL.md", "linked.md"])

    with pytest.raises(ValueError, match="must not contain symlinks"):
        build_skill_bundle(root, tmp_path / "output")


def test_missing_required_file_is_rejected(tmp_path: Path) -> None:
    root = _make_source(tmp_path)
    _write_manifest(root, required_files=["SKILL.md", "missing.md"])

    with pytest.raises(FileNotFoundError, match="required runtime file is missing: missing.md"):
        build_skill_bundle(root, tmp_path / "output")


def test_missing_required_license_is_rejected(tmp_path: Path) -> None:
    root = _make_source(tmp_path)
    _write_manifest(root, required_files=["SKILL.md", "LICENSE"])

    with pytest.raises(FileNotFoundError, match="required runtime file is missing: LICENSE"):
        build_skill_bundle(root, tmp_path / "output")


def test_directory_in_file_allowlist_is_rejected(tmp_path: Path) -> None:
    root = _make_source(tmp_path)
    (root / "references").mkdir()
    _write_manifest(root, required_files=["SKILL.md", "references"])

    with pytest.raises(ValueError, match="must be a regular file: references"):
        build_skill_bundle(root, tmp_path / "output")


def test_missing_optional_file_and_its_link_are_skipped(tmp_path: Path) -> None:
    root = _make_source(tmp_path, "# Test Skill\n\n[Optional note](notes/optional.md)\n")
    _write_manifest(root, optional_files=["notes/optional.md"])

    result = build_skill_bundle(root, tmp_path / "output")

    assert "notes/optional.md" not in result.files
    assert "SKILL.md" in result.files


def test_undeclared_missing_markdown_link_is_rejected(tmp_path: Path) -> None:
    root = _make_source(tmp_path, "# Test Skill\n\n[Missing note](notes/missing.md)\n")

    with pytest.raises(ValueError, match="unresolved link"):
        build_skill_bundle(root, tmp_path / "output")


@pytest.mark.parametrize("entry_file", [MISSING, None, 42])
def test_entry_file_must_be_declared_as_a_path(tmp_path: Path, entry_file: object) -> None:
    root = _make_source(tmp_path)
    _write_manifest(root, entry_file=entry_file)

    with pytest.raises(ValueError, match="entry_file must be present"):
        build_skill_bundle(root, tmp_path / "output")


@pytest.mark.parametrize("entry_file", ["README.md", "./SKILL.md", "references/SKILL.md"])
def test_entry_file_must_be_exactly_skill_md(tmp_path: Path, entry_file: str) -> None:
    root = _make_source(tmp_path)
    _write_manifest(root, entry_file=entry_file)

    with pytest.raises(ValueError, match="entry_file must be exactly SKILL.md"):
        build_skill_bundle(root, tmp_path / "output")


def test_entry_file_must_be_in_required_files(tmp_path: Path) -> None:
    root = _make_source(tmp_path)
    (root / "other.md").write_text("# Other\n", encoding="utf-8")
    _write_manifest(root, required_files=["other.md"], optional_files=["SKILL.md"])

    with pytest.raises(ValueError, match="entry_file SKILL.md must be listed in required_files"):
        build_skill_bundle(root, tmp_path / "output")


def test_missing_entry_file_is_rejected(tmp_path: Path) -> None:
    root = _make_source(tmp_path)
    (root / "SKILL.md").unlink()

    with pytest.raises(FileNotFoundError, match="required runtime file is missing: SKILL.md"):
        build_skill_bundle(root, tmp_path / "output")


def test_entry_file_must_be_a_regular_file(tmp_path: Path) -> None:
    root = _make_source(tmp_path)
    (root / "SKILL.md").unlink()
    (root / "SKILL.md").mkdir()

    with pytest.raises(ValueError, match="must be a regular file: SKILL.md"):
        build_skill_bundle(root, tmp_path / "output")


@pytest.mark.parametrize(
    ("required_files", "optional_files", "message"),
    [
        (["SKILL.md", "SKILL.md"], [], "required_files contains duplicate paths"),
        (["SKILL.md", "skill.MD"], [], "required_files contains duplicate paths"),
        (["SKILL.md"], ["note.md", "./note.md"], "optional_files contains duplicate paths"),
        (["SKILL.md", "note.md"], ["note.md"], "both required and optional"),
        (["SKILL.md"], ["skill.MD"], "both required and optional"),
    ],
)
def test_duplicate_and_overlapping_paths_are_rejected(
    tmp_path: Path,
    required_files: list[str],
    optional_files: list[str],
    message: str,
) -> None:
    root = _make_source(tmp_path)
    _write_manifest(root, required_files=required_files, optional_files=optional_files)

    with pytest.raises(ValueError, match=message):
        build_skill_bundle(root, tmp_path / "output")


@pytest.mark.parametrize("field", ["required_files", "optional_files"])
@pytest.mark.parametrize(
    "reserved_path",
    [
        "skill-manifest.yaml",
        "SKILL-MANIFEST.YAML",
        "skill-manifest.yaml/nested.md",
        "SKILL-MANIFEST.YAML/nested.md",
        "MANIFEST.sha256",
        "manifest.SHA256",
        "MANIFEST.sha256/nested.md",
        "manifest.SHA256/nested.md",
    ],
)
def test_reserved_bundle_paths_and_descendants_are_rejected(
    tmp_path: Path, field: str, reserved_path: str
) -> None:
    root = _make_source(tmp_path)
    values = ["SKILL.md", reserved_path] if field == "required_files" else [reserved_path]
    kwargs = {field: values}
    _write_manifest(root, **kwargs)

    with pytest.raises(ValueError, match="reserved bundle path"):
        build_skill_bundle(root, tmp_path / "output")


@pytest.mark.parametrize(
    "allowed_path",
    [
        "metadata/skill-manifest.yaml",
        "metadata/MANIFEST.sha256",
        "skill-manifest.yaml.backup",
        "MANIFEST.sha256.backup",
    ],
)
def test_non_reserved_path_boundaries_remain_allowed(
    tmp_path: Path, allowed_path: str
) -> None:
    root = _make_source(tmp_path)
    target = root / allowed_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("allowed\n", encoding="utf-8")
    _write_manifest(root, required_files=["SKILL.md", allowed_path])

    result = build_skill_bundle(root, tmp_path / "output")

    assert allowed_path in result.files


@pytest.mark.parametrize(
    "invalid_path",
    [
        42,
        {"path": "note.md"},
        "",
        ".",
        "notes/bad\nentry.md",
        "notes/bad\u0085entry.md",
        "notes/bad\u2028entry.md",
        "notes/bad\u2029entry.md",
        "..\\outside.md",
        "C:/outside.md",
    ],
)
def test_unsupported_manifest_path_types_are_rejected(tmp_path: Path, invalid_path: object) -> None:
    root = _make_source(tmp_path)
    _write_manifest(root, required_files=["SKILL.md", invalid_path])

    with pytest.raises(ValueError, match="path strings|unsupported path|must name a file|POSIX path"):
        build_skill_bundle(root, tmp_path / "output")


@pytest.mark.parametrize("forbidden_path", [".GIT/secret", "TESTS/case.yaml", "SRC/code.py"])
def test_mixed_case_development_paths_are_rejected(
    tmp_path: Path, forbidden_path: str
) -> None:
    root = _make_source(tmp_path)
    target = root / forbidden_path
    target.parent.mkdir(parents=True)
    target.write_text("secret\n", encoding="utf-8")
    _write_manifest(root, required_files=["SKILL.md", forbidden_path])

    with pytest.raises(ValueError, match="development-only path"):
        build_skill_bundle(root, tmp_path / "output")


def test_output_root_cannot_overlap_repository(tmp_path: Path) -> None:
    root = _make_source(tmp_path)

    for unsafe_output in (root, tmp_path, root / "custom-output"):
        with pytest.raises(ValueError, match="output root|custom output root"):
            build_skill_bundle(root, unsafe_output)


def test_case_alias_output_root_cannot_bypass_repository_containment(tmp_path: Path) -> None:
    root = _make_source(tmp_path)

    for unsafe_output in (Path(str(root).upper()), Path(str(tmp_path).upper())):
        with pytest.raises(ValueError, match="output root"):
            build_skill_bundle(root, unsafe_output)


def test_default_dist_output_inside_repository_is_allowed(tmp_path: Path) -> None:
    root = _make_source(tmp_path)

    result = build_skill_bundle(root)

    assert result.bundle_dir == root / "dist" / "skill"
    assert result.zip_path == root / "dist" / "mingren-skill.zip"


def test_recognised_bundle_output_can_be_rebuilt(tmp_path: Path) -> None:
    root = _make_source(tmp_path)
    output = tmp_path / "output"
    first = build_skill_bundle(root, output)
    first_digest = hashlib.sha256(first.zip_path.read_bytes()).digest()

    second = build_skill_bundle(root, output)

    assert hashlib.sha256(second.zip_path.read_bytes()).digest() == first_digest
    assert second.checksum_manifest.is_file()


def test_unrecognised_output_directory_is_not_deleted(tmp_path: Path) -> None:
    root = _make_source(tmp_path)
    output = tmp_path / "output"
    existing = output / "skill"
    existing.mkdir(parents=True)
    marker = existing / "keep.txt"
    marker.write_text("keep\n", encoding="utf-8")

    with pytest.raises(ValueError, match="refusing to replace unrecognised output directory"):
        build_skill_bundle(root, output)

    assert marker.read_text(encoding="utf-8") == "keep\n"


def test_bogus_checksum_marker_does_not_authorize_output_deletion(tmp_path: Path) -> None:
    root = _make_source(tmp_path)
    output = tmp_path / "output"
    existing = output / "skill"
    existing.mkdir(parents=True)
    marker = existing / "keep.txt"
    marker.write_text("keep\n", encoding="utf-8")
    (existing / "MANIFEST.sha256").write_text(
        f"{'0' * 64}  keep.txt\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="refusing to replace unrecognised output directory"):
        build_skill_bundle(root, output)

    assert marker.read_text(encoding="utf-8") == "keep\n"


def test_unrelated_existing_zip_is_not_deleted_with_a_recognised_bundle(
    tmp_path: Path,
) -> None:
    root = _make_source(tmp_path)
    output = tmp_path / "output"
    result = build_skill_bundle(root, output)
    unrelated = b"not a generated Mingren ZIP\n"
    result.zip_path.write_bytes(unrelated)

    with pytest.raises(ValueError, match="refusing to replace unrecognised output file"):
        build_skill_bundle(root, output)

    assert result.zip_path.read_bytes() == unrelated
    assert result.checksum_manifest.is_file()
