# Installing Mingren Skill

## Current status

The bundle format is experimental. A generated bundle is designed for host environments that can load its Markdown/YAML files, preserve relative references, and use `SKILL.md` as the entry instruction. Compatibility with a specific named host has not been formally verified, and the [manual behavioral cases](../evals/manual_evaluation.md) have not yet been run.

Building and validating the bundle currently requires Python 3.11 or newer and the documented dependencies. A compatible host may consume an already generated bundle without the project's Python build tooling; this is a design target, not a verified compatibility claim.

## Build and validate

Install the local development dependencies, validate the repository, and build the bundle:

```bash
python -m pip install -e ".[dev]"
python scripts/validate.py
python scripts/build_skill_bundle.py
```

This creates `dist/skill/`, `dist/mingren-skill.zip`, and a checksum manifest. Repository checks compare repeated local builds for deterministic output; cross-platform reproducibility has not been established. Generated distribution artifacts are intentionally not committed.

## Minimum host capabilities

A candidate host must be able to:

- load Markdown and YAML files;
- preserve and follow relative file references;
- use `SKILL.md` as the entry instruction;
- generate a learner-facing natural-language response; and
- preserve Skill safety instructions over user-provided text.

## Experimental loading procedure

1. Build and validate the bundle using the commands above.
2. Provide `dist/mingren-skill.zip` or the contents of `dist/skill/` through the candidate host's supported file or Skill mechanism.
3. Set or load `SKILL.md` as the entry instruction and keep the bundled relative file layout intact.
4. Run every case in [`evals/manual_evaluation.md`](../evals/manual_evaluation.md) and record the host name, model version, date, and result.

Interface labels and instruction-loading behavior vary by host. Do not describe a host as compatible until that manual evaluation has actually been completed for the named host and version.

## Bundle use versus toolkit use

- **Generated bundle:** designed to be read by a compatible host without the Python build tooling. This path has not yet been verified against a named host.
- **Python toolkit:** currently required to build and validate the bundle and available for offline routing, prompt inspection, response linting, tests, and local release checks.

Neither layer calls a model-provider API or requires a Mingren backend, database, or RAG service.
