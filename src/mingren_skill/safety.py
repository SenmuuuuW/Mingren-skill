"""Transparent safety precedence checks; not a professional classifier."""

from __future__ import annotations

import re

from mingren_skill.models import SafetyDecision

CATEGORY_PATTERNS: dict[str, tuple[str, ...]] = {
    "medical": (
        r"\b(diagnos|dose|medication|symptom|doctor|patient|surgery)\w*\b",
        r"\b(chest (pain|hurts?)|cannot breathe|can'?t breathe|difficulty breathing|shortness of breath)\b",
        r"(诊断|剂量|药物|症状|医生|患者|手术|胸口.*痛|胸痛|无法呼吸|不能呼吸|呼吸困难)",
    ),
    "legal": (r"\b(lawsuit|legal advice|attorney|contract|criminal|liability)\b", r"(法律建议|律师|合同|刑事|法律责任|起诉)"),
    "financial": (r"\b(invest|stock|tax advice|retirement|portfolio|crypto)\w*\b", r"(投资|股票|税务建议|退休金|投资组合|加密货币)"),
    "self-harm": (r"\b(kill myself|suicide|self[- ]harm|hurt myself)\b", r"(自杀|自残|伤害自己|不想活了)"),
    "dangerous activities": (r"\b(bomb|explosive|poison|weapon|break in|hotwire)\w*\b", r"(炸弹|爆炸物|下毒|武器|撬锁|偷车)"),
    "security-sensitive": (r"\b(exploit|malware|ransomware|steal password|bypass authentication|credential)\w*\b", r"(漏洞利用|恶意软件|勒索软件|偷.*密码|绕过认证|凭证)"),
    "manipulative questioning": (r"\b(trick|corner|coerce|manipulate)\b.*\b(question|admit|agree|consent)\w*\b", r"(诱导|逼迫|操纵|套话).*(承认|同意|问题|提问)"),
    "urgent non-intervention": (
        r"\b(emergency|urgent|immediately|right now|active breach|overdose|bleeding|cannot breathe|can'?t breathe)\b",
        r"(紧急|马上|立刻|正在入侵|过量服药|大出血|无法呼吸|不能呼吸|剧痛)",
    ),
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
