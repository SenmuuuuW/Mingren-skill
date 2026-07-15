# Research Distillation Framework

## Research Goal

Convert source-grounded reasoning and explanation methods into observable Skill behavior. The output is a set of bounded actions with triggers, exits, evidence, and failure cases—not biography, roleplay, quotations, or imitation of personality.

## What Should Not Be Collected

Exclude decorative anecdotes, personality traits, writing tics, decontextualized quotations, generic biography, claims that cannot affect behavior, and material included only because it is famous. Famous quotes must not be used unless traced to a reliable source.

## Source Hierarchy

| Grade | Evidence |
| --- | --- |
| A | Primary material by the thinker: authored books, lectures, letters, recorded talks, or directly documented work. |
| B | Reliable first-hand accounts: interviews, students, colleagues, contemporaries, or well-documented teaching records. |
| C | Serious biographies, peer-reviewed research, university publications, or high-quality scholarly commentary. |
| D | Secondary internet summaries, unsourced articles, quote websites, social posts, or popular retellings. |

Core rules should preferably rely on A or B sources. Grade D can identify a research question but cannot independently support a core rule.

## Evidence Grading

Grade the source, not the attractiveness of the claim. Record provenance, whether the material is direct or retrospective, the original domain, translation or editorial limitations, and whether independent sources repeat the pattern. A precise citation does not cure weak evidence.

Allowed confidence values are `high`, `medium`, `low`, and `provisional`. Confidence reflects evidence quality, repetition, contextual fit, and inference distance.

## Method Extraction Process

1. Identify a recurring, behaviorally relevant passage or documented practice.
2. Record its original context and domain.
3. Separate the observed practice from the proposed general method.
4. State the purpose the practice served.
5. Find a correct case, a boundary case, and a failure case.
6. Check for repeated evidence and competing interpretations.
7. Complete all metadata below; otherwise mark the claim `TODO-SOURCE` and provisional.

Every extracted method contains:

1. source
2. source type
3. evidence grade
4. original context
5. method summary
6. underlying purpose
7. applicable situations
8. non-applicable situations
9. executable behavior
10. correct example
11. failure example
12. confidence level

## Rule Conversion Process

Translate a method into a rule only when its behavior is observable and testable:

1. Express user/task signals as trigger conditions.
2. Select one primary lens and only compatible secondary lenses.
3. Turn the method into ordered actions.
4. List prohibited shortcuts and characteristic failures under `avoid`.
5. Define a measurable exit condition.
6. Assign an explicit priority and attach safety notes, confidence, and resolvable source references.
7. Add at least one success case and one failure case in the thinker research or evaluation taxonomy.

Factual correctness and safety take priority. A lens is a temporary intervention, not a voice or identity.

## Uncertainty Handling

Do not fill evidentiary gaps from memory. Use:

```text
TODO-SOURCE:
- claim:
- preferred source type:
- verification needed:
- current confidence:
```

Keep provisional methods out of high-stakes decisions and disclose material uncertainty. Downgrade confidence when translation, attribution, context, or generalization is unresolved.

## Conflict Handling

Safety and factual correctness override every lens. Prefer direct explanation when questioning adds friction. Combine lenses only if their actions are compatible; sequence them when ordering resolves the conflict. If one lens calls for simplification while another requires precision, establish intuition first and restore necessary terminology before exiting. If no compatible sequence exists, select the lens closest to the user's explicit goal and record the rejected action.

## Acceptance Criteria

A method is accepted when it has complete metadata, traceable evidence or an explicit research placeholder, bounded applicability, an executable behavior, correct and failure examples, an exit condition at rule level, and no conflict with safety boundaries. A core rule normally requires A/B evidence or clearly disclosed provisional status.

## Rejection Criteria

Reject or defer material that is chiefly biography or style; relies on an untraceable quote; invents bibliographic precision; cannot produce observable behavior; lacks boundaries; universalizes a domain-specific practice; conflicts with established facts or professional standards; duplicates an existing rule; or remains too vague to test.
