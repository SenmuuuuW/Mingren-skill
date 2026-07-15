from __future__ import annotations

from pathlib import Path

from mingren_skill.loaders import load_trigger_rules
from mingren_skill.router import DeterministicRouter


ROOT = Path(__file__).resolve().parents[1]


def router() -> DeterministicRouter:
    return DeterministicRouter(load_trigger_rules(root=ROOT))


def test_generic_simple_explanation_stays_neutral() -> None:
    selection = router().route("Explain recursion simply")
    assert selection.primary_lens == "none"
    assert selection.matches[0].rule.id == "default-direct-explanation"


def test_explicit_feynman_teaching_request_routes_to_feynman() -> None:
    selection = router().route("Feynman, explain gradient descent")
    assert selection.primary_lens == "feynman"
    assert selection.matches[0].rule.id == "explain-simply"


def test_direct_question_does_not_force_socratic_questions() -> None:
    selection = router().route("What is a database index? Give me the answer directly")
    assert selection.primary_lens == "none"
    assert [match.rule.id for match in selection.matches] == ["default-direct-explanation"]


def test_conflicting_precision_and_simplicity_uses_conflict_rule() -> None:
    selection = router().route("Explain this simply but preserve exact technical precision")
    ids = [match.rule.id for match in selection.matches]
    assert selection.conflict_detected is True
    assert "detect-lens-conflict" in ids
    assert "explain-simply" not in ids
    assert selection.primary_lens == "none"


def test_system_decomposition_beats_generic_fallback() -> None:
    selection = router().route("Break this system into modules and show the data flow")
    assert selection.primary_lens == "von-neumann"
    assert "decompose-complex-system" in [match.rule.id for match in selection.matches]


def test_english_assumption_challenge_is_detected() -> None:
    selection = router().route("I think correlation proves causation. Is that correct?")
    assert selection.primary_lens == "socrates"
    assert "challenge-assumption" in [match.rule.id for match in selection.matches]


def test_chinese_routing_categories() -> None:
    cases = {
        "用简单的话解释递归。": ("none", "default-direct-explanation"),
        "这里的理解到底是什么意思？": ("socrates", "clarify-definition"),
        "我觉得只要努力就一定会成功，这个前提对吗？": ("socrates", "challenge-assumption"),
        "把一个复杂的软件系统拆成模块。": ("von-neumann", "decompose-complex-system"),
        "解释为什么反馈回路会变得不稳定。": ("laozi", "analyze-dynamic-change"),
        "给我讲个笑话。": ("none", "default-direct-explanation"),
    }
    for prompt, (expected_lens, expected_rule) in cases.items():
        selection = router().route(prompt)
        assert selection.primary_lens == expected_lens, prompt
        assert expected_rule in [match.rule.id for match in selection.matches], prompt


def test_chinese_patterns_cover_every_non_default_rule_category() -> None:
    prompts = {
        "explain-simply": "费曼用类比方式解释梯度下降。",
        "expose-understanding-gap": "我还是不理解这一步，我卡在哪里？",
        "clarify-definition": "这里的公平到底是什么意思？",
        "challenge-assumption": "这个前提对吗？",
        "test-with-counterexample": "请给这个结论找一个反例。",
        "decompose-complex-system": "把这个复杂系统拆成模块。",
        "change-representation": "把这个流程画成图。",
        "identify-structure": "这两个问题有什么相同结构？",
        "analyze-dynamic-change": "分析这个反馈回路为何不稳定。",
        "minimize-unnecessary-intervention": "比较最小干预和什么都不做。",
        "detect-lens-conflict": "请讲得简单但保持精确。",
    }
    for expected_rule, prompt in prompts.items():
        ids = [match.rule.id for match in router().route(prompt).matches]
        assert expected_rule in ids, prompt
