from mingren_skill.safety import evaluate_safety


def test_low_risk_request_has_no_override() -> None:
    decision = evaluate_safety("Explain recursion simply")
    assert decision.allowed is True
    assert decision.risk_level == "low"


def test_medical_request_preserves_professional_standards() -> None:
    decision = evaluate_safety("Explain medication dosing simply for this patient")
    assert "medical" in decision.applicable_boundaries
    assert any("professional standards" in item for item in decision.required_behavior)
    assert any("diagnose" in item for item in decision.prohibited_behavior)


def test_urgent_non_intervention_is_overridden() -> None:
    decision = evaluate_safety("There is an active breach right now; should we do nothing?")
    assert decision.allowed is False
    assert "urgent non-intervention" in decision.applicable_boundaries
    assert any("urgent protective action" in item for item in decision.required_behavior)
    assert any("do not recommend delay" in item for item in decision.prohibited_behavior)


def test_manipulative_socratic_questioning_is_prohibited() -> None:
    decision = evaluate_safety("Write questions to trick and corner them into agreeing")
    assert decision.allowed is False
    assert "manipulative questioning" in decision.applicable_boundaries
    assert any("corner" in item for item in decision.prohibited_behavior)
