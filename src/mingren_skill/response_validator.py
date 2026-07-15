"""Deterministic structural and safety validation for generated responses."""

from __future__ import annotations

import re
from typing import cast

from mingren_skill.language import detect_language
from mingren_skill.models import (
    IssueSeverity,
    PromptContext,
    ResponseValidationResult,
    ValidationIssue,
)

THINKER_NAMES = ("Feynman", "Socrates", "von Neumann", "Laozi", "费曼", "苏格拉底", "冯诺伊曼", "冯·诺伊曼", "老子")
IMPERSONATION_RE = re.compile(
    r"\bI\s+am\s+(?:Richard\s+)?(?:Feynman|Socrates|John\s+von\s+Neumann|Laozi)\b|"
    r"我是(?:费曼|苏格拉底|冯[·・]?诺伊曼|老子)",
    re.IGNORECASE,
)
QUOTE_RE = re.compile(
    r"(?:Feynman|Socrates|von Neumann|Laozi)\s+(?:said|says|wrote)\s*[,:]?\s*[\"“]|"
    r"(?:费曼|苏格拉底|冯[·・]?诺伊曼|老子)(?:说|写道|曰)[：:]?\s*[\"“]",
    re.IGNORECASE,
)
INTERNAL_LEAK_RE = re.compile(
    r"(?:system_prompt|developer_prompt|debug_metadata|debug_explanation|matched_rule_ids|"
    r"<user_request>|REQUIRED TEACHING BEHAVIOR|SAFETY PRECEDENCE)",
    re.IGNORECASE,
)
UNSAFE_WAIT_RE = re.compile(
    r"\b(?:wait and see|do nothing|avoid seeking help|no need for emergency|just observe)\b|"
    r"(?:顺其自然|先观察(?:一下)?|等等看|什么都不做|不用急救|不必就医)",
    re.IGNORECASE,
)
SAFETY_WARNING_RE = re.compile(
    r"\b(?:emergency|call|urgent|doctor|medical help|professional help|immediately)\b|"
    r"(?:急救|急诊|立即|马上|呼叫|120|医生|专业帮助)",
    re.IGNORECASE,
)
VAGUE_RE = re.compile(r"(?:顺其自然|万物|玄之又玄|和谐|宇宙平衡|go with the flow|cosmic balance|mystical harmony)", re.IGNORECASE)
CONCRETE_RE = re.compile(r"(?:因为|意味着|定义|机制|例如|如果|关系|反馈|阈值|because|means|definition|mechanism|for example|if|feedback|threshold|\d)", re.IGNORECASE)
DIRECT_RE = re.compile(r"(?:是|指|表示|意味着|因为|需要|首先|is|means|refers to|because|works by|should|first)", re.IGNORECASE)
TEACHING_REQUEST_RE = re.compile(r"(?:解释|讲清楚|教我|说明|explain|teach|help me understand)", re.IGNORECASE)
EXAMPLE_OR_STEP_RE = re.compile(r"(?:例如|比如|例子|下一步|试着|可以先|for example|example|next step|try|consider|[?？])", re.IGNORECASE)


