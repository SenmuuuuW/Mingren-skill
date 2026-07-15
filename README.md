<div align="center">

# 🧠 Famous Teacher Skill

<p><strong>Teach any subject through distilled thinker lenses.</strong></p>
<p><sub>名人教你 Skill · 用名人的思维方式教所有学科。</sub></p>

<p>English &nbsp;|&nbsp; <a href="README.zh-CN.md">中文</a></p>

<p>
  <a href="CHANGELOG.md"><img alt="Stage: v0.1 foundation" src="https://img.shields.io/badge/stage-v0.1%20foundation-0f766e?style=flat-square"></a>
  <a href="SKILL.md"><img alt="Specification first" src="https://img.shields.io/badge/approach-specification%20first-2563eb?style=flat-square"></a>
  <a href="pyproject.toml"><img alt="Python 3.11+ prototype" src="https://img.shields.io/badge/Python-3.11%2B%20prototype-3776AB?style=flat-square&logo=python&logoColor=white"></a>
  <a href="references/thinkers/"><img alt="Four thinker lenses" src="https://img.shields.io/badge/thinker%20lenses-4-7c3aed?style=flat-square"></a>
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-2ea44f?style=flat-square"></a>
</p>

</div>

> [!IMPORTANT]
> **Current stage: V0.1 foundation.** Teaching behavior, boundaries, examples, and evaluation criteria remain specification-first and are defined in Markdown. The repository also contains an early deterministic Python implementation for routing, model-ready prompt packages, and response checks. It is not yet a complete answer-generation product.

## What this project is

Famous Teacher Skill is a cross-subject learning project that turns documented reasoning and teaching methods into explicit, reviewable thinker lenses. A lens changes how an explanation is organized while the real academic concept remains authoritative.

This is learning-first, not celebrity simulation: no identity impersonation, fake quotations, or theatrical roleplay.

## Why it is different

| Generic AI tutor | Famous Teacher Skill |
| --- | --- |
| Explains in a general style | Organizes teaching through a selected thinker lens |
| May imitate personality or tone | Distills reasoning patterns and teaching moves |
| Often jumps directly to an answer | Uses a lens-specific path toward understanding |
| Can make style the product | Keeps correctness and learning outcomes primary |

## The four V0.1 lenses

| Lens | Best suited to | Teaching pattern |
| --- | --- | --- |
| Feynman | Intuition, STEM foundations, formulas | Plain language, analogy, concrete examples, explain-back checks |
| von Neumann | CS, AI, systems, algorithms | Inputs, parameters, state, rules, outputs, modular structure |
| Socrates | Definitions, proof, reasoning | Questions, assumptions, counterexamples, guided discovery |
| Laozi | Abstraction, change, relationships | Contrast, reversal, balance, relation, change |

V0.1 intentionally stops at these four lenses. Each specification records source basis, strengths, weak contexts, response structure, and failure risks.

## Try the intended interaction

```text
Teach me gradient descent through the Feynman lens.
Question me about this proof in a Socratic way. Do not reveal the answer yet.
Break operating-system process scheduling into inputs, state, rules, and outputs.
Use the Laozi lens to open up calculus, then return to formal mathematics.
```

Responses following the Skill specification name the lens once, teach the real concept, ground it with a small example, and end with one focused check or next step.

## Designed response flow

```text
User question
    ↓
Identify topic and learning intent
    ↓
Detect or clarify the thinker lens
    ↓
Apply the distilled teaching pattern
    ↓
Reconnect to the academic concept
    ↓
Give one small example
    ↓
Ask one focused check question
```

Direct lens requests take priority. Distinctive method requests may suggest a lens. Subject alone never silently selects one, and generic requests such as “explain simply” remain neutral unless lens intent is otherwise clear.

## Project layers

| Layer | Role | Key paths |
| --- | --- | --- |
| Product specification | Authoritative Skill behavior and quality boundaries | [`SKILL.md`](SKILL.md), [`references/`](references/) |
| Thinker research | Source-bounded definitions for the four lenses | [`references/thinkers/`](references/thinkers/) |
| Examples and evaluation | Calibrated responses, cases, and failure checks | [`examples/`](examples/), [`evals/`](evals/) |
| Python prototype | Routing, prompt packaging, and deterministic response checks | [`src/mingren_skill/`](src/mingren_skill/), [`tests/`](tests/) |

