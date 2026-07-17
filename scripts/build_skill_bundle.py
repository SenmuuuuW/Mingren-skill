#!/usr/bin/env python3
"""Build a deterministic, allowlisted host-runtime bundle with no network access."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import tempfile
import unicodedata
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import yaml

MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
CHECKSUM_LINE_RE = re.compile(r"^([0-9a-f]{64})  (.+)$")
FORBIDDEN_PARTS = {
    ".git", ".venv", "venv", "__pycache__", ".pytest_cache", "tests",
    "scripts", "src", "build", "dist", ".env",
}
RESERVED_ROOT_PATHS = {"skill-manifest.yaml", "MANIFEST.sha256"}


@dataclass(frozen=True, slots=True)
class BundleResult:
    bundle_dir: Path
    zip_path: Path
    checksum_manifest: Path
    files: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ManifestFiles:
    entry_file: str
    required_files: tuple[str, ...]
    optional_files: tuple[str, ...]


def _normalise_runtime_path(value: object, field: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"manifest field {field} must contain only path strings")
    if (
        not value
        or not value.strip()
        or any(
            unicodedata.category(character) in {"Cc", "Cf", "Zl", "Zp"}
            for character in value
        )
    ):
        raise ValueError(f"manifest field {field} contains an empty or unsupported path")
    if "\\" in value or ":" in value:
        raise ValueError(
            f"manifest field {field} must use a portable relative POSIX path: {value}"
        )

    path = Path(value)
    if path.is_absolute():
        raise ValueError(f"runtime path must be relative to the repository: {value}")
    if ".." in path.parts:
        raise ValueError(f"runtime path must not contain parent traversal: {value}")
    if path == Path("."):
        raise ValueError(f"runtime path must name a file: {value}")
    if any(
        part.casefold() in FORBIDDEN_PARTS or part.casefold().endswith(".egg-info")
        for part in path.parts
    ):
        raise ValueError(f"development-only path is forbidden from runtime bundle: {value}")
    return path.as_posix()


def _portable_path_key(path: str) -> str:
    return unicodedata.normalize("NFC", path).casefold()


def _portable_absolute_parts(path: Path) -> tuple[str, ...]:
    return tuple(_portable_path_key(part) for part in path.parts)


def _is_portably_relative_to(path: Path, parent: Path) -> bool:
    path_parts = _portable_absolute_parts(path)
    parent_parts = _portable_absolute_parts(parent)
    return len(path_parts) >= len(parent_parts) and path_parts[:len(parent_parts)] == parent_parts


def _normalise_path_list(manifest: dict[str, object], field: str) -> tuple[str, ...]:
    entries = manifest.get(field)
    if not isinstance(entries, list):
        raise ValueError(f"manifest field {field} must be a list of path strings")
    paths = tuple(_normalise_runtime_path(item, field) for item in entries)
    seen: set[str] = set()
    duplicates: set[str] = set()
    for path in paths:
        key = _portable_path_key(path)
        if key in seen:
            duplicates.add(path)
        seen.add(key)
    if duplicates:
        raise ValueError(f"manifest field {field} contains duplicate paths: {', '.join(sorted(duplicates))}")
    return paths


def _manifest_files(manifest: dict[str, object]) -> ManifestFiles:
    entry_file = manifest.get("entry_file")
    if not isinstance(entry_file, str) or not entry_file:
        raise ValueError("manifest entry_file must be present and contain a path string")
    if entry_file != "SKILL.md":
        raise ValueError("manifest entry_file must be exactly SKILL.md")

    required = _normalise_path_list(manifest, "required_files")
    optional = _normalise_path_list(manifest, "optional_files")
    reserved_keys = {_portable_path_key(path) for path in RESERVED_ROOT_PATHS}
    for path in (*required, *optional):
        first_component = Path(path).parts[0]
        if _portable_path_key(first_component) in reserved_keys:
            raise ValueError(
                f"reserved bundle path must not be listed or used as a parent: {path}"
            )
    required_keys = {_portable_path_key(path): path for path in required}
    optional_keys = {_portable_path_key(path): path for path in optional}
    overlap_keys = set(required_keys) & set(optional_keys)
    if overlap_keys:
        overlap = {
            f"{required_keys[key]} / {optional_keys[key]}" for key in overlap_keys
        }
        raise ValueError(
            "manifest paths cannot be both required and optional: "
            + ", ".join(sorted(overlap))
        )
    if entry_file not in required:
        raise ValueError("manifest entry_file SKILL.md must be listed in required_files")
    return ManifestFiles(entry_file, required, optional)


def _resolve_source(root: Path, relative: str, *, required: bool) -> Path | None:
    relative_path = Path(relative)
    source = root / relative_path

    current = root
    for part in relative_path.parts:
        current /= part
        if current.is_symlink():
            raise ValueError(f"runtime path must not contain symlinks: {relative}")

    try:
        resolved = source.resolve(strict=False)
    except (OSError, RuntimeError) as exc:
        raise ValueError(f"cannot resolve runtime path {relative}: {exc}") from exc
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"runtime path resolves outside the repository: {relative}") from exc

    if not source.exists():
        if required:
            raise FileNotFoundError(f"required runtime file is missing: {relative}")
        return None
    if not source.is_file():
        raise ValueError(f"runtime path must be a regular file: {relative}")
    return resolved


def _load_manifest(root: Path) -> dict[str, object]:
    path = _resolve_source(root, "skill-manifest.yaml", required=True)
    assert path is not None
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("skill-manifest.yaml must contain a mapping")
    return data


def _approved_sources(
    root: Path, manifest: dict[str, object]
) -> tuple[ManifestFiles, dict[str, Path], set[str]]:
    files = _manifest_files(manifest)
    sources = {"skill-manifest.yaml": root / "skill-manifest.yaml"}
    for relative in files.required_files:
        source = _resolve_source(root, relative, required=True)
        assert source is not None
        sources[relative] = source

    skipped_optional: set[str] = set()
    for relative in files.optional_files:
        source = _resolve_source(root, relative, required=False)
        if source is None:
            skipped_optional.add(relative)
        else:
            sources[relative] = source

    if files.entry_file not in sources:
        raise ValueError(f"manifest entry_file is not included in the runtime bundle: {files.entry_file}")
    return files, sources, skipped_optional


def _copy_allowlist(bundle_dir: Path, sources: dict[str, Path]) -> None:
    for relative, source in sorted(sources.items()):
        destination = bundle_dir / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)


def _verify_markdown_links(bundle_dir: Path, skipped_optional: set[str]) -> None:
    errors: list[str] = []
    resolved_bundle_dir = bundle_dir.resolve()
    for path in sorted(bundle_dir.rglob("*.md")):
        content = path.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK_RE.findall(content):
            target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            file_target = target.split("#", 1)[0]
            if not file_target:
                continue
            resolved = (path.parent / file_target).resolve()
            try:
                bundle_relative = resolved.relative_to(resolved_bundle_dir).as_posix()
            except ValueError:
                errors.append(f"{path.relative_to(bundle_dir)} link escapes bundle: {target}")
                continue
            if not resolved.exists():
                if bundle_relative in skipped_optional:
                    continue
                errors.append(f"{path.relative_to(bundle_dir)} has unresolved link: {target}")
    if errors:
        raise ValueError("runtime link validation failed:\n- " + "\n- ".join(errors))


def _write_checksums(bundle_dir: Path) -> Path:
    lines = []
    for path in sorted(item for item in bundle_dir.rglob("*") if item.is_file()):
        relative = path.relative_to(bundle_dir).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {relative}")
    manifest = bundle_dir / "MANIFEST.sha256"
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest


def _write_deterministic_zip(bundle_dir: Path, zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(item for item in bundle_dir.rglob("*") if item.is_file()):
            relative = Path("mingren-skill") / path.relative_to(bundle_dir)
            info = zipfile.ZipInfo(relative.as_posix(), date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def _resolve_repository_root(root: Path) -> Path:
    try:
        resolved = root.resolve(strict=True)
    except (FileNotFoundError, OSError) as exc:
        raise ValueError(f"repository root does not exist: {root}") from exc
    if not resolved.is_dir():
        raise ValueError(f"repository root must be a directory: {resolved}")
    return resolved


def _resolve_output_root(root: Path, output_root: Path | None) -> Path:
    default_output_root = root / "dist"
    requested = output_root or default_output_root
    if requested.is_symlink():
        raise ValueError(f"output root must not be a symlink: {requested}")
    try:
        resolved = requested.resolve(strict=False)
        default_resolved = default_output_root.resolve(strict=False)
    except (OSError, RuntimeError) as exc:
        raise ValueError(f"cannot resolve output root {requested}: {exc}") from exc

    if _portable_absolute_parts(resolved) == _portable_absolute_parts(root) or _is_portably_relative_to(root, resolved):
        raise ValueError("output root must not be the repository root or one of its ancestors")
    if (
        _is_portably_relative_to(resolved, root)
        and _portable_absolute_parts(resolved) != _portable_absolute_parts(default_resolved)
    ):
        raise ValueError("custom output root must not be inside the repository; use the default root/dist")
    if resolved.exists() and not resolved.is_dir():
        raise ValueError(f"output root must be a directory: {resolved}")
    return resolved


def _existing_bundle_is_recognised(bundle_dir: Path) -> bool:
    checksum_manifest = bundle_dir / "MANIFEST.sha256"
    if (
        not bundle_dir.is_dir()
        or bundle_dir.is_symlink()
        or not checksum_manifest.is_file()
        or checksum_manifest.is_symlink()
    ):
        return False

    expected: dict[str, str] = {}
    try:
        lines = checksum_manifest.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return False
    for line in lines:
        match = CHECKSUM_LINE_RE.fullmatch(line)
        if match is None:
            return False
        digest, raw_relative = match.groups()
        try:
            relative = _normalise_runtime_path(raw_relative, "MANIFEST.sha256")
        except ValueError:
            return False
        if relative in expected or relative == "MANIFEST.sha256":
            return False
        expected[relative] = digest

    if not {"SKILL.md", "skill-manifest.yaml"}.issubset(expected):
        return False
    actual: dict[str, Path] = {}
    for path in bundle_dir.rglob("*"):
        if path.is_symlink():
            return False
        if path.is_file() and path != checksum_manifest:
            actual[path.relative_to(bundle_dir).as_posix()] = path
    if set(actual) != set(expected):
        return False
    return all(
        hashlib.sha256(actual[relative].read_bytes()).hexdigest() == digest
        for relative, digest in expected.items()
    )


def _existing_zip_matches_bundle(bundle_dir: Path, zip_path: Path) -> bool:
    expected = {
        f"mingren-skill/{path.relative_to(bundle_dir).as_posix()}": path
        for path in bundle_dir.rglob("*")
        if path.is_file()
    }
    try:
        with zipfile.ZipFile(zip_path) as archive:
            entries = archive.infolist()
            names = [entry.filename for entry in entries]
            if (
                len(names) != len(set(names))
                or set(names) != set(expected)
                or any(entry.is_dir() for entry in entries)
            ):
                return False
            for entry in entries:
                source = expected[entry.filename]
                if entry.file_size != source.stat().st_size:
                    return False
                if archive.read(entry) != source.read_bytes():
                    return False
    except (OSError, KeyError, RuntimeError, zipfile.BadZipFile, zipfile.LargeZipFile):
        return False
    return True


def _validate_output_targets(bundle_dir: Path, zip_path: Path) -> bool:
    if bundle_dir.is_symlink() or zip_path.is_symlink():
        raise ValueError("output bundle targets must not be symlinks")
    recognised = _existing_bundle_is_recognised(bundle_dir)
    if bundle_dir.exists() and not recognised:
        raise ValueError(f"refusing to replace unrecognised output directory: {bundle_dir}")
    if zip_path.exists():
        if not zip_path.is_file():
            raise ValueError(f"output ZIP path must be a regular file: {zip_path}")
        if not recognised or not _existing_zip_matches_bundle(bundle_dir, zip_path):
            raise ValueError(f"refusing to replace unrecognised output file: {zip_path}")
    return recognised


def _replace_output_targets(
    staged_bundle_dir: Path,
    staged_zip_path: Path,
    bundle_dir: Path,
    zip_path: Path,
    replace_existing: bool,
) -> None:
    if replace_existing:
        shutil.rmtree(bundle_dir)
        if zip_path.exists():
            zip_path.unlink()
    shutil.move(str(staged_bundle_dir), bundle_dir)
    shutil.move(str(staged_zip_path), zip_path)


def build_skill_bundle(root: Path | None = None, output_root: Path | None = None) -> BundleResult:
    root = _resolve_repository_root(root or Path(__file__).resolve().parents[1])
    output_root = _resolve_output_root(root, output_root)
    bundle_dir = output_root / "skill"
    zip_path = output_root / "mingren-skill.zip"

    manifest = _load_manifest(root)
    _, sources, skipped_optional = _approved_sources(root, manifest)
    output_root.mkdir(parents=True, exist_ok=True)
    replace_existing = _validate_output_targets(bundle_dir, zip_path)

    with tempfile.TemporaryDirectory(prefix=".mingren-skill-build-", dir=output_root) as staging:
        staging_root = Path(staging)
        staged_bundle_dir = staging_root / "skill"
        staged_zip_path = staging_root / "mingren-skill.zip"
        staged_bundle_dir.mkdir()
        _copy_allowlist(staged_bundle_dir, sources)
        _verify_markdown_links(staged_bundle_dir, skipped_optional)
        _write_checksums(staged_bundle_dir)
        _write_deterministic_zip(staged_bundle_dir, staged_zip_path)
        _replace_output_targets(
            staged_bundle_dir,
            staged_zip_path,
            bundle_dir,
            zip_path,
            replace_existing,
        )

    checksum_manifest = bundle_dir / "MANIFEST.sha256"

    bundled_files = tuple(
        path.relative_to(bundle_dir).as_posix()
        for path in sorted(item for item in bundle_dir.rglob("*") if item.is_file())
    )
    return BundleResult(bundle_dir, zip_path, checksum_manifest, bundled_files)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-root", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = build_skill_bundle(args.root, args.output_root)
    print(json.dumps({
        "bundle_dir": str(result.bundle_dir),
        "zip_path": str(result.zip_path),
        "checksum_manifest": str(result.checksum_manifest),
        "file_count": len(result.files),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
