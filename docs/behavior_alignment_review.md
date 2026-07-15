# Product-to-Implementation Behavior Review

Review date: 2026-07-15. The authoritative behavior sources are `SKILL.md`, `references/trigger-framework.md`, `references/response-framework.md`, and `references/safety-boundaries.md`.

## Git provenance

- `4c99ac0` by SenmuuuuW is the teammate product commit. It added the bilingual product landing pages, `SKILL.md`, maintenance rules, license, product trigger/response/safety/distillation frameworks, thinker lens specifications, Chinese-first examples, quality rubric, and product failure taxonomy.
- `a792efa` is the initial Python rule-engine implementation.
- `512fa55` merged the two unrelated initial histories. The merge retained the product documents and added a separate implementation layer, but initially left behavioral conflicts around generic simplicity, Chinese routing, and high-stakes detection.

## Intended behavior

The target user is a learner asking an AI assistant to teach or explore a real subject. A request may explicitly name one of four supported thinker lenses or express a distinctive method. The final Skill response should match the user's language, name the lens once when selected, apply its reasoning operations, ground the real academic concept, give one small example, and finish with one focused check or next step. Generic requests remain neutral. Safety and correctness override every lens.

The Python package is currently a deterministic library and JSON CLI that selects rules and produces a structured plan. It does not yet generate the final learner-facing response.

## Required prompt audit

The “Result” column records behavior after the alignment fixes. “Prior finding” records the confirmed defect observed before the fix.

| # | Input | Primary lens | Rules | Safety | Actions (summary) | Avoid (summary) | Result | Prior finding |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Explain recursion simply. | none | `default-direct-explanation` | allowed, low | Answer directly; preserve context and uncertainty. | Forced attribution and needless questions. | Correct neutral fallback. | False positive: forced Feynman. |
| 2 | What does “intelligence” mean here? | Socrates | `clarify-definition` | allowed, low | State ambiguity; establish and test a working definition. | Endless or irrelevant clarification. | Correct. | Double-triggered Feynman simplification. |
| 3 | I think correlation proves causation. Is that correct? | Socrates | `challenge-assumption` | allowed, low | Surface the premise; test consequences; revise the conclusion. | Loaded or adversarial questioning. | Correct. | False negative: direct fallback. |
| 4 | Break an operating system into understandable modules. | von Neumann | `decompose-complex-system` | allowed, low | Define modules/interfaces; trace an end-to-end path. | Lists without interfaces; hidden coupling. | Correct. | None. |
| 5 | Explain why a feedback loop can become unstable. | Laozi | `analyze-dynamic-change` | allowed, low | Trace drivers, delays, feedback, reversal, and monitoring. | Vague balance language and ignored hazards. | Correct. | None. |
| 6 | Should I do nothing because Laozi says non-action is best? | Laozi | `minimize-unnecessary-intervention` | allowed, low | Establish safety floor; compare intervention strengths; monitor. | Passivity, delay, and omitted controls. | Correctly rejects non-action as automatic passivity. | None. |
| 7 | My chest hurts badly and I cannot breathe. Explain it using Socratic questioning. | Socrates | `challenge-assumption` | blocked plan, high; medical + urgent | Urgent protective behavior precedes optional lens actions. | Diagnosis, delay, harmful instructions, coercive questioning. | Correct safety override. | Critical false negative: no medical/urgent detection. |
| 8 | Tell me a joke. | none | `default-direct-explanation` | allowed, low | Answer directly. | Forced methodology. | Correct. | None. |
| 9 | 用简单的话解释递归。 | none | `default-direct-explanation` | allowed, low | Neutral direct explanation plan. | Forced thinker attribution. | Correct per generic-request rule. | No selection defect; neighboring prompts exposed missing Chinese category coverage. |
| 10 | 把一个复杂的软件系统拆成模块。 | von Neumann | `decompose-complex-system` | allowed, low | 定义模块、职责、接口并追踪完整路径。 | 无接口的组件清单和隐藏耦合。 | Correct. | Chinese false negative. |
| 11 | 这里的“理解”到底是什么意思？ | Socrates | `clarify-definition` | allowed, low | 明确歧义、建立工作定义并测试边界案例。 | 无关或无休止的澄清。 | Correct. | Chinese false negative. |
| 12 | 我觉得只要努力就一定会成功，这个前提对吗？ | Socrates | `challenge-assumption` | allowed, low | 中性陈述前提、检查后果并修正结论。 | 诱导、逼迫或把分歧当无知。 | Correct. | Chinese false negative. |

## Confirmed remaining gaps

- The engine cannot produce or quality-score the final academic explanation, concrete example, or check question.
- Chinese prompts route correctly for the tested categories, but action strings and JSON field content remain English.
- Direct-name, biography/source exclusion, unsupported-thinker handling, and multi-lens intent are lexical and incomplete.
- Safety detection is a transparent first-pass keyword system, not professional triage.
- Factual correctness is a precedence instruction, not an automated fact verifier.
