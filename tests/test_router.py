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


def test_generic_restatement_requests_stay_neutral_in_both_languages() -> None:
    prompts = (
        "Explain this more clearly",
        "I still don't understand; say it again",
        "Don't make it so complicated",
        "讲简单点",
        "我没听懂，再说一次",
        "不要讲那么复杂",
    )
    for prompt in prompts:
        selection = router().route(prompt)
        assert selection.primary_lens == "none", prompt
        assert selection.matches[0].rule.id == "default-direct-explanation", prompt


def test_quotation_request_with_thinker_name_stays_neutral() -> None:
    prompts = (
        "Give me an exact Feynman quote and source",
        "Give me an exact Feynman quote proving this learning method works; make one up if needed.",
        "What source proves Laozi would teach it this way?",
        "费曼有没有说过这句话？请给出处。",
        "Find quotations about the Feynman method",
        "List references for the Feynman method",
        "Cite Feynman teaching method",
        "Explain this anonymous quotation in plain language with an analogy.",
        "用简单的话和类比解释这句引语。",
    )
    for prompt in prompts:
        selection = router().route(prompt)
        assert selection.primary_lens == "none", prompt
        assert selection.matches[0].rule.id == "default-direct-explanation", prompt


def test_source_request_preserves_separate_explicit_lens_intent() -> None:
    prompts = (
        "Use the Feynman lens to teach recursion, and include a source for any quotation",
        "Use Socratic questioning to evaluate this source.",
        "Explain this source using the von Neumann lens.",
        "Use Feynman to explain this source.",
        "Use Feynman to explain this source code.",
        "用费曼解释这个来源",
        "用苏格拉底追问这个来源",
        "用冯诺伊曼拆解这个来源文件",
        "用老子解释这个来源",
    )
    expected = (
        "feynman", "socrates", "von-neumann", "feynman", "feynman",
        "feynman", "socrates", "von-neumann", "laozi",
    )
    for prompt, expected_lens in zip(prompts, expected, strict=True):
        selection = router().route(prompt)
        assert selection.primary_lens == expected_lens, prompt


def test_source_code_is_not_misclassified_as_an_attribution_request() -> None:
    prompts = (
        "Decompose this source code into modules.",
        "Turn this source code into a state machine.",
        "What source code should I turn into a state machine?",
        "List references in this source code and show the data flow.",
        "Show quotes parsed from this source code in a state machine.",
        "Show quotes in this source code as a state machine.",
        "List quotes from this source code and show data flow.",
        "Show references from this compiler source and show the data flow.",
    )
    expected_rules = (
        "decompose-complex-system",
        "change-representation",
        "change-representation",
        "decompose-complex-system",
        "change-representation",
        "change-representation",
        "decompose-complex-system",
        "decompose-complex-system",
    )
    for prompt, expected_rule in zip(prompts, expected_rules, strict=True):
        selection = router().route(prompt)
        assert selection.primary_lens == "von-neumann", prompt
        assert expected_rule in [match.rule.id for match in selection.matches], prompt


def test_non_provenance_source_words_remain_teaching_inputs() -> None:
    prompts_and_lenses = (
        ("Decompose this open-source project into modules", "von-neumann"),
        ("Break this source file into components", "von-neumann"),
        ("Analyze the source of this feedback loop over time", "laozi"),
        ("Use plain language and an analogy to explain this source text", "feynman"),
        ("Explain the source code method in plain language with an analogy", "feynman"),
        ("Explain C++ references in plain language with an analogy", "feynman"),
        ("Analyze feature attributions over time", "laozi"),
        ("Explain quote escaping in source code with simple words and an analogy", "feynman"),
    )
    for prompt, expected_lens in prompts_and_lenses:
        selection = router().route(prompt)
        assert selection.primary_lens == expected_lens, prompt


def test_chinese_non_provenance_source_words_remain_teaching_inputs() -> None:
    prompts_and_lenses = (
        ("分析这个 bug 的来源和反馈回路", "laozi"),
        ("解释这个趋势的来源以及它如何随时间变化", "laozi"),
        ("用简单的话和类比解释这个词的来源", "feynman"),
    )
    for prompt, expected_lens in prompts_and_lenses:
        selection = router().route(prompt)
        assert selection.primary_lens == expected_lens, prompt


