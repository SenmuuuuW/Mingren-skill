#!/usr/bin/env python3
"""Build a deterministic, allowlisted host-runtime bundle with no network access."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import yaml

MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
FORBIDDEN_PARTS = {
    ".git", ".venv", "venv", "__pycache__", ".pytest_cache", "tests",
    "scripts", "src", "build", "dist", ".env",
}


@dataclass(frozen=True, slots=True)
class BundleResult:
    bundle_dir: Path
    zip_path: Path
    checksum_manifest: Path
    files: tuple[str, ...]


def _load_manifest(root: Path) -> dict[str, object]:
    path = root / "skill-manifest.yaml"
    if not path.is_file():
        raise FileNotFoundError(f"runtime manifest does not exist: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("skill-manifest.yaml must contain a mapping")
    return data


def _approved_files(manifest: dict[str, object]) -> list[str]:
    values = ["skill-manifest.yaml"]
    for field in ("required_files", "optional_files"):
        entries = manifest.get(field)
        if not isinstance(entries, list) or any(not isinstance(item, str) for item in entries):
            raise ValueError(f"manifest field {field} must be a list of paths")
        values.extend(entries)
    unique = list(dict.fromkeys(values))
    for relative in unique:
        path = Path(relative)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError(f"runtime path must stay inside the repository: {relative}")
        if any(part in FORBIDDEN_PARTS or part.endswith(".egg-info") for part in path.parts):
            raise ValueError(f"development-only path is forbidden from runtime bundle: {relative}")
    return sorted(unique)


def _copy_allowlist(root: Path, bundle_dir: Path, files: list[str]) -> None:
    for relative in files:
        source = root / relative
        if not source.is_file():
            raise FileNotFoundError(f"runtime dependency is missing: {relative}")
        destination = bundle_dir / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)


def _verify_markdown_links(bundle_dir: Path) -> None:
    errors: list[str] = []
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
                resolved.relative_to(bundle_dir.resolve())
            except ValueError:
                errors.append(f"{path.relative_to(bundle_dir)} link escapes bundle: {target}")
                continue
            if not resolved.exists():
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
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def build_skill_bundle(root: Path | None = None, output_root: Path | None = None) -> BundleResult:
    root = (root or Path(__file__).resolve().parents[1]).resolve()
    output_root = (output_root or root / "dist").resolve()
    bundle_dir = output_root / "skill"
    zip_path = output_root / "mingren-skill.zip"

    if bundle_dir.exists():
        shutil.rmtree(bundle_dir)
    if zip_path.exists():
        zip_path.unlink()
    bundle_dir.mkdir(parents=True, exist_ok=True)

    manifest = _load_manifest(root)
    files = _approved_files(manifest)
    _copy_allowlist(root, bundle_dir, files)
    _verify_markdown_links(bundle_dir)
    checksum_manifest = _write_checksums(bundle_dir)
    _write_deterministic_zip(bundle_dir, zip_path)

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
