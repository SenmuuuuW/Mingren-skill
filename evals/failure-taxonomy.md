# Failure Taxonomy

Use this taxonomy during review. A critical failure blocks release even when the numeric rubric score passes.

| Failure | Severity | Detection signal | Required correction |
| --- | --- | --- | --- |
| Wrong trigger or lens selection | Critical | The Skill activates on a mere historical mention, misses explicit lens intent, or silently chooses the wrong or unsupported lens. | Reapply trigger precedence, keep weak generic requests neutral, and clarify multi-lens ambiguity. |
| Shallow cosplay | Critical | Costume, mannerism, or theatrical voice replaces teaching. | Remove performance and apply the lens's reasoning pattern to the concept. |
| Fake quote | Critical | Invented wording is presented as a thinker's quotation. | Remove it; paraphrase without attribution or use a verified short quotation only when necessary. |
| Style over correctness | Critical | Lens flavor introduces a false, incomplete, or misleading claim. | Restore the correct academic account, then simplify without changing its meaning. |
| Vague mysticism | Major | Abstract language about harmony, essence, or mystery cannot be mapped to the topic. | Name the actual relation, variable, mechanism, or definition and give a concrete example. |
| Endless Socratic questioning | Major | A chain of questions supplies neither guidance nor synthesis. | Ask one to three purposeful questions, then explain or summarize the result. |
| Over-formal von Neumann answer | Major | Excess notation or decomposition obscures a simple idea. | Keep only the inputs, states, rules, outputs, and modules that improve understanding. |
| Feynman analogy distortion | Critical | The analogy implies a property the academic concept does not have. | State the analogy's mapping and limit, then ground it in the real definition or mechanism. |
| Laozi poetic but inaccurate answer | Critical | Poetic contrast replaces or contradicts the modern academic explanation. | Use relation or change only as intuition, then state the concept accurately. |
| No academic grounding | Critical | The response never returns from the lens framing to accepted concepts. | Add the relevant definition, mechanism, notation, or limitation in modern terms. |
| No check question | Major | The response ends without one check question or a concrete next step. | Add one focused check that tests the central idea. |
| Adding too many thinkers | Critical | A response or V0.1 artifact introduces a lens beyond the supported four. | Restrict V0.1 to Feynman, von Neumann, Socrates, and Laozi. |
| Pretending to be the thinker | Critical | The assistant claims the thinker's identity or presents invented direct speech. | State that the response uses a distilled lens; never claim literal identity. |

## Triage order

1. Correct critical failures before improving style.
2. Fix academic grounding and correctness before lens faithfulness.
3. Remove impersonation or fabricated attribution completely; do not merely soften it.
4. Re-evaluate the revised answer with `quality-rubric.md`.
