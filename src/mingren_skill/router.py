"""Deterministic and inspectable first-version trigger router."""

from __future__ import annotations

import re
from collections.abc import Iterable

from mingren_skill.models import LensSelection, TriggerMatch, TriggerRule

PATTERNS: dict[str, tuple[str, ...]] = {
    "explain-simply": (
        r"\bfeynman\b.*\b(teach|explain|lens|method|way|style)\b", r"\b(use|through)\b.*\bfeynman\b",
        r"费曼.*(教|解释|方式|镜头|方法)",
        r"\b(analogy first|explain[- ]back|in my own words|intuition before (the )?formula)\b",
        r"\bintuition first\b.*\bexplain (it )?back\b",
        r"\b(plain language|simple words)\b.*\banalogy\b", r"\banalogy\b.*\b(plain language|simple words)\b",
        r"((白话|简单的话).*类比|类比.*(白话|简单的话)|先用类比|让我复述|用自己的话讲回来|先讲直觉再讲公式)",
    ),
    "expose-understanding-gap": (
        r"\bi can'?t (reproduce|apply|explain (it )?back)\b", r"\bwhere am i going wrong\b", r"\bwhere .* step (came|comes) from\b", r"\bmissing step\b",
        r"(我无法复现|我不会应用|我没法用自己的话复述|我卡在哪|哪一步没懂)",
    ),
    "clarify-definition": (
        r"\bdefine\b", r"\bwhat (exactly )?do(es| you) .* mean\b", r"\bambiguous\b",
        r"(是什么意思|到底指什么|如何定义|怎么定义|含义不清|有歧义)",
    ),
    "challenge-assumption": (
        r"\b(socrates|socratic)\b.*\b(teach|question|lens|method|way|style)\w*\b", r"\b(use|through)\b.*\b(socrates|socratic)\b",
        r"苏格拉底.*(教|追问|提问|方式|镜头|方法)",
        r"\bassum(e|ption|ing)\b", r"\bhidden premise\b", r"\bchallenge (this|my|the)\b",
        r"\bi think\b.*\bis that correct\b", r"\bwhat premise\b",
        r"(这个前提对吗|这个假设|隐藏前提|是不是默认|质疑.*前提)",
    ),
    "test-with-counterexample": (
        r"\bcounterexample\b", r"\b(always|never|all|none)\b", r"\bdoes this hold\b",
        r"(反例|总是如此|一定都|从来不会|是否对所有.*成立)",
    ),
    "decompose-complex-system": (
        r"\b(von neumann|von-neumann)\b.*\b(teach|explain|decompose|lens|method|way|style)\w*\b", r"\b(use|through)\b.*\b(von neumann|von-neumann)\b",
        r"冯[·・]?诺伊曼.*(教|解释|拆解|分解|方式|镜头|方法)",
        r"\b(break|split|decompose)\b.*\b(system|modules?|components?)\b", r"\barchitecture\b", r"\bdata flow\b",
        r"(把.*系统.*拆成.*模块|分解.*系统|模块划分|系统架构|数据流)",
    ),
    "change-representation": (
        r"\b(diagram|table|graph|state machine|equation|flowchart)\b", r"\banother representation\b", r"\bturn .* into\b.*\b(model|table|graph)\b",
        r"(画成图|整理成表格|状态机|流程图|换一种表示|转成.*模型)",
    ),
    "identify-structure": (
        r"\b(pattern|invariant|isomorphic|structural similarity)\b", r"\bsame structure\b",
        r"\banalogy\b.*\b(mapping|preserved|broken|breaks?|structure)\b",
        r"(相同结构|共同模式|结构相似|不变量|这个类比.*哪里.*失效)",
    ),
    "analyze-dynamic-change": (
        r"\blaozi\b.*\b(teach|explain|lens|method|way|style)\b", r"\b(use|through)\b.*\blaozi\b",
        r"老子.*(教|解释|方式|镜头|方法)",
        r"\b(feedback loop|trend|second-order|dynamic|over time|unintended consequence)\b", r"\bwhat changes if\b",
        r"(反馈回路|反馈环|随时间变化|二阶影响|意外后果|为何.*不稳定|为什么.*不稳定)",
    ),
    "minimize-unnecessary-intervention": (
        r"\b(minimum|minimal|least|smallest)\b.*\b(intervention|change|action)\b", r"\bdo nothing\b", r"\bnon-intervention\b",
        r"(最小干预|最少干预|什么都不做|不干预|无为.*最好)",
    ),
    "detect-lens-conflict": (
        r"\bconflicting lenses?\b", r"\bsimpl(?:e|y|ify)\b.*\b(precise|precision|exact)\b", r"\bquestion.*direct answer\b",
        r"(简单|白话).*(精确|严谨|准确)", r"(只问问题).*(直接答案)",
    ),
}

