# John von Neumann

## Scope

This file extracts structural methods visible in von Neumann's documented technical work. It avoids turning anecdotes about speed or memory into a fictional universal thinking style.

## Core Lens

Represent a problem so its essential objects, constraints, and transformations are explicit; decompose systems by interfaces; and reuse structure only when the mapping preserves relevant assumptions.

## Reliable Sources

| Source | Source type | Evidence grade | Relevance | Notes or limitations |
| --- | --- | --- | --- | --- |
| *Theory of Games and Economic Behavior* (with Oskar Morgenstern) | Authored technical work | A | Formal representation of strategic interaction. | Coauthored and domain-specific. |
| *First Draft of a Report on the EDVAC* | Authored technical report | A | Functional decomposition of a computing system. | Draft and collaborative historical context; attribution requires care. |
| *The Computer and the Brain* | Authored lectures/book | A | Comparison of computational and biological organization. | Unfinished and historically bounded science. |

## How They Explain

### Change representation to expose operations

- **Source evidence:** Formal representations in *Theory of Games and Economic Behavior* and system description in the EDVAC report.
- **Original context:** Strategic choice and computer architecture.
- **Method summary:** Restate prose as objects, states, constraints, payoffs, flows, or transformations.
- **Underlying purpose:** Make dependencies and possible operations explicit.
- **Applicable situations:** Multi-actor decisions, algorithms, stateful systems, ambiguous process descriptions.
- **Non-applicable situations:** Qualitative contexts where quantification would fabricate precision.
- **Executable rule:** Choose the smallest representation that preserves the decision-relevant relations; map every symbol back to the case.
- **Correct example:** Convert a deployment story into states, transitions, rollback conditions, and owners.
- **Failure example:** Add equations to an underspecified human conflict and call it objective.
- **Confidence:** medium

## How They Ask Questions

### Ask which structure is invariant

- **Source evidence:** Cross-domain structural comparison in *The Computer and the Brain*; broader personal-method claim needs verification.
- **Original context:** Comparing kinds of information processing and component behavior.
- **Method summary:** Identify which relations survive a change of notation, implementation, or domain.
- **Underlying purpose:** Separate essential structure from accidental detail.
- **Applicable situations:** Architecture comparison, algorithm transfer, refactoring, analogies.
- **Non-applicable situations:** When domain-specific mechanisms determine the outcome.
- **Executable rule:** Name the proposed mapping, list preserved constraints, and list at least one non-preserved property.
- **Correct example:** Map both a workflow and state machine by transitions while noting human discretion has no exact machine equivalent.
- **Failure example:** Treat brains and computers as identical because both process information.
- **Confidence:** provisional

TODO-SOURCE:
- claim: Seeking invariants across representations was a recurring general-purpose personal method for von Neumann.
- preferred source type: multiple primary works plus reliable first-hand account
- verification needed: evidence beyond inference from selected technical publications
- current confidence: provisional

## How They Simplify or Structure Complex Problems

### Decompose by function and interface

- **Source evidence:** Functional organization in *First Draft of a Report on the EDVAC*.
- **Original context:** Description of components in a stored-program computing system.
- **Method summary:** Divide a system into responsibilities, inputs, outputs, state, and coordination constraints.
- **Underlying purpose:** Localize reasoning while retaining system-level interactions.
- **Applicable situations:** Software, processes, organizations, and other interface-bearing systems.
- **Non-applicable situations:** Tightly coupled phenomena where the proposed boundaries erase dominant interactions.
- **Executable rule:** Name components and contracts; trace one end-to-end path; revise boundaries if cross-coupling dominates.
- **Correct example:** Separate ingestion, validation, storage, and serving, then trace error propagation.
- **Failure example:** Produce a component list without interfaces or an end-to-end check.
- **Confidence:** high

### Formalize only decision-relevant structure

- **Source evidence:** Modeling choices in *Theory of Games and Economic Behavior*.
- **Original context:** Formal treatment of games and economic behavior.
- **Method summary:** Specify actors, available actions, information, outcomes, and objective assumptions.
- **Underlying purpose:** Make a complex interaction analyzable and assumptions contestable.
- **Applicable situations:** Strategic or optimization problems with sufficiently specified elements.
- **Non-applicable situations:** Values disputes or poorly observed systems where the formal inputs are speculative.
- **Executable rule:** Declare objects and assumptions; solve or compare within the model; validate conclusions outside it.
- **Correct example:** Model scheduling choices with capacity and lateness costs, then sensitivity-test uncertain costs.
- **Failure example:** Optimize a precise score that omits safety and fairness constraints.
- **Confidence:** high

## Recurring Principles

- Representation choice controls which operations and comparisons are visible (medium).
- Decomposition is incomplete without interfaces and an end-to-end trace (high within architecture context).
- Structural analogy requires an explicit mapping and stated breakpoints (provisional as a general lens).

## Trigger Candidates

### Complex system lacks inspectable structure

- **Trigger condition:** Many interacting components, unclear dependencies, or prose obscures states and constraints.
- **Primary lens:** von Neumann
- **Optional secondary lens:** Laozi for feedback and second-order effects
- **Actions:** choose representation; define components and interfaces; trace a path; identify invariants and broken analogy points.
- **Avoid:** formalism for display, fabricated quantities, detached component lists.
- **Exit condition:** The representation answers the target question and maps cleanly back to reality.
- **Confidence:** medium

## Misconceptions to Avoid

- Anecdotes about exceptional calculation or memory are not executable methods.
- Formalization does not make uncertain assumptions true.
- “Von Neumann architecture” shorthand does not settle complex historical attribution.

## Open Research Questions

- Find first-hand evidence about how von Neumann selected representations in collaborative work.
- Distinguish recurring personal practice from methods inferred from finished publications.
- Audit historical attribution around the EDVAC report before making broader claims.
