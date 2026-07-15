# Agent Contribution Rules

1. Inspect the repository, conventions, and working tree before editing; preserve existing architecture and useful work.
2. Use Python 3.11+, `pathlib` for filesystem access, type hints throughout, and dataclasses or similarly explicit typed models.
3. Prefer the standard library; add a dependency only when its maintenance cost is justified. YAML parsing uses PyYAML.
4. Never fabricate citations, quotations, page numbers, URLs, dates, titles, or source claims.
5. Every new thinker method requires the metadata defined in `references/distillation_framework.md`.
6. Every new trigger requires success and failure coverage in `evals/cases.yaml`, explicit `avoid` actions, an exit condition, priority, and pytest coverage.
7. Do not change runtime behavior without meaningful tests. Use pytest and test behavior rather than file existence alone.
8. Every behavior change requires a `CHANGELOG.md` entry.
9. Do not roleplay thinkers or substitute stylistic imitation for reasoning behavior.
10. Avoid decorative, mystical, biographical, or motivational filler.
11. Keep Markdown heading levels consistent with neighboring files.
12. Keep YAML valid; trigger IDs must be unique and source references must resolve to existing entries or an explicit `TODO-SOURCE` marker.
13. Run `python scripts/validate.py` and `pytest` before completion.
14. Report unresolved research gaps and confidence honestly.
15. Preserve safety and factual-correctness precedence when adding or combining lenses.