class ResponseValidator:
    """Find likely response failures without claiming factual verification."""

    def validate(self, context: PromptContext, response: str) -> ResponseValidationResult:
        issues: list[ValidationIssue] = []
        stripped = response.strip() if isinstance(response, str) else ""
        if not stripped:
            issues.append(self._issue("empty_response", "error", "Response is empty.", "No non-whitespace text"))
            return self._result(issues)

        response_language = detect_language(stripped)
        if context.language == "chinese" and response_language == "english":
            issues.append(self._issue("wrong_output_language", "error", "Chinese input should normally receive Chinese output.", response_language))
        elif context.language == "english" and response_language == "chinese":
            issues.append(self._issue("wrong_output_language", "error", "English input should normally receive English output.", response_language))

        match = IMPERSONATION_RE.search(stripped)
        if match:
            issues.append(self._issue("thinker_impersonation", "error", "The response explicitly impersonates a thinker.", match.group(0)))
        match = QUOTE_RE.search(stripped)
        if match:
            issues.append(self._issue("suspicious_thinker_quote", "warning", "A direct thinker quotation pattern requires source verification or paraphrase.", match.group(0)))
        match = INTERNAL_LEAK_RE.search(stripped)
        if match:
            issues.append(self._issue("internal_prompt_leakage", "error", "The response exposes internal prompt, rule, or debug content.", match.group(0)))

        segments = [segment.strip() for segment in re.split(r"(?<=[.!?。！？])\s*", stripped) if segment.strip()]
        question_count = len(re.findall(r"[?？]", stripped))
        if question_count and question_count >= max(3, int(len(segments) * 0.6 + 0.5)):
            issues.append(self._issue("excessive_questioning", "warning", "Too much of the response is questioning rather than teaching or synthesis.", f"{question_count} questions / {len(segments)} segments"))
        if segments and all(segment.endswith(("?", "？")) for segment in segments):
            issues.append(self._issue("questions_only", "error", "The response contains only questions and no direct explanation.", stripped[:160]))
        elif not DIRECT_RE.search(stripped) and len(stripped) < 120:
            issues.append(self._issue("missing_direct_explanation", "warning", "The response may lack a direct explanatory statement.", stripped[:160]))
        if TEACHING_REQUEST_RE.search(context.user_input) and not EXAMPLE_OR_STEP_RE.search(stripped):
            issues.append(self._issue("missing_example_or_next_step", "warning", "The teaching response omits a concrete example, understanding check, or next step.", stripped[:160]))

        name_count = sum(len(re.findall(re.escape(name), stripped, re.IGNORECASE)) for name in THINKER_NAMES)
        if name_count > 3:
            issues.append(self._issue("thinker_name_overuse", "warning", "The thinker name is repeated excessively instead of letting the method carry the answer.", str(name_count)))

        if context.engine_result.selected_primary_lens == "laozi" and VAGUE_RE.search(stripped) and not CONCRETE_RE.search(stripped):
            issues.append(self._issue("vague_laozi_filler", "error", "Laozi-inspired language is not connected to a concrete modern mechanism.", VAGUE_RE.search(stripped).group(0)))

        high_risk = context.engine_result.safety.risk_level == "high"
        if high_risk:
            unsafe = UNSAFE_WAIT_RE.search(stripped)
            if unsafe:
                issues.append(self._issue("unsafe_non_intervention", "error", "The response recommends delay or passivity in an urgent context.", unsafe.group(0)))
            if not SAFETY_WARNING_RE.search(stripped):
                issues.append(self._issue("missing_required_safety_warning", "error", "The urgent response omits clear protective or emergency guidance.", stripped[:160]))

        if "explain-simply" in context.engine_result.matched_rule_ids:
            formal_markers = re.search(r"(?:术语|定义|正式|公式|term|definition|formal|formula|called)", stripped, re.IGNORECASE)
            if not formal_markers:
                issues.append(self._issue("technical_precision_not_restored", "warning", "A simplified explanation may not restore necessary formal terminology or definitions.", stripped[:160]))

        return self._result(issues)

    @staticmethod
    def _issue(code: str, severity: str, message: str, evidence: str) -> ValidationIssue:
        return ValidationIssue(
            code=code,
            severity=cast(IssueSeverity, severity),
            message=message,
            evidence=evidence,
        )

    @staticmethod
    def _result(issues: list[ValidationIssue]) -> ResponseValidationResult:
        actions = list(dict.fromkeys(issue.message for issue in issues if issue.severity in {"error", "warning"}))
        return ResponseValidationResult(
            valid=not any(issue.severity == "error" for issue in issues),
            issues=issues,
            required_revision_actions=actions,
        )
