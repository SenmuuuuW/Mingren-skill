"""Command-line interface for structured plan generation."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from typing import Sequence

from mingren_skill.engine import MingrenSkillEngine
from mingren_skill.language import detect_language
from mingren_skill.models import PromptContext
from mingren_skill.prompt_builder import PromptBuilder
from mingren_skill.response_validator import ResponseValidator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Plan, preview prompts, or validate Mingren Skill responses.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan_parser = subparsers.add_parser("plan", help="Print the structured EngineResult JSON.")
    plan_parser.add_argument("input", help="User request to route")

    prompt_parser = subparsers.add_parser("prompt", help="Print a provider-independent PromptPackage JSON.")
    prompt_parser.add_argument("input", help="User request to route and package")
    prompt_parser.add_argument("--context", dest="conversation_context", help="Optional prior conversation context")
    prompt_parser.add_argument("--subject", help="Optional explicit subject label")

    validate_parser = subparsers.add_parser("validate-response", help="Validate a proposed learner-facing response.")
    validate_parser.add_argument("input", help="Original user request")
    validate_parser.add_argument("--response", required=True, help="Proposed response text")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = list(argv) if argv is not None else sys.argv[1:]
    commands = {"plan", "prompt", "validate-response", "-h", "--help"}
    if arguments and arguments[0] not in commands:
        arguments.insert(0, "plan")
    args = build_parser().parse_args(arguments)

    result = MingrenSkillEngine().plan(args.input)
    if args.command == "plan":
        output = result
    else:
        context = PromptContext(
            user_input=args.input,
            language=detect_language(args.input),
            engine_result=result,
            conversation_context=getattr(args, "conversation_context", None),
            subject=getattr(args, "subject", None),
            output_mode="prompt_preview" if args.command == "prompt" else "final_answer",
        )
        if args.command == "prompt":
            output = PromptBuilder().build(context)
        else:
            output = ResponseValidator().validate(context, args.response)
    print(json.dumps(asdict(output), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
