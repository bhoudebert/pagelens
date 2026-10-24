# How Pagelens evolves

Every change follows the same path, whether a person or a coding agent makes it. The path
exists so that each change is designed before it is coded, specified before it is tested,
and explained before it is released.

```text
idea ─▶ decision ─▶ spec ─▶ code + tests ─▶ evaluate ─▶ docs ─▶ PR ─▶ release
        (ADR)      (openspec)              (ground truth)        (review) (automatic)
```

## 1. Idea

Ideas live in [`ROADMAP.md`](../ROADMAP.md) or an issue. Before building, say who it is for,
what they do, and what Pagelens does in response. A feature that cannot be described that
way is not ready.

## 2. Decision: an ADR when the shape of the system changes

A new data store, a new provider behind a port, a new dependency, a default model, a rule
that cuts across features, or a choice between real alternatives: add a record in
[`docs/adr/`](adr/) from `template.md`, including the alternatives that lost. Small
changes inside an existing shape need no record. Accepted records are never rewritten; a
later record supersedes them.

## 3. Spec: what the system shall do

Update `openspec/specs/<capability>/spec.md` with requirements (`MUST`, `SHOULD`, `MAY`)
and at least one scenario each. Proposals that are not yet implemented live under
`openspec/changes/<change-id>/` and are folded into the specs when merged. The spec is
reviewed in the same pull request as the code.

## 4. Code and tests

- Business rules in `src/pagelens/application/`; providers behind protocols in `ports.py`,
  implementations in `adapters/`. Heavy model packages are imported lazily.
- Rules that must always hold are enforced in code, not only in a prompt.
- Unit tests are deterministic and offline: temporary PDFs, fake embedders, no Ollama.
- `make quality` must pass (format, Ruff, mypy `--strict`, pytest with coverage).

## 5. Evaluate

Retrieval or verification changes are measured, not eyeballed. Add or adjust a scenario in
`testdata/ground-truth.json`, then run:

```bash
pagelens evaluate testdata/ground-truth.json            # candidate recall
pagelens evaluate testdata/ground-truth.json --verify   # + false confirmations
```

State the result in the pull request, including scenarios that fail. See the known failure
in [`docs/limitations-and-roadmap.md`](limitations-and-roadmap.md).

## 6. Docs

`README.md` when the overview changes; `docs/` for behaviour, options and limits;
`docs/cli-reference.md` when a command or flag changes; the `site/` page when a user would
notice the feature; `CONTRIBUTING.md` or `AGENTS.md` when the way of working changes;
`ROADMAP.md` when something ships or is dropped.

## 6a. Changelog

Do not edit `CHANGELOG.md` by hand for released versions. release-please writes it from the
Conventional Commit history. Write good commit subjects and PR titles.

## 7. Pull request

Fill in the template: what changed, which ADR and spec, what was verified and what was
not. The **PR title follows Conventional Commits**: squash merges turn it into the commit on
`main`, which release automation reads. CI runs format, lint, types, tests and the title
check; the maintainer reviews and merges.

## 8. Release

release-please keeps a release pull request open with the version bump and changelog.
Merging it tags the release, creates the GitHub release, and attaches the built wheel and
source archive. Nothing is published to PyPI.
