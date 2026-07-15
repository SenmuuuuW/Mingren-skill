from mingren_skill.language import detect_language


def test_detects_chinese_only() -> None:
    assert detect_language("用简单的话解释递归") == "chinese"


def test_detects_english_only() -> None:
    assert detect_language("Explain recursion with an example") == "english"


def test_detects_mixed_language() -> None:
    assert detect_language("请解释 Python recursion 的机制") == "mixed"


def test_code_heavy_input_is_unknown() -> None:
    assert detect_language("def f(x): return f(x - 1)") == "unknown"


def test_empty_input_is_unknown() -> None:
    assert detect_language("   ") == "unknown"
