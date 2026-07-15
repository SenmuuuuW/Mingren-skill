"""Transparent safety precedence checks; not a professional classifier."""

from __future__ import annotations

import re

from mingren_skill.models import SafetyDecision

CATEGORY_PATTERNS: dict[str, tuple[str, ...]] = {
    "medical": (r"\b(diagnos|dose|medication|symptom|doctor|patient|surgery)\w*\b",),
    "legal": (r"\b(lawsuit|legal advice|attorney|contract|criminal|liability)\b",),
    "financial": (r"\b(invest|stock|tax advice|retirement|portfolio|crypto)\w*\b",),
    "self-harm": (r"\b(kill myself|suicide|self[- ]harm|hurt myself)\b",),
    "dangerous activities": (r"\b(bomb|explosive|poison|weapon|break in|hotwire)\w*\b",),
    "security-sensitive": (r"\b(exploit|malware|ransomware|steal password|bypass authentication|credential)\w*\b",),
    "manipulative questioning": (r"\b(trick|corner|coerce|manipulate)\b.*\b(question|admit|agree|consent)\w*\b",),
    "urgent non-intervention": (r"\b(emergency|urgent|immediately|right now|active breach|overdose|bleeding)\b",),
}

HIGH_RISK = {"self-harm", "dangerous activities", "security-sensitive", "urgent non-intervention"}
PROFESSIONAL = {"medical", "legal", "financial"}


def evaluate_safety(user_input: str) -> SafetyDecision:
    text = " ".join(user_input.lower().split())
    categories = [
        category
        for category, patterns in CATEGORY_PATTERNS.items()
        if any(re.search(pattern, text) for pattern in patterns)
    ]
    if not categories:
        return SafetyDecision(True, "low", [], [], [])

    high_risk = any(category in HIGH_RISK for category in categories)
    manipulative = "manipulative questioning" in categories
    professional = any(category in PROFESSIONAL for category in categories)
    required = ["prioritize factual correctness and applicable safety boundaries"]
    prohibited = ["do not treat a thinker lens as professional authority"]

    if professional:
        required.append("preserve professional standards, uncertainty, and qualified-guidance boundaries")
        prohibited.append("do not diagnose or give falsely definitive professional conclusions")
    if "urgent non-intervention" in categories:
        required.append("give established urgent protective action before optional lens analysis")
        prohibited.append("do not recommend delay or non-intervention")
    if manipulative:
        required.append("use neutral, consent-respecting questions or decline manipulative framing")
        prohibited.append("do not use Socratic questioning to corner, shame, or coerce")
    if high_risk:
        required.append("limit the structured plan to safe, protective, and non-operational guidance")
        prohibited.append("do not provide instructions that facilitate serious harm")

    return SafetyDecision(
        allowed=not (high_risk or manipulative),
        risk_level="high" if high_risk else "medium",
        applicable_boundaries=categories,
        required_behavior=required,
        prohibited_behavior=prohibited,
    )
