# Maintenance Rules

These rules keep Famous Teacher Skill / 名人教你 Skill focused, accurate, and maintainable.

## V0.1 scope

- Support exactly four thinker lenses: Feynman, von Neumann, Socrates, and Laozi.
- Do not add a new thinker without a clear learning need, a completed distillation file, representative examples, and rubric-based evaluation.
- Do not add living or private people in early versions.
- Keep the thinker-lens teaching contract Markdown-first. Python is an auxiliary implementation and validation layer; it must not redefine behavior established by `SKILL.md` and the product frameworks.

## Owner-approved offline Python scope

This is a narrow, owner-approved refinement of the original docs-first policy, not open-ended permission to add code.

Small offline Python tools may be added only when they directly support bundle construction, manifest validation, evaluation-case validation, link or consistency checking, local release verification, or the existing deterministic routing and inspection prototype.

These tools must:

- remain optional for reading and applying the Markdown specifications in a compatible host;
- avoid model-provider APIs, API credentials, and network dependencies during normal validation;
- avoid backend services, databases, vector stores, and RAG;
- have a clear, documented purpose;
- include tests when they affect packaging, validation, or deterministic routing;
- preserve the thinker-lens behavior contract rather than redefining it; and
- remain small enough to review as auxiliary local tooling.

The following remain disallowed without explicit owner approval:

- web applications or course platforms;
- production APIs or persistent backend services;
- databases, vector stores, or RAG;
- user accounts or hidden memory;
- provider-specific runtime integrations;
- large dependency frameworks;
- automatic scraping; and
- lens marketplaces.

## Content rules

- Distill a thinking and teaching method, not personality, mannerisms, or a simulated identity.
- Academic correctness beats stylistic fidelity.
- Do not fabricate quotations, citations, or claims about what a thinker would literally say.
- Do not use long quotations. Prefer concise paraphrase from stable public knowledge.
- Keep both READMEs concise, aligned, and mutually linked; update English and Chinese positioning together.
- Keep examples small, academically correct, Chinese-first where appropriate, and complete with one check question or next step.
- Use `references/distillation-framework.md` for every future thinker proposal.

## Change checklist

Before merging a content change:

1. Confirm it stays within the approved lens scope.
2. Check that the lens affects reasoning structure rather than surface tone.
3. Verify all academic claims, examples, notation, and attributions.
4. Score affected examples with `evals/quality-rubric.md` and resolve failures in `evals/failure-taxonomy.md`.
5. Keep `SKILL.md`, the bilingual READMEs, examples, and reference files consistent.
6. Update `CHANGELOG.md` for user-visible behavior or scope changes.

## Adding a thinker in a future version

A proposal must explain the unmet learning need, why an existing lens cannot meet it, suitable and weak subjects, failure risks, triggers, and response structure. It must also include at least one good example and one failure case. Adding a famous name for novelty or marketplace growth is not sufficient.