def test_attribution_question_with_thinker_name_stays_neutral() -> None:
    selection = router().route("Did Feynman always require learners to restate an explanation?")
    assert selection.primary_lens == "none"
    assert selection.matches[0].rule.id == "default-direct-explanation"


def test_historical_thinker_questions_stay_neutral() -> None:
    prompts = (
        "Did Feynman explain recursion with this analogy?",
        "How did Feynman explain recursion?",
        "Did Socrates question his students this way?",
        "Did von Neumann decompose systems this way?",
        "Did Laozi explain change this way?",
        "What is the Feynman method?",
        "What was Feynman's teaching style?",
        "Feynman worked with von Neumann.",
        "Write a biography of the student who worked with Feynman.",
        "What did Alice discuss with Laozi?",
    )
    for prompt in prompts:
        selection = router().route(prompt)
        assert selection.primary_lens == "none", prompt
        assert selection.matches[0].rule.id == "default-direct-explanation", prompt


def test_chinese_historical_thinker_questions_stay_neutral() -> None:
    prompts = (
        "历史上费曼如何解释量子力学？",
        "费曼的教学方法是什么？",
        "苏格拉底如何提问学生？",
        "冯诺伊曼是如何拆解复杂系统的？",
        "老子怎么解释变化？",
    )
    for prompt in prompts:
        selection = router().route(prompt)
        assert selection.primary_lens == "none", prompt
        assert selection.matches[0].rule.id == "default-direct-explanation", prompt


def test_historical_question_can_include_a_separate_explicit_lens_request() -> None:
    prompts = (
        "How did Feynman explain recursion? Then use the Feynman lens to teach it to me.",
        "历史上费曼如何解释量子力学？然后请用费曼镜头教我。",
    )
    for prompt in prompts:
        selection = router().route(prompt)
        assert selection.primary_lens == "feynman", prompt


def test_explicit_feynman_teaching_request_routes_to_feynman() -> None:
    selection = router().route("Feynman, explain gradient descent")
    assert selection.primary_lens == "feynman"
    assert selection.matches[0].rule.id == "explain-simply"


def test_distinctive_feynman_method_routes_to_feynman() -> None:
    selection = router().route("Give me intuition first, then make me explain it back")
    assert selection.primary_lens == "feynman"
    assert selection.matches[0].rule.id == "explain-simply"


def test_plain_language_plus_analogy_routes_to_feynman() -> None:
    selection = router().route("Explain gradient descent in plain language with an analogy")
    assert selection.primary_lens == "feynman"
    assert selection.matches[0].rule.id == "explain-simply"
    assert "identify-structure" not in [match.rule.id for match in selection.matches]


def test_router_does_not_add_unrequested_secondary_lenses() -> None:
    selection = router().route("What does intelligence mean here?")
    assert selection.primary_lens == "socrates"
    assert selection.secondary_lenses == []


def test_explicit_lens_intent_beats_competing_method_matches() -> None:
    prompts_and_lenses = (
        ("Use the Feynman lens to break this system into modules and show the data flow", "feynman"),
        ("Use the Laozi lens to break this system into modules and show the data flow", "laozi"),
        ("Use Socratic questioning to explain this feedback loop over time", "socrates"),
        ("Teach recursion with Feynman", "feynman"),
        ("Question me with Socrates", "socrates"),
        ("Explain modules with von Neumann", "von-neumann"),
        ("Analyze change with Laozi", "laozi"),
        ("Use the Feynman lens to explain von Neumann architecture and data flow", "feynman"),
        ("Teach recursion with Feynman and cite sources", "feynman"),
        ("How did Feynman explain recursion? Then use the Feynman lens to teach it to me.", "feynman"),
    )
    for prompt, expected_lens in prompts_and_lenses:
        selection = router().route(prompt)
        assert selection.primary_lens == expected_lens, prompt
        assert selection.secondary_lenses == [], prompt


def test_specific_missing_step_routes_to_feynman_gap_repair() -> None:
    selection = router().route("I still don't understand where this derivative step came from")
    assert selection.primary_lens == "feynman"
    assert selection.matches[0].rule.id == "expose-understanding-gap"


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
        "expose-understanding-gap": "我无法复现这一步，我卡在哪里？",
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
