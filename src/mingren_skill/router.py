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
        r"(先用类比|让我复述|用自己的话讲回来|先讲直觉再讲公式)",
    ),
    "expose-understanding-gap": (
        r"\bi (still )?don'?t understand\b", r"\bwhere am i going wrong\b", r"\bmissing step\b",
        r"(还是不理解|还是没明白|我卡在哪|哪一步没懂)",
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
        r"\b(pattern|invariant|isomorphic|structural similarity|analogy)\b", r"\bsame structure\b",
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
        matches: list[TriggerMatch] = []
        for rule_id, patterns in PATTERNS.items():
            signals = [pattern for pattern in patterns if re.search(pattern, text, re.IGNORECASE)]
            if signals:
                rule = self.rules[rule_id]
                strength = len(signals) * 10 + rule.priority
                matches.append(TriggerMatch(rule=rule, strength=strength, matched_signals=signals))

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

        primary_match = next(
            (match for match in matches if match.rule.primary_lens != "none"),
            matches[0],
        )
        secondary: list[str] = []
        for match in matches:
            lens = match.rule.primary_lens
            if lens not in {"none", primary_match.rule.primary_lens} and lens not in secondary:
                if frozenset({lens, primary_match.rule.primary_lens}) in COMPATIBLE_LENS_PAIRS:
                    secondary.append(lens)
        for lens in primary_match.rule.secondary_lenses:
            if lens != primary_match.rule.primary_lens and lens not in secondary:
                secondary.append(lens)

        return LensSelection(
            primary_lens=primary_match.rule.primary_lens,
            secondary_lenses=secondary,
            matches=matches,
            conflict_detected=conflict,
            debug_explanation=(
                f"Matched {', '.join(match.rule.id for match in matches)}; "
                f"ranked by transparent pattern strength and rule priority."
            ),
        )

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
