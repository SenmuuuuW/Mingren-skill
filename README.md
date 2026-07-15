# Source-Grounded Thinker Lenses

This Python 3.11+ project converts recurring reasoning methods associated with Feynman, Socrates, John von Neumann, and Laozi into bounded, testable Skill behaviors. It deterministically selects applicable rules and returns a structured reasoning plan; it does not generate the final natural-language answer.

The lenses are reasoning interventions: clarify a definition, expose an understanding gap, change a representation, or inspect second-order effects. They are not personalities, roleplay modes, biographies, quote collections, or substitutes for evidence.

## Architecture

The runtime is intentionally small and transparent:

- `models.py` defines validated dataclasses for rules, matches, selections, safety decisions, and engine results.
- `loaders.py` strictly parses YAML and resolves source references.
- `router.py` matches explicit keywords and patterns, ranks rules by match strength and priority, and flags incompatible lenses.
- `safety.py` applies keyword-based safety precedence. It is explicitly not a complete professional safety classifier.
- `engine.py` combines compatible actions, prohibitions, exits, and safety requirements into a structured plan.
- `__main__.py` exposes JSON output through the module and console CLIs.

## Trigger Selection

`references/trigger_rules.yaml` matches task signals to ordered actions. A rule must stop when its exit condition is met. Direct explanation is the default when questioning would add friction, and no lens applies universally. Compatible lenses may be sequenced or combined; incompatible actions are resolved using the conflict rule.

Safety and factual correctness always override thinker lenses. Professional standards govern high-stakes domains.

## Repository Structure

- `references/distillation_framework.md`: evidence and conversion process
- `references/thinkers/`: consistent thinker research records
- `references/trigger_rules.yaml`: machine-readable behavior rules
- `references/safety_boundaries.md`: hard constraints and examples
- `evals/failure_taxonomy.md`: failure definitions and tests
- `src/mingren_skill/`: typed Python runtime
- `evals/cases.yaml`: behavior and safety evaluation fixtures
- `tests/`: pytest behavior and validation coverage
- `scripts/validate.py`: repository, Markdown, YAML, and source-reference validation
- `AGENTS.md`: contribution rules for coding agents

## Setup and Installation

Python 3.11 or newer is required.

```sh
python -m pip install -e ".[dev]"
```

PyYAML is the only runtime dependency. Pytest is installed by the `dev` extra.

## CLI Usage

Both forms print a JSON-serialized `EngineResult`:

```sh
python -m mingren_skill "Explain recursion simply"
mingren-skill "Break this system into modules"
```

The JSON includes selected lenses, matched rule IDs, ordered actions, prohibited behaviors, exit conditions, safety notes, confidence, and a debug explanation.

## Rule Format

Every entry in `references/trigger_rules.yaml` requires:

```yaml
- id: explain-simply
  priority: 60
  description: "..."
  triggers: ["..."]
  primary_lens: feynman
  secondary_lenses: []
  actions: ["..."]
  avoid: ["..."]
  exit_conditions: ["..."]
  safety_notes: ["..."]
  confidence: medium
  source_refs: ["references/thinkers/feynman.md#replace-a-label-with-a-mechanism"]
```

Allowed confidence values are `high`, `medium`, `low`, and `provisional`.

## Adding a Method or Rule

1. Add the method to the appropriate thinker file with all evidence metadata, applicability limits, examples, and confidence.
2. Use `TODO-SOURCE` instead of guessing when evidence is incomplete.
3. Add or update a trigger with actions, prohibitions, exit conditions, safety notes, and source references.
4. Add a success/failure evaluation and changelog entry.
5. Add evaluation cases and behavior tests for the change.
6. Run validation and tests:

```sh
python scripts/validate.py
pytest
```

## Research Limitations

This first version deliberately marks several generalizations as provisional. Von Neumann reasoning-style claims are especially vulnerable to retrospective anecdote; Socratic evidence depends on mediated ancient texts; Laozi interpretation depends on textual and translation choices; and some popular Feynman teaching claims exceed the available primary evidence. See each thinker's open research questions.
