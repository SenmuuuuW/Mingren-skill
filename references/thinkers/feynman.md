# Richard Feynman

## Scope

This file extracts bounded explanation and checking methods associated with documented Feynman work. It is not a biography, a voice guide, or a license to attribute the popular “explain it to a child” formula to him.

## Core Lens

Replace labels with mechanisms, anchor abstractions in cases, and test whether an explanation can distinguish outcomes. Simplicity is a diagnostic stage; necessary precision returns before completion.

## Reliable Sources

| Source | Source type | Evidence grade | Relevance | Notes or limitations |
| --- | --- | --- | --- | --- |
| *The Feynman Lectures on Physics* | Authored lectures | A | Explanations connect formalism, mechanisms, and examples. | Edited lecture record; methods observed in physics may not generalize unchanged. |
| “Cargo Cult Science” | Published address by thinker | A | Emphasizes tests that could expose error and full reporting. | Research-integrity context, not a universal teaching procedure. |
| *Surely You're Joking, Mr. Feynman!* | Recollected autobiographical stories | A/B | Contains examples contrasting names with understanding. | Edited recollection; anecdotes require corroboration before becoming core rules. |

## How They Explain

### Replace a label with a mechanism

- **Source evidence:** *The Feynman Lectures on Physics*; relevant naming-versus-knowing anecdotes in *Surely You're Joking, Mr. Feynman!*.
- **Original context:** Explaining physical phenomena and recounting science learning.
- **Method summary:** Restate unfamiliar terms as entities, relations, and changes, then reconnect the formal name.
- **Underlying purpose:** Prevent terminology from concealing a missing causal or operational model.
- **Applicable situations:** Novice explanations, jargon-heavy text, definitions that merely repeat labels.
- **Non-applicable situations:** When the user already has the mechanism or exact terminology is immediately safety-critical.
- **Executable rule:** Identify undefined terms; explain one in ordinary language with a concrete case; restore the technical term and its constraint.
- **Correct example:** Explain “latency” as elapsed waiting time for one request, measure a request, then distinguish it from throughput.
- **Failure example:** Replace every technical term with a loose metaphor and never restore distinctions.
- **Confidence:** medium

### Make the explanation discriminate

- **Source evidence:** “Cargo Cult Science” and problem-solving practice visible in *The Feynman Lectures on Physics*.
- **Original context:** Scientific testing and physics reasoning.
- **Method summary:** Ask what observation, prediction, or contrasting case would differ if the explanation were right.
- **Underlying purpose:** Separate explanatory content from plausible-sounding restatement.
- **Applicable situations:** Causal claims, conceptual checks, competing explanations.
- **Non-applicable situations:** Purely conventional definitions or requests needing only a direct factual lookup.
- **Executable rule:** Give two nearby cases and identify the outcome the explanation predicts differently.
- **Correct example:** Contrast a CPU-bound and I/O-bound task to test a performance diagnosis.
- **Failure example:** Demand an experiment for a definition fixed by specification.
- **Confidence:** medium

## How They Ask Questions

### Locate the first unsupported step

- **Source evidence:** Problem-development pattern in *The Feynman Lectures on Physics*; stronger pedagogical attribution remains to be verified.
- **Original context:** Stepwise physical derivations.
- **Method summary:** Find the earliest term or inference the learner cannot unpack.
- **Underlying purpose:** Repair the actual prerequisite rather than repeat the final answer.
- **Applicable situations:** Learner says they understand but cannot reproduce or apply an explanation.
- **Non-applicable situations:** Urgent tasks or users requesting a concise answer without tutoring.
- **Executable rule:** Ask for one step in the user's own words or one prediction; teach the first missing prerequisite directly.
- **Correct example:** Ask what a derivative measures before redoing the chain rule.
- **Failure example:** Turn the interaction into a memory quiz.
- **Confidence:** provisional

TODO-SOURCE:
- claim: Feynman repeatedly used learner restatement as a deliberate teaching protocol.
- preferred source type: recorded lecture or reliable first-hand teaching record
- verification needed: direct, repeated evidence beyond popular “Feynman technique” summaries
- current confidence: provisional

## How They Simplify or Structure Complex Problems

### Rebuild from stable primitives

- **Source evidence:** Expository progression in *The Feynman Lectures on Physics*.
- **Original context:** Developing physical models from established concepts and mathematical relations.
- **Method summary:** Start with known entities and relations, add one dependency at a time, and check each step.
- **Underlying purpose:** Make hidden assumptions and prerequisite gaps observable.
- **Applicable situations:** Mechanistic explanations and multi-step derivations.
- **Non-applicable situations:** Domains where “first principles” are disputed or empirical constraints dominate deduction.
- **Executable rule:** List primitives and assumptions; derive one intermediate result; verify it against a case.
- **Correct example:** Build queue waiting time from arrival rate, service rate, and capacity assumptions.
- **Failure example:** Declare personal intuitions to be first principles.
- **Confidence:** medium

## Recurring Principles

- A name is not yet a mechanism (medium).
- An explanation should support a check or distinction (medium).
- Simplification must not discard constraints required for correctness (supported by the wider technical record; medium).

## Trigger Candidates

### Jargon masks understanding

- **Trigger condition:** The explanation repeats undefined labels or the user cannot apply it to a nearby case.
- **Primary lens:** Feynman
- **Optional secondary lens:** Socrates for one clarifying question
- **Actions:** stop adding concepts; unpack the first term; give a concrete case; test a distinction; restore terminology.
- **Avoid:** childish tone, permanent loss of precision, attribution of the popular child-explanation slogan.
- **Exit condition:** The user can state the mechanism or distinguish the test cases with correct terms.
- **Confidence:** medium

## Misconceptions to Avoid

- “Explain everything to a child” is not an adequately sourced universal rule.
- Plain language alone does not prove understanding.
- First-principles reasoning does not override empirical evidence or domain standards.

## Open Research Questions

- Verify direct evidence for the modern four-step “Feynman technique.”
- Separate Feynman's documented teaching practice from later productivity summaries.
- Determine how consistently prediction checks were used outside physics and research integrity.
