# Changelog

All notable changes to this project will be documented here.

## [Unreleased]

### Added

- Research distillation and evidence-grading framework.
- Consistent research files for Feynman, Socrates, John von Neumann, and Laozi.
- Machine-readable trigger rules with priority, conflicts, exits, and safety notes.
- Failure taxonomy with concrete correction and evaluation guidance.
- Safety boundaries for attribution, precision, questioning, and high-stakes use.
- Typed Python models, strict YAML/research loaders, deterministic routing, safety precedence, and structured plan orchestration.
- Python module and `mingren-skill` JSON CLI entry points.
- YAML evaluation cases and behavior-focused pytest coverage.
- Python repository validator covering structure, sources, triggers, TODO-SOURCE records, taxonomy, and cases.
- README guidance for lens selection, extension, and current research limits.

### Changed

- Migrated validation and project tooling to Python 3.11+, PyYAML, pytest, and `pyproject.toml`.
- Added explicit numeric priority to every trigger rule.
- Expanded contributor rules for typing, tests, and evaluation-case requirements.

### Removed

- Standalone Ruby validation script.
