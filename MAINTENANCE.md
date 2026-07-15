# Maintenance Rules

These rules keep Famous Teacher Skill / 名人教你 Skill focused, accurate, and maintainable.

## V0.1 scope

- Support exactly four thinker lenses: Feynman, von Neumann, Socrates, and Laozi.
- Do not add a new thinker without a clear learning need, a completed distillation file, representative examples, and rubric-based evaluation.
- Do not add living or private people in early versions.
- Keep the product Markdown-first. Optional offline build, routing, validation, and evaluation scripts are allowed for maintainers, but they must never become a host runtime dependency.
- Do not add model providers, API credentials, HTTP generation, backends, databases, or RAG. The host that loads the Skill generates the answer.

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
