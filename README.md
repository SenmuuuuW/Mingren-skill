<div align="center">

# 🧠 Famous Teacher Skill

**Teach any subject through distilled thinker lenses.**

English | [中文](README.zh-CN.md)

![License](https://img.shields.io/badge/license-MIT-2ea44f)
![Markdown only](https://img.shields.io/badge/format-Markdown--only-111111)
![AI Skill](https://img.shields.io/badge/type-AI%20Skill-2563eb)
![Distilled lenses](https://img.shields.io/badge/method-distilled%20thinker%20lenses-d97706)
![MVP](https://img.shields.io/badge/MVP-4%20thinkers-7c3aed)

</div>

## ✨ What is this?

Famous Teacher Skill is a cross-subject AI learning Skill that explains real academic ideas through distilled thinker lenses.

It lets a learner ask:

- “Feynman, teach me gradient descent.”
- “Socrates, question me through this proof.”
- “Laozi, teach me calculus.”
- “Explain neural networks through von Neumann-style structure.”

The Skill does not pretend to be those people. It distills useful reasoning patterns, teaching moves, conceptual frames, and questioning methods, then reconnects every answer to the actual subject.

> The lens shapes the path to understanding. It does not replace academic truth.

## 🧩 Why this is different

| Normal tutor | Famous Teacher Skill |
| --- | --- |
| Explains in a generic style | Explains through a selected thinker lens |
| May copy personality or tone | Distills reasoning and teaching method |
| Often gives the answer directly | Guides understanding with lens-specific moves |
| Can become roleplay-first | Remains learning-first |
| Treats style as decoration | Connects style to a repeatable reasoning structure |

This is not a celebrity chatbot, persona simulator, or quotation generator.

## 🧠 First four lenses

Version 0.1 deliberately supports only four lenses:

| Lens | Best for | Teaching pattern |
| --- | --- | --- |
| Feynman | Intuition, STEM foundations, formulas | Plain language, analogy, concrete examples, simple checks |
| von Neumann | CS, AI, systems, algorithms | Inputs, outputs, states, rules, models, modular structure |
| Socrates | Definitions, proof, reasoning | Questions, assumptions, counterexamples, guided discovery |
| Laozi | Abstraction, change, relationships | Contrast, reversal, balance, relation, change |

Each lens has explicit strengths, weak contexts, source boundaries, response steps, and failure risks.

## 🚀 Quick examples

```text
用费曼方式解释梯度下降
老子教我微积分
让苏格拉底追问我这道证明题
用冯诺伊曼方式拆解操作系统进程
```

An answer normally names the lens once, teaches the real concept, gives a small example, and ends with one useful check question or next step.

## 🔍 How it works

```text
User question
    ↓
Detect topic and learning intent
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

Direct thinker names take priority. Distinctive method requests can suggest a lens. Subject alone never silently selects one; an ambiguous request receives neutral teaching or one focused clarification.

## 🧭 Design principles

- **Correctness first.** Lens flavor never overrides accepted definitions, evidence, or notation.
- **Method over mannerism.** The response uses intellectual moves, not costume language.
- **Small and inspectable.** One good example is better than a pile of vague analogies.
- **Diagnosis before excess.** Address the learner's visible obstacle instead of dumping a full course.
- **One next step.** End with a check that reveals whether the idea transferred.
- **Explicit limits.** Mark analogy boundaries and historical uncertainty.

## 📚 Documentation map

- [`README.md`](README.md) — English project landing page
- [`README.zh-CN.md`](README.zh-CN.md) — Chinese project landing page
- [`SKILL.md`](SKILL.md) — central behavior specification and response workflow
- [`references/distillation-framework.md`](references/distillation-framework.md) — standard for turning a thinker into a teaching lens
- [`references/trigger-framework.md`](references/trigger-framework.md) — direct, stylistic, intent, and ambiguity rules
- [`references/response-framework.md`](references/response-framework.md) — the default six-move answer structure
- [`references/safety-boundaries.md`](references/safety-boundaries.md) — identity, source, correctness, and high-stakes limits
- [`references/thinkers/`](references/thinkers/) — the four detailed lens specifications
- [`examples/`](examples/) — Chinese-first calibrated responses and a bad-versus-good comparison
- [`evals/`](evals/) — quality rubric and failure taxonomy
- [`MAINTENANCE.md`](MAINTENANCE.md) — scope and contribution rules
- [`CHANGELOG.md`](CHANGELOG.md) — release history
- [`LICENSE`](LICENSE) — MIT license terms

## 🗂️ Repository structure

```text
Mingren-skill/
├── SKILL.md
├── README.md
├── README.zh-CN.md
├── CHANGELOG.md
├── MAINTENANCE.md
├── LICENSE
├── references/
│   ├── distillation-framework.md
│   ├── trigger-framework.md
│   ├── response-framework.md
│   ├── safety-boundaries.md
│   └── thinkers/
├── examples/
└── evals/
```

Version 0.1's authoritative product behavior remains defined in Markdown. The repository now also includes a small Python rule engine that turns explicit task signals into inspectable structured plans. It has no website, API service, backend, database, hidden memory, or retrieval system.

## 🛡️ Boundaries

- No literal impersonation or “I am Feynman” claims
- No fabricated quotations, citations, or historical views
- No long copyrighted quotations
- No style-over-correctness answers
- No vague mystical substitute for academic explanation
- No living- or private-person imitation in V0.1
- No database, RAG, backend, or celebrity marketplace
- No thinkers beyond the first four in V0.1

See the full [safety and quality boundaries](references/safety-boundaries.md).

## 🔖 Status

This repository contains the focused `v0.1.0` MVP. Quality and behavioral boundaries take priority over lens count.

## 🐍 Python rule engine

The `src/mingren_skill/` package is a deterministic implementation layer for the product rules. It validates trigger metadata, applies transparent keyword and pattern routing, gives safety and factual correctness precedence, resolves compatible lenses, and returns a structured plan rather than a roleplayed answer. It does not call an external LLM and is not a complete professional safety classifier.

Install and verify it with Python 3.11 or newer:

```sh
python -m pip install -e ".[dev]"
python scripts/validate.py
pytest
```

Both CLI forms print a JSON `EngineResult`:

```sh
python -m mingren_skill "Explain recursion simply"
mingren-skill "Break this system into modules"
```

Technical artifacts are intentionally separate from the authoritative teaching specification:

- `references/trigger_rules.yaml` — executable rules, priorities, exits, and source links
- `references/distillation_framework.md` — implementation evidence metadata and acceptance rules
- `references/safety_boundaries.md` — implementation-specific hard boundaries
- `evals/cases.yaml` and `evals/failure_taxonomy.md` — machine-oriented cases and detailed failure tests
- `tests/` — loader, router, engine, safety, and validator behavior tests
- `AGENTS.md` — coding-agent contribution requirements

When product Markdown and implementation behavior diverge, the product definitions in `SKILL.md` and the hyphenated framework documents are authoritative; update code, evaluation cases, and tests together.

## 📄 License

Released under the [MIT License](LICENSE).