The product Markdown remains authoritative. When implementation and specification diverge, update the Python rules, evaluation cases, and tests to match the specification.

## Python implementation prototype

Python is the current implementation direction. The package turns the product rules into four inspectable stages:

```text
User request
    ↓
Language detection + rule routing + safety evaluation
    ↓
EngineResult (structured teaching plan)
    ↓
PromptBuilder → PromptPackage (system/developer/user prompts)
    ↓
External model provider chosen by the integrator (not included)
    ↓
Candidate learner-facing answer
    ↓
ResponseValidator → issues and required revisions
```

The prototype does **not** generate an answer by itself, fact-check claims, call an external model, expose a hosted API, or represent a finished teaching application. Safety and response checks are deterministic first versions, not comprehensive professional classification. Substantial implementation work remains.

Routing covers tested English and Chinese categories, including explicit lens requests and neutral fallback for generic simplicity requests. Pattern matching remains lexical rather than semantic, so aliases and paraphrases are not exhaustive.

Requirements: Python 3.11 or newer, with PyYAML at runtime and pytest for development checks.

```bash
python -m pip install -e ".[dev]"
python scripts/validate.py
pytest
```

The CLI exposes three explicit commands:

```bash
mingren-skill plan "Explain recursion simply"
mingren-skill prompt "What exactly does intelligence mean here?"
mingren-skill validate-response "My chest hurts and I cannot breathe" --response "Wait and see."
```

`plan` prints an `EngineResult`; `prompt` prints a provider-independent `PromptPackage`; `validate-response` reports deterministic issues and required revisions. For backward compatibility, `mingren-skill "input"` and `python -m mingren_skill "input"` still behave as `plan`.

No provider SDK, network call, streaming layer, or API credential handling is included.

## Documentation

- [`SKILL.md`](SKILL.md): central behavior specification and response workflow
- [`references/distillation-framework.md`](references/distillation-framework.md): standard for distilling a thinker lens
- [`references/trigger-framework.md`](references/trigger-framework.md): trigger precedence, ambiguity, and non-trigger rules
- [`references/response-framework.md`](references/response-framework.md): default teaching-response structure
- [`references/safety-boundaries.md`](references/safety-boundaries.md): identity, source, correctness, and high-stakes limits
- [`references/thinkers/`](references/thinkers/): the four detailed lens specifications
- [`references/trigger_rules.yaml`](references/trigger_rules.yaml): executable rules, priorities, exits, and source links
- [`examples/`](examples/): Chinese-first calibrated examples and a bad-versus-good comparison
- [`evals/`](evals/): human-facing quality checks and machine-oriented cases
- [`evals/prompt_snapshots/`](evals/prompt_snapshots/): representative prompt regression expectations
- [`docs/requirements_traceability.md`](docs/requirements_traceability.md): product requirements mapped to behavior, tests, and gaps
- [`docs/behavior_alignment_review.md`](docs/behavior_alignment_review.md): audited prompt behavior and confirmed limitations
- [`AGENTS.md`](AGENTS.md): coding-agent contribution requirements
- [`MAINTENANCE.md`](MAINTENANCE.md): scope and maintenance rules
- [`CHANGELOG.md`](CHANGELOG.md): release history

## Boundaries

- No literal impersonation or “I am Feynman” claims
- No fabricated quotations, citations, or historical views
- No style-over-correctness answers or vague mysticism
- No living- or private-person imitation in V0.1
- No hidden memory, database, RAG, hosted API, or backend service
- No additional thinker lenses in V0.1

See the full [safety and quality boundaries](references/safety-boundaries.md).

## Direction

The near-term goal is to keep the Skill specification, source boundaries, evaluation cases, prompt snapshots, and Python prototype aligned. Later implementation work can connect a model provider and build a fuller learning experience without weakening correctness, attribution, or the four-lens scope.

## License

Released under the [MIT License](LICENSE).
