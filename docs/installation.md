# Installing Mingren Skill

Mingren is installed into a capable host by providing the runtime bundle and making `SKILL.md` the entry instruction. No API key, network service, Python runtime, or backend is needed for ordinary use.

Build the portable bundle as a maintainer with:

```sh
python scripts/build_skill_bundle.py
```

This creates `dist/skill/`, `dist/mingren-skill.zip`, and a checksum manifest. Generated distribution artifacts are reproducible and intentionally not committed.

## ChatGPT-style host

Use the host's supported file or Skill installation mechanism to provide the ZIP or the contents of `dist/skill/`. Set or load `SKILL.md` as the entry instruction and keep its required references available. Exact interface labels vary by host, so consult the host's current documentation. No model API credential is needed.

## Claude-style host

Add the runtime bundle through the host's supported project, knowledge, or Skill file mechanism. Ensure `SKILL.md` and relative reference files remain available together. Do not configure a separate generation API; the host model already executes the Skill.

## Codex-style host

Clone or provide the repository, then instruct the agent to read `SKILL.md` and its runtime references. The Python toolkit can validate or inspect behavior during development, but it is optional for normal host execution. No external generation API is needed.

## Skill installation versus toolkit installation

- **Skill installation:** load `dist/skill/` or `dist/mingren-skill.zip` into the host. This is the end-user path and has no Python dependency.
- **Toolkit installation:** maintainers may run `python -m pip install -e ".[dev]"` to use routing, prompt inspection, response linting, tests, and bundle validation offline.

Hosts differ in supported file layouts and instruction-loading behavior. Compatibility should be claimed only after a manual evaluation using `evals/manual_evaluation.md`.
