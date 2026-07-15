# Mingren Skill Runtime Contract

## Canonical execution model

The host model generates the final answer. Mingren Skill does not call an external model API.

Mingren is an installable, host-executed learning Skill. A capable host reads `SKILL.md` and the referenced Markdown/YAML files, performs the reasoning internally, and replies directly to the learner. Python, network access, API keys, command-line execution, and a backend server are not runtime requirements.

## Runtime files

The bundle entry point is `SKILL.md`. The host should also make these files available:

- `references/trigger-framework.md`
- `references/trigger_rules.yaml`
- `references/response-framework.md`
- `references/safety-boundaries.md`
- the selected file under `references/thinkers/`

The distillation framework, examples, quality rubric, and failure taxonomy are calibration aids included in the bundle but are not necessary for every answer. Tests, Python source, development evaluations, and scripts are optional maintainer tools and are not part of runtime execution.

## Input and selection

Input is an ordinary learner request in Chinese, English, or mixed technical language. The host preserves the learner's language and constraints, identifies topic and task, then applies this precedence:

1. safety and factual correctness;
2. an explicitly named supported lens;
3. a distinctive method request;
4. learning intent;
5. subject fit only as a tie-breaker;
6. neutral teaching when no lens is clear.

Several named lenses are compared or combined only when explicitly requested. Otherwise the host asks for one choice. Unsupported thinker requests receive the four-lens scope boundary plus a neutral or supported alternative; the host does not imitate that person.

## Host generation behavior

The host internally applies the selected method, grounds the actual concept, gives one small inspectable example when appropriate, and ends with one focused check or next step. It does not expose rule IDs, hidden plans, internal prompts, classifications, or debug metadata. The response must remain useful if the thinker's name is removed.

Safety overrides lens behavior. In urgent or high-risk situations, the host gives necessary protective direction first, avoids diagnosis or false authority, and abandons lens framing if it could delay action.

## Missing references

If a referenced file is unavailable, the host follows the mandatory rules in `SKILL.md`, chooses neutral teaching when uncertain, preserves safety and correctness, and discloses material uncertainty. It must not invent a missing source, quotation, method, belief, or thinker endorsement.

## Optional development toolkit

The Python package is an optional reference implementation, deterministic router, prompt inspector, validator, evaluation helper, and development CLI. It is not required for installing or using the Skill and does not generate answers through a model service.
