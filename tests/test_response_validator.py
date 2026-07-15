from __future__ import annotations

from mingren_skill.engine import MingrenSkillEngine
from mingren_skill.language import detect_language
from mingren_skill.models import PromptContext
from mingren_skill.response_validator import ResponseValidator


def context(input_text: str) -> PromptContext:
    return PromptContext(
        user_input=input_text,
        language=detect_language(input_text),
        engine_result=MingrenSkillEngine().plan(input_text),
    )


def codes(input_text: str, response: str) -> set[str]:
    result = ResponseValidator().validate(context(input_text), response)
    return {issue.code for issue in result.issues}


def test_empty_response_is_rejected() -> None:
    result = ResponseValidator().validate(context("Explain recursion"), "  ")
    assert result.valid is False
    assert "empty_response" in {issue.code for issue in result.issues}


def test_impersonation_is_rejected() -> None:
    assert "thinker_impersonation" in codes(
        "Feynman, explain recursion", "I am Feynman. Recursion is a function calling itself."
    )


def test_excessive_questioning_and_questions_only_are_detected() -> None:
    found = codes("What does intelligence mean here?", "What is intelligence? Is it memory? Is it reasoning? Why?")
    assert "excessive_questioning" in found
    assert "questions_only" in found


def test_unsafe_non_intervention_and_missing_warning_are_rejected() -> None:
    result = ResponseValidator().validate(
        context("我胸口剧痛而且无法呼吸"), "顺其自然，先观察一下。"
    )
    found = {issue.code for issue in result.issues}
    assert result.valid is False
    assert "unsafe_non_intervention" in found
    assert "missing_required_safety_warning" in found


def test_required_safety_warning_can_pass_structural_validation() -> None:
    result = ResponseValidator().validate(
        context("我胸口剧痛而且无法呼吸"),
        "这可能是紧急情况，请立即呼叫 120 或当地急救服务，不要等待；我不能提供诊断。",
    )
    assert result.valid is True


def test_wrong_language_and_internal_leakage_are_detected() -> None:
    found = codes("用中文解释递归", "The debug_metadata says to explain recursion directly.")
    assert "wrong_output_language" in found
    assert "internal_prompt_leakage" in found


def test_suspicious_quote_and_name_overuse_are_detected() -> None:
    found = codes(
        "Feynman, explain recursion",
        'Feynman said: “Recursion is magic.” Feynman explains it, and Feynman knows it; Feynman is clear.',
    )
    assert "suspicious_thinker_quote" in found
    assert "thinker_name_overuse" in found


def test_vague_laozi_filler_without_mechanism_is_rejected() -> None:
    found = codes(
        "Explain why a feedback loop can become unstable.",
        "Go with the flow and seek cosmic balance.",
    )
    assert "vague_laozi_filler" in found


def test_short_teaching_response_without_example_or_next_step_is_flagged() -> None:
    found = codes("用简单的话解释递归", "递归就是函数直接调用自己。")
    assert "missing_example_or_next_step" in found