TECHNICAL_SOURCE_OBJECT = r"(?:source code|code|parser|compiler|syntax tree|ast)"
TECHNICAL_SOURCE_SUFFIX = (
    rf"(?:in|from|inside)\s+(?:this\s+|the\s+|a\s+)?{TECHNICAL_SOURCE_OBJECT}"
)
TECHNICAL_QUOTE_FOLLOWUP = (
    r"(?:escaping|characters?|marks?|delimiters?|syntax|handling|parser|parsing|"
    r"parsed|tokens?|strings?|literals?)"
)
PROVENANCE_NOUN = r"(?:sources?|citations?|attributions?|references?|bibliograph(?:y|ies))"

QUOTATION_REQUEST_PATTERNS = (
    rf"\b(?:give|find|provide|list|show|verify|check|cite)\b.{{0,80}}\b(?:quotes?|quotations?)\b(?!\s+(?:{TECHNICAL_QUOTE_FOLLOWUP}|{TECHNICAL_SOURCE_SUFFIX})\b)",
    rf"\b(?:this|that|an?|the)(?:\s+(?:anonymous|exact|direct|verified|alleged|famous)){{0,2}}\s+(?:quotes?|quotations?)\b(?!\s+(?:{TECHNICAL_QUOTE_FOLLOWUP}|{TECHNICAL_SOURCE_SUFFIX})\b)",
    r"(原话|引语|名言|这句引文|这段引文|有没有说过|是否说过)",
)
PROVENANCE_REQUEST_PATTERNS = (
    rf"\b(?:give|provide|find|show|list|verify|check|cite|attribute|include|add)\b(?:(?!\b{PROVENANCE_NOUN}\b).){{0,80}}\b{PROVENANCE_NOUN}\b(?!\s+(?:{TECHNICAL_SOURCE_SUFFIX}|code|files?|texts?|projects?|systems?|data|trees?|maps?)\b)",
    r"\b(what|which)\s+sources?\b(?!\s+(code|files?|texts?|projects?|systems?|data|trees?|maps?)\b)",
    r"\bsources?\b(?!\s+(code|files?|texts?|projects?|systems?|data|trees?|maps?)\b).{0,80}\b(prove|support|verify|confirm|evidence|claim|said|taught)\w*\b",
    r"(给出|提供|查找|核实|验证|注明).{0,20}(出处|来源)",
    r"(出处|来源).{0,20}(证明|支持|核实|验证|引文|引用)",
)
THINKER_PROVENANCE_PATTERNS = (
    r"\b(citations?|attributions?|references?|bibliograph(?:y|ies)|cite|cites|cited|attributed)\b",
    r"\b(did|does|has|would)\b.*\b(feynman|socrates|socratic|von neumann|von-neumann|laozi)\b.*\b(say|require|believe|teach|write|claim)\w*\b",
    r"(费曼|苏格拉底|冯[·・]?诺伊曼|老子).{0,20}(方法|观点|说法).{0,12}(出处|来源)",
)
HISTORICAL_THINKER_REQUEST_PATTERNS = (
    r"^\s*(did|how did|what did|when did|where did|why did)\b.*\b(feynman|socrates|von neumann|von-neumann|laozi)\b",
    r"^\s*what (is|was)\b.*\b(feynman|socrates|von neumann|von-neumann|laozi)(?:'s)?\b.*\b(method|teaching style|approach|way)\b",
    r"(费曼|苏格拉底|冯[·・]?诺伊曼|老子).*(是否|曾经|当时|历史上).*(说|教|解释|提问|拆解|方法)",
    r"历史上.*(费曼|苏格拉底|冯[·・]?诺伊曼|老子).*(如何|怎么).*(解释|教|提问|拆解|分析)",
    r"(费曼|苏格拉底|冯[·・]?诺伊曼|老子).*(教学方法|教学方式|思想方法|方法).*(是什么|如何|怎么样)",
    r"(费曼|苏格拉底|冯[·・]?诺伊曼|老子).*(如何|怎么|是如何).*(解释|教|提问|拆解|分析)",
    r"^\s*(describe|summarize|tell me about)\b.*\b(feynman|socrates|von neumann|von-neumann|laozi)(?:'s)?\b.*\b(method|teaching style|approach|history|biography)\b",
)
LENS_NAME_PATTERNS = {
    "feynman": r"\b(feynman)\b|费曼|费恩曼",
    "socrates": r"\b(socrates|socratic)\b|苏格拉底",
    "von-neumann": r"\b(von neumann|von-neumann)\b|冯[·・]?诺伊曼|冯[·・]?诺依曼",
    "laozi": r"\b(laozi|lao tzu)\b|老子",
}
EXPLICIT_RULE_BY_LENS = {
    "feynman": "explain-simply",
    "socrates": "challenge-assumption",
    "von-neumann": "decompose-complex-system",
    "laozi": "analyze-dynamic-change",
}


