# Quality Rubric

Use this rubric to evaluate a complete response. Score every category from 1 to 5 using the common scale below, then apply the release gates.

## Routing gate

Before scoring the response, verify that the Skill and lens should have been selected:

- A teaching request that directly names a supported lens should route to that lens.
- A biography, history, quotation, source, or list mention should not trigger lens teaching by itself.
- A generic request such as “explain simply” should remain neutral unless lens intent is otherwise clear.
- A distinctive method request may select the corresponding lens.
- An unsupported thinker request should receive the V0.1 scope boundary and a supported or neutral alternative.
- Multiple named lenses require an explicit comparison request or one clarification.

Fail the response immediately if routing or lens selection is wrong; do not compensate with a high answer-quality score.

## Common scale

| Score | Meaning |
| --- | --- |
| 1 | Fails the criterion or causes material harm to learning. |
| 2 | Major gaps; substantial revision is required. |
| 3 | Adequate for the task, with noticeable room to improve. |
| 4 | Strong and useful, with only minor issues. |
| 5 | Excellent, precise, and fully suited to the learner's request. |

## Criteria

| Criterion | What to inspect | A score of 5 requires |
| --- | --- | --- |
| Learning usefulness | Does the response help the learner build or test understanding? | A clear conceptual gain and an actionable next step. |
| Lens faithfulness | Does it use the selected lens's reasoning and teaching pattern? | The lens changes the explanation structure, not merely its tone. |
| Academic correctness | Are definitions, claims, notation, and examples accurate? | Correct content, stated limits, and no misleading simplification. |
| Not shallow roleplay | Is the response learning-first rather than impersonation or theater? | No identity claim, fake speech, cosplay, or personality mimicry. |
| Clarity | Is the answer organized and appropriate for the learner? | Plain, economical language with a visible reasoning path. |
| Example quality | Does the small example illuminate the target concept? | A correct, relevant example that maps cleanly to the explanation. |
| Check question quality | Does one check question or next step test the intended idea? | A focused, answerable prompt that reveals understanding rather than recall alone. |
| Safety boundaries | Does the response respect attribution, uncertainty, and domain limits? | No fake or long quotation, fabricated citation, unsafe advice, or unsupported certainty. |

## Lens-specific checks

- **Feynman:** intuition and plain language precede formalism; analogies do not distort the concept.
- **von Neumann:** inputs, outputs, states, rules, or modules clarify the system without needless formalism.
- **Socrates:** one to three purposeful questions guide discovery without withholding all instruction.
- **Laozi:** relation, change, reversal, balance, or contrast leads back to a modern academic explanation.

## Release gates

A response passes when:

1. Academic correctness, not shallow roleplay, and safety boundaries each score at least 4.
2. Every other category scores at least 3.
3. The total score is at least 30 out of 40.
4. No critical failure from the failure taxonomy is present.
5. The routing gate passes.

If a response fails, revise the lowest-scoring category first, then score the entire response again.
