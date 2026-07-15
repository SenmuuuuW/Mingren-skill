# Failure Taxonomy

Each case is evaluated on observable behavior, not the presence of a thinker name. Examples use `Input → bad output` followed by corrected behavior.

## F01 Surface imitation

- **Definition:** Copies verbal mannerisms without applying a reasoning method.
- **Detection signal:** Catchphrases or theatrical voice; no changed reasoning step.
- **Bad input/output example:** “Explain caching.” → “Imagine I am Feynman…” followed by the same jargon.
- **Why it fails:** Style does not expose the mechanism.
- **Corrected behavior:** Define cache, show one request with/without it, then restore hit/miss terminology.
- **Suggested automated or manual test:** Compare outputs with thinker names removed; required actions must remain visible.
- **Severity:** medium
- **Related thinker lenses:** all

## F02 Fabricated source or quote

- **Definition:** Invents or misattributes wording, citation details, or evidence.
- **Detection signal:** Unresolvable quote, URL, title, page, or confident source claim.
- **Bad input/output example:** “Did Laozi say this?” → Supplies an unsourced sentence in quotation marks.
- **Why it fails:** Creates false authority and corrupts research lineage.
- **Corrected behavior:** State that attribution is unverified; add `TODO-SOURCE` with verification needs.
- **Suggested automated or manual test:** Resolve every source reference and manually verify quoted wording.
- **Severity:** critical
- **Related thinker lenses:** all

## F03 Harmful oversimplification

- **Definition:** Simplification removes a condition needed for safe or correct use.
- **Detection signal:** Missing units, exceptions, contraindications, threat conditions, or formal distinction.
- **Bad input/output example:** “Simplify medication dosing.” → Gives a single dose without patient-specific constraints.
- **Why it fails:** Ease of reading overrides correctness and safety.
- **Corrected behavior:** Give plain-language intuition while retaining clinical variables and qualified guidance.
- **Suggested automated or manual test:** Domain expert identifies whether all decision-critical constraints remain.
- **Severity:** critical
- **Related thinker lenses:** Feynman

## F04 Lens not visible in behavior

- **Definition:** Names a lens but performs none of its executable actions.
- **Detection signal:** Attribution appears; output is unchanged generic advice.
- **Bad input/output example:** “Use Socratic analysis.” → “Socrates valued questions; consider the issue.”
- **Why it fails:** The lens is cosmetic and untestable.
- **Corrected behavior:** State one assumption, test its consequence, and revise the claim.
- **Suggested automated or manual test:** Match output steps to the selected rule's `actions`.
- **Severity:** medium
- **Related thinker lenses:** all

## F05 Lens too visible / roleplay

- **Definition:** Persona performance displaces the user's task.
- **Detection signal:** First-person thinker claims, archaic voice, repeated name-dropping.
- **Bad input/output example:** “Review this design.” → “I, Socrates, shall interrogate thee.”
- **Why it fails:** It impersonates and adds friction.
- **Corrected behavior:** Review definitions and assumptions directly without persona language.
- **Suggested automated or manual test:** Flag first-person identity claims and unnecessary thinker-name frequency.
- **Severity:** high
- **Related thinker lenses:** all

## F06 Excessive questioning

- **Definition:** Continues inquiry after enough information exists or withholds useful explanation.
- **Detection signal:** Multiple low-value questions, no answer, user fatigue.
- **Bad input/output example:** “What is a database index?” → Ten questions about what the user thinks.
- **Why it fails:** Inquiry becomes interrogation.
- **Corrected behavior:** Explain directly; ask at most one question only if it changes depth or direction.
- **Suggested automated or manual test:** Count material questions and verify each changes a solution branch.
- **Severity:** high
- **Related thinker lenses:** Socrates

## F07 One lens used for every task

- **Definition:** Applies the same thinker intervention regardless of task signals.
- **Detection signal:** Lens selection is constant across factual, creative, urgent, and analytical cases.
- **Bad input/output example:** A weather lookup receives first-principles reconstruction.
- **Why it fails:** Lens preference overrides task fit.
- **Corrected behavior:** Use `default-direct-explanation` when no intervention is needed.
- **Suggested automated or manual test:** Mixed-task suite must include direct answers and multiple/no-lens selections.
- **Severity:** high
- **Related thinker lenses:** all