def _lens_intent_patterns(english_alias: str, chinese_alias: str) -> tuple[str, ...]:
    descriptor = r"lens|method|way|style|approach|questioning"
    action = r"teach|explain|question|analyze|evaluate|decompose|clarify|reframe"
    return (
        rf"\buse\s+(the\s+)?({english_alias})(?:\s+({descriptor}))?\b",
        rf"\b(using|through)\s+(the\s+)?({english_alias})\s+({descriptor})\b",
        rf"\b({action})\b[^.!?。！？]*\b(using|through|with)\s+(the\s+)?({english_alias})(?:\s+({descriptor}))?\b",
        rf"^\s*(please\s+)?({english_alias})\b[,:]?\s*({action})\b",
        rf"(用|通过)\s*({chinese_alias})(镜头|方式|方法)?(来)?(教|解释|追问|拆解|分解|分析)",
        rf"({chinese_alias}).*(教我|给我讲|解释给我|追问我)",
    )


EXPLICIT_LENS_PATTERNS = {
    "feynman": _lens_intent_patterns(r"feynman", r"费曼|费恩曼"),
    "socrates": _lens_intent_patterns(r"socrates|socratic", r"苏格拉底"),
    "von-neumann": _lens_intent_patterns(
        r"von neumann|von-neumann", r"冯[·・]?诺伊曼|冯[·・]?诺依曼"
    ),
    "laozi": _lens_intent_patterns(r"laozi|lao tzu", r"老子"),
}

COMPATIBLE_LENS_PAIRS = {
    frozenset({"feynman", "socrates"}),
    frozenset({"von-neumann", "laozi"}),
}


