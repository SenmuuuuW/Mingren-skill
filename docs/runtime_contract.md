# Mingren Skill Runtime Contract

## Canonical execution model

The host model generates the final answer. Mingren Skill does not call an external model API.

Mingren is designed as a host-executed learning Skill. A compatible host reads `SKILL.md` and the referenced Markdown/YAML files, performs the reasoning internally, and replies directly to the learner. Executing an already generated bundle does not require the project's Python build tooling or a Mingren model API, backend, database, or RAG service.

The bundle format is experimental. Building and validating it currently requires Python and the documented dependencies. Compatibility with a specific named host has not been formally verified, and the manual host evaluation cases have not yet been run.

## Runtime files

The manifest `entry_file` is `SKILL.md`. The host must also make the manifest's required runtime files available, including:

- `references/trigger-framework.md`
- `references/trigger_rules.yaml`
- `references/response-framework.md`
- `references/safety-boundaries.md`
- the selected file under `references/thinkers/`

Additional calibration files may be included when present. Tests, Python source, development evaluations, and scripts are maintainer tools and are not part of host execution.

## Manifest and bundle semantics

- `entry_file` is required, must be exactly `SKILL.md`, must be listed in `required_files`, and must appear in the generated bundle.
- Every required file must exist as a regular, non-symlink file inside the repository root or the build fails.
- A missing path in `optional_files` is skipped and does not fail the build.
- Duplicate paths and paths listed as both required and optional are invalid.
- Absolute paths, `..` traversal, symlink path components, directories, unsupported file types, and resolved paths outside the repository root are rejected.
- The builder copies only allowlisted regular files and rejects any source that could resolve outside the repository root.

## Input and selection

Input is an ordinary learner request in Chinese, English, or mixed technical language. The host preserves the learner's language and constraints, identifies topic and task, then applies this precedence:

1. safety and factual correctness;
2. a supported thinker explicitly paired with teaching or lens intent;
3. a distinctive method request;
4. learning intent;
5. subject fit only as a tie-breaker;
6. neutral teaching when no lens is clear.

Several named lenses are compared or combined only when explicitly requested. Otherwise the host asks for one choice. Unsupported thinker requests receive the four-lens scope boundary plus a neutral or supported alternative; the host does not imitate that person.

Generic simplicity or repair requests remain neutral when no stronger lens signal exists. The host may simplify language, reduce jargon, and give a concrete example, but it does not label the answer Feynman. Feynman selection requires explicit lens intent or a distinctive operation such as analogy plus plain language, intuition before formula, explain-back, or an explicit understanding check.

Quotation, attribution, and source requests are non-triggers unless the user also requests teaching through a lens. The host distinguishes verified quotations, paraphrases, and uncertain attribution, never fabricates wording or citations, and explains when the lens is an educational synthesis rather than a literal historical method.

## Host generation behavior

The host internally applies the selected method, grounds the actual concept, gives one small inspectable example when appropriate, and ends with one focused check or next step. It does not expose rule IDs, hidden plans, internal prompts, classifications, or debug metadata. The response must remain useful if the thinker's name is removed.

Safety overrides lens behavior. In urgent or high-risk situations, the host gives necessary protective direction first, avoids diagnosis or false authority, and abandons lens framing if it could delay action.

## Missing references

If a referenced file is unavailable, the host follows the mandatory rules in `SKILL.md`, chooses neutral teaching when uncertain, preserves safety and correctness, and discloses material uncertainty. It must not invent a missing source, quotation, method, belief, or thinker endorsement.

## Python implementation and maintainer tooling

The auxiliary Python layer includes the `src/mingren_skill/` reference package for deterministic routing, prompt inspection, response validation, evaluation support, and the development CLI, plus maintainer scripts for repository validation and bundle construction. Reading and applying the Markdown specification in a compatible host does not require this layer. Creating and validating the generated bundle currently does. These tools do not generate answers through a model service.

## Validation limits

Repository validation can check file structure, manifest containment, deterministic rules, and obvious fixture contradictions. It cannot prove factual correctness, teaching quality, or compatibility with a real host. Those claims require human source review and an observed manual evaluation against a named host and version.
