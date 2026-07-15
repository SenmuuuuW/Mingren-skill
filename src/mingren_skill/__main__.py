"""Command-line interface for structured plan generation."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from typing import Sequence

from mingren_skill.engine import MingrenSkillEngine


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a structured thinker-lens plan.")
    parser.add_argument("input", help="User request to route")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = MingrenSkillEngine().plan(args.input)
    print(json.dumps(asdict(result), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