class DeterministicRouter:
    def __init__(self, rules: Iterable[TriggerRule]):
        self.rules = {rule.id: rule for rule in rules}
        missing = set(PATTERNS) - self.rules.keys()
        if missing:
            raise ValueError(f"router is missing configured rules: {', '.join(sorted(missing))}")
        if "default-direct-explanation" not in self.rules:
            raise ValueError("router requires default-direct-explanation")

    def route(self, user_input: str) -> LensSelection:
        text = " ".join(user_input.lower().split())
        explicit_lenses = self._explicit_lenses(text)
        has_explicit_lens_intent = bool(explicit_lenses)
        explicit_lens = explicit_lenses[0] if len(explicit_lenses) == 1 else None
        thinker_mentioned = any(
            re.search(pattern, text, re.IGNORECASE)
            for pattern in LENS_NAME_PATTERNS.values()
        )
        quotation_or_source_request = (
            any(
                re.search(pattern, text, re.IGNORECASE)
                for pattern in QUOTATION_REQUEST_PATTERNS
            )
            or any(
                re.search(pattern, text, re.IGNORECASE)
                for pattern in PROVENANCE_REQUEST_PATTERNS
            )
            or (
                thinker_mentioned
                and any(
                    re.search(pattern, text, re.IGNORECASE)
                    for pattern in THINKER_PROVENANCE_PATTERNS
                )
            )
        )
        if not has_explicit_lens_intent and any(
            re.search(pattern, text, re.IGNORECASE)
            for pattern in HISTORICAL_THINKER_REQUEST_PATTERNS
        ):
            default = self.rules["default-direct-explanation"]
            return LensSelection(
                primary_lens=default.primary_lens,
                secondary_lenses=[],
                matches=[
                    TriggerMatch(
                        default,
                        default.priority,
                        ["historical or factual thinker question without teaching-lens intent"],
                    )
                ],
                conflict_detected=False,
                debug_explanation=(
                    "Historical or factual thinker question detected without teaching-lens intent; "
                    "selected neutral fallback."
                ),
            )
        if quotation_or_source_request and not has_explicit_lens_intent:
            default = self.rules["default-direct-explanation"]
            return LensSelection(
                primary_lens=default.primary_lens,
                secondary_lenses=[],
                matches=[
                    TriggerMatch(
                        default,
                        default.priority,
                        ["quotation or source request without explicit teaching-lens intent"],
                    )
                ],
                conflict_detected=False,
                debug_explanation=(
                    "Quotation or source request detected without explicit teaching-lens intent; "
                    "selected neutral attribution-safe fallback."
                ),
            )
        matches: list[TriggerMatch] = []
        for rule_id, patterns in PATTERNS.items():
            signals = [pattern for pattern in patterns if re.search(pattern, text, re.IGNORECASE)]
            if signals:
                rule = self.rules[rule_id]
                strength = len(signals) * 10 + rule.priority
                matches.append(TriggerMatch(rule=rule, strength=strength, matched_signals=signals))

        if explicit_lens is not None and not any(
            match.rule.primary_lens == explicit_lens for match in matches
        ):
            rule = self.rules[EXPLICIT_RULE_BY_LENS[explicit_lens]]
            matches.append(
                TriggerMatch(
                    rule=rule,
                    strength=10_000 + rule.priority,
                    matched_signals=[f"explicit {explicit_lens} teaching-lens intent"],
                )
            )

        if not matches:
            default = self.rules["default-direct-explanation"]
            return LensSelection(
                primary_lens=default.primary_lens,
                secondary_lenses=[],
                matches=[TriggerMatch(default, default.priority, ["no clear lens signal"])],
                conflict_detected=False,
                debug_explanation="No specific trigger matched; selected direct explanation fallback.",
            )

        matches.sort(key=lambda match: (-match.strength, -match.rule.priority, match.rule.id))
        conflict = self._has_conflict(matches)
        if conflict and all(match.rule.id != "detect-lens-conflict" for match in matches):
            rule = self.rules["detect-lens-conflict"]
            matches.insert(0, TriggerMatch(rule, 10_000 + rule.priority, ["incompatible candidate lenses"]))

        primary_match = (
            next(
                (
                    match
                    for match in matches
                    if match.rule.primary_lens == explicit_lens
                ),
                None,
            )
            if explicit_lens is not None
            else None
        )
        if primary_match is None:
            primary_match = next(
                (match for match in matches if match.rule.primary_lens != "none"),
                matches[0],
            )
        return LensSelection(
            primary_lens=primary_match.rule.primary_lens,
            secondary_lenses=[],
            matches=matches,
            conflict_detected=conflict,
            debug_explanation=(
                f"Matched {', '.join(match.rule.id for match in matches)}; "
                f"ranked by transparent pattern strength and rule priority."
            ),
        )

    @staticmethod
    def _explicit_lenses(text: str) -> list[str]:
        return [
            lens
            for lens, patterns in EXPLICIT_LENS_PATTERNS.items()
            if any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)
        ]

    @staticmethod
    def _has_conflict(matches: list[TriggerMatch]) -> bool:
        if any(match.rule.id == "detect-lens-conflict" for match in matches):
            return True
        lenses = {match.rule.primary_lens for match in matches if match.rule.primary_lens != "none"}
        if len(lenses) < 2:
            return False
        return any(
            frozenset({left, right}) not in COMPATIBLE_LENS_PAIRS
            for left in lenses for right in lenses if left != right
        )