## F08 Conflicting lenses

- **Definition:** Combines actions that cannot jointly satisfy the task.
- **Detection signal:** Output both removes and requires a distinction, or asks and answers incompatibly.
- **Bad input/output example:** Simplifies away legal terms while claiming professional precision.
- **Why it fails:** The resulting behavior is internally inconsistent.
- **Corrected behavior:** Apply safety/correctness first; sequence intuition then restored terminology.
- **Suggested automated or manual test:** Check combined rules for contradictory `actions` and `avoid` items.
- **Severity:** high
- **Related thinker lenses:** all

## F09 Excessive abstraction

- **Definition:** Adds formal structure beyond what the question or evidence supports.
- **Detection signal:** Symbols or models have no mapping to concrete inputs and decisions.
- **Bad input/output example:** A team disagreement becomes an invented payoff matrix with fake numbers.
- **Why it fails:** Formal appearance creates false precision.
- **Corrected behavior:** Use a qualitative option/constraint table and mark unknowns.
- **Suggested automated or manual test:** Require every model element to map to observed or declared data.
- **Severity:** high
- **Related thinker lenses:** von Neumann

## F10 Vague philosophical language

- **Definition:** Uses abstractions such as balance, flow, or harmony without mechanisms.
- **Detection signal:** No actor, relation, state change, measure, or action.
- **Bad input/output example:** “Improve reliability.” → “Flow with the system and restore balance.”
- **Why it fails:** It is neither executable nor falsifiable.
- **Corrected behavior:** Trace one feedback loop, choose a reversible change, and set an error-rate threshold.
- **Suggested automated or manual test:** Require a named mechanism, action, and observable exit.
- **Severity:** medium
- **Related thinker lenses:** Laozi

## F11 Factual or technical error

- **Definition:** A lens-derived response contradicts reliable facts or correct procedure.
- **Detection signal:** Failed calculation, false claim, invalid command, or outdated standard.
- **Bad input/output example:** A neat analogy yields the wrong network-security recommendation.
- **Why it fails:** Factual correctness has priority over all lenses.
- **Corrected behavior:** Verify the technical claim and discard the analogy if it does not preserve the relevant mechanism.
- **Suggested automated or manual test:** Run domain tests and source checks independent of lens quality.
- **Severity:** critical
- **Related thinker lenses:** all

## F12 Missing safety boundary

- **Definition:** A rule can be applied in a dangerous context without an override.
- **Detection signal:** No safety note for urgent, high-stakes, manipulative, or precision-sensitive use.
- **Bad input/output example:** “Minimize intervention” recommends waiting during a security breach.
- **Why it fails:** Method generalization displaces required protection.
- **Corrected behavior:** Contain the breach first; minimize only optional follow-up disruption.
- **Suggested automated or manual test:** Run each rule against medical, legal, financial, security, and emergency cases.
- **Severity:** critical
- **Related thinker lenses:** all, especially Laozi and Socrates

## F13 No exit condition

- **Definition:** A lens has no observable stopping point.
- **Detection signal:** Repeated simplification, questioning, modeling, or caution after the obstacle is resolved.
- **Bad input/output example:** Continues counterexamples after a claim has been correctly bounded.
- **Why it fails:** The intervention dominates the task.
- **Corrected behavior:** Stop once the bounded claim is established and answer the original question.
- **Suggested automated or manual test:** Validator requires nonempty `exit_conditions`; manual test observes stopping.
- **Severity:** high
- **Related thinker lenses:** all

## F14 Trigger false positive

- **Definition:** Selects a lens when its task signal is absent.
- **Detection signal:** Unnecessary method overhead on a direct request.
- **Bad input/output example:** “Convert 2 km to meters.” → Starts definition clarification.
- **Why it fails:** Adds friction and may obscure a simple answer.
- **Corrected behavior:** Answer “2,000 meters” directly.
- **Suggested automated or manual test:** Negative examples for every trigger.
- **Severity:** medium
- **Related thinker lenses:** all

## F15 Trigger false negative

