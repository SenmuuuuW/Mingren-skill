from __future__ import annotations

import json

from mingren_skill.__main__ import main


def test_cli_plan_command(capsys) -> None:
    assert main(["plan", "用简单的话解释递归"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["matched_rule_ids"] == ["default-direct-explanation"]


def test_cli_legacy_input_remains_plan(capsys) -> None:
    assert main(["Tell me a joke"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["selected_primary_lens"] == "none"


def test_cli_prompt_command(capsys) -> None:
    assert main(["prompt", "这里的理解到底是什么意思？"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["applied_rules"] == ["clarify-definition"]
    assert "<user_request>" in output["user_prompt"]


def test_cli_validate_response_command(capsys) -> None:
    assert main([
        "validate-response", "我胸口剧痛而且无法呼吸",
        "--response", "顺其自然，先观察一下。",
    ]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["valid"] is False
    assert "unsafe_non_intervention" in {issue["code"] for issue in output["issues"]}
