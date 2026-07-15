"""Lightweight language detection for prompt-output selection."""

from __future__ import annotations

import re

from mingren_skill.models import DetectedLanguage

HAN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
LATIN_WORD_RE = re.compile(r"\b[A-Za-z]{2,}\b")
CODE_MARKER_RE = re.compile(
    r"(?:\b(?:def|class|return|import|const|let|function|SELECT|FROM)\b|[{}();]|=>|==|::)"
)


def detect_language(text: str) -> DetectedLanguage:
    """Classify natural-language content as Chinese, English, mixed, or unknown."""
    if not isinstance(text, str) or not text.strip():
        return "unknown"

    han_count = len(HAN_RE.findall(text))
    latin_words = LATIN_WORD_RE.findall(text)
    code_markers = CODE_MARKER_RE.findall(text)
    non_space_length = len(re.sub(r"\s", "", text))

    if han_count == 0 and len(code_markers) >= 2 and non_space_length < 80:
        return "unknown"
    if han_count >= 2 and latin_words:
        return "mixed"
    if han_count >= 2:
        return "chinese"
    if len(latin_words) >= 2:
        return "english"
    return "unknown"
