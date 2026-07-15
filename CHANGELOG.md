# Changelog

## Unreleased - Host-executed Skill packaging

- Defined the two-layer runtime contract: a Markdown/YAML Skill executed by the host and an optional offline Python development toolkit.
- Made `SKILL.md` self-sufficient for lens selection, safety, completion, unsupported thinkers, failure prevention, and reference loading.
- Added the runtime manifest, generic host installation guide, deterministic allowlisted bundle builder, checksums, and reproducible ZIP packaging.
- Added host-model evaluation fixtures and a repeatable manual evaluation procedure without making network calls.
- Extended repository validation for runtime links, manifest integrity, lens and version consistency, host cases, absent API configuration, and reproducible builds.
- Repositioned the Python prompt package as an offline inspection aid rather than an external generation handoff.

## Previous unreleased - Python rule engine integration

- Added the typed `mingren_skill` Python package, deterministic rule router, safety precedence, and structured plan engine.
- Added machine-readable trigger and evaluation cases, pytest coverage, repository validation, packaging, and JSON CLIs.
- Preserved the v0.1.0 product specification, bilingual documentation, examples, quality rubric, and research boundaries.
- Aligned generic requests with neutral fallback, added direct teaching-intent and English assumption routing, and added transparent Chinese patterns across existing rule categories.
- Added English and Chinese urgent-medical detection and safety precedence tests.
- Added product-to-implementation requirements traceability with explicit implementation gaps and decisions.
- Added typed PromptContext/PromptPackage models, lightweight language detection, offline prompt previews, and deterministic response validation.
- Added `plan`, `prompt`, and `validate-response` CLI commands while preserving legacy input-as-plan behavior.
- Added seven prompt regression snapshots and behavioral coverage for injection containment, language, safety, questioning, impersonation, and prompt leakage.
- Polished the bilingual landing pages and clarified the specification-first V0.1 and Python-prototype boundary.
- Updated bilingual architecture documentation without adding a model API.

## v0.1.0 - Initial MVP

- Initialized Famous Teacher Skill / 名人教你 Skill.
- Added bilingual README.
- Added main `SKILL.md`.
- Added four thinker lenses: Feynman, von Neumann, Socrates, Laozi.
- Added distillation, trigger, response, and safety frameworks.
- Added Chinese-first examples.
- Added quality rubric and failure taxonomy.
- Added MIT License.