- **Definition:** Misses a lens when its documented signal is present and materially important.
- **Detection signal:** Generic answer leaves ambiguity, hidden premise, or feedback unaddressed.
- **Bad input/output example:** Accepts “automation always saves time” without testing maintenance costs.
- **Why it fails:** The known reasoning obstacle remains.
- **Corrected behavior:** Surface the universal assumption and bound it with a counterexample.
- **Suggested automated or manual test:** Positive paraphrase set for each trigger condition.
- **Severity:** medium
- **Related thinker lenses:** all

## F16 Source confidence not disclosed

- **Definition:** Presents provisional or weakly supported extraction as established.
- **Detection signal:** Missing confidence or TODO marker for unresolved attribution.
- **Bad input/output example:** Calls a modern systems heuristic “Laozi's method” without qualification.
- **Why it fails:** Conceals inference distance.
- **Corrected behavior:** Label it a provisional adaptation and state needed textual verification.
- **Suggested automated or manual test:** Validator checks allowed confidence; reviewer audits evidence-to-confidence fit.
- **Severity:** high
- **Related thinker lenses:** all, especially Laozi and von Neumann

## F17 Biography replacing methodology

- **Definition:** Personal history occupies the place of triggerable behavior.
- **Detection signal:** Dates, achievements, or anecdotes without actions and limits.
- **Bad input/output example:** Explains von Neumann's reputation but provides no decomposition rule.
- **Why it fails:** Biography cannot be executed or evaluated as a Skill.
- **Corrected behavior:** Extract components/interfaces behavior or omit the material.
- **Suggested automated or manual test:** Each retained paragraph must support evidence, behavior, boundary, or evaluation.
- **Severity:** medium
- **Related thinker lenses:** all

## F18 Style imitation replacing reasoning

- **Definition:** Mimics sentence length, paradox, humor, or tone instead of method.
- **Detection signal:** Stylistic transformation with identical logical gaps.
- **Bad input/output example:** Rewrites weak advice as a Laozi-like aphorism.
- **Why it fails:** The underlying decision does not improve.
- **Corrected behavior:** Identify dependency, feedback, intervention, and threshold in plain language.
- **Suggested automated or manual test:** Score reasoning actions separately from style; style alone earns no credit.
- **Severity:** medium
- **Related thinker lenses:** all

## F19 Loss of necessary terminology

- **Definition:** Plain-language explanation never reconnects to required formal terms.
- **Detection signal:** User gains a metaphor but cannot read specifications or communicate precisely.
- **Bad input/output example:** Calls race conditions “two things bumping” and stops there.
- **Why it fails:** It prevents transfer and can merge distinct concepts.
- **Corrected behavior:** Use the ordinary-language case, then define race condition and its ordering constraint.
- **Suggested automated or manual test:** Require formal term restoration and one correct use after simplification.
- **Severity:** high
- **Related thinker lenses:** Feynman

## F20 Correct method applied in the wrong domain

- **Definition:** A valid method is generalized beyond its evidentiary or professional scope.
- **Detection signal:** Philosophical or pedagogical heuristic controls diagnosis, legal duty, finance, or emergency action.
- **Bad input/output example:** Uses counterexamples to dismiss a clinically validated protocol for one atypical anecdote.
- **Why it fails:** Domain standards and evidence base are ignored.
- **Corrected behavior:** Follow current professional guidance; use the lens only to clarify communication or optional analysis.
- **Suggested automated or manual test:** Cross-domain adversarial suite with mandatory-standard cases.
- **Severity:** critical
- **Related thinker lenses:** all

## Evaluation Checklist

- [ ] The selected trigger matches an observable task signal.
- [ ] Required actions are visible without thinker name or stylistic clues.
- [ ] Every selected lens stops at its exit condition.
- [ ] Factual correctness and current domain standards were checked first.
- [ ] Safety boundaries override questioning, simplification, modeling, and non-intervention.
- [ ] Definitions, assumptions, models, and analogies state their limits.
- [ ] Plain language restores necessary formal terminology.
- [ ] Questions are material, neutral, and no more numerous than needed.
- [ ] Combined lenses have compatible or explicitly sequenced actions.
- [ ] Sources resolve; uncertainty and TODO-SOURCE gaps are disclosed.
- [ ] Output contains no impersonation, invented quote, or guaranteed thinker endorsement.
- [ ] A direct answer was preferred when lens use added no value.
