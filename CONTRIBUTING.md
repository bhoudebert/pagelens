# Contributing

## What helps most

Pagelens is open source (MIT) and measured against ground truth. Small contributions make the
biggest difference, roughly in this order:

1. **An evaluation case.** A query Pagelens gets wrong, with the pages that must be found
   and the ones that must not be confirmed (`testdata/ground-truth.json`; the "Evaluation
   case" issue template is enough if you do not code).
2. **A bug report with a reproduction** on fictional or public PDFs.
3. **A better verification prompt**, with `pagelens evaluate --verify` output before and
   after.
4. **A provider**: another embedder, store or verifier behind the ports.
5. **Docs and examples** that make the first run easier.

Everyone taking part follows the [code of conduct](CODE_OF_CONDUCT.md).

## Setup

```bash
nix develop path:.        # pinned toolchain (Python 3.12, Ruff, mypy, pytest, Ollama, Tesseract)
# or
uv sync --dev             # plain Python 3.11–3.13
```

Models for the end-to-end checks:

```bash
ollama pull embeddinggemma-2:440m-q8_0-text-vision
ollama pull qwen3-vl:8b-instruct
```

`nix run path:.#quality` runs the same gates in a clean environment, and
`nix flake check path:.` also checks Nix formatting and the package build. Each file in
`nix/modules/` is a self-contained flake-parts module, picked up automatically. With Nix,
keep the `--` in `nix run path:. -- <command> --option`.

## Workflow

The path every change follows, from idea to release, is described in
[`docs/EVOLVING.md`](docs/EVOLVING.md). In short:

1. Branch from `main`: `feat/...`, `fix/...`, `docs/...`, `chore/...`.
2. Behaviour change: update the spec first, `openspec/specs/<capability>/spec.md`
   (requirements with scenarios). New capability: a new folder plus a line in
   `openspec/README.md`.
3. Architectural choice (new dependency, store, provider, model default, cross-cutting rule):
   add a record in [`docs/adr/`](docs/adr/) from `template.md`.
4. Code with tests. Business rules in `src/pagelens/application/`; providers behind
   protocols in `ports.py`. Unit tests are deterministic and offline: temporary PDFs, fake
   embedders, no Ollama, no model downloads.
5. `make quality` (format check, Ruff, mypy `--strict`, pytest with coverage) must pass.
   The pre-commit hooks format and lint staged files and check commit messages.
6. For retrieval or verification changes, run `pagelens evaluate testdata/ground-truth.json`
   with and without `--verify` and report the result, including failures.
7. Open a pull request with the template filled in: what was verified, what was not. The
   **PR title follows the commit convention too**: squash merges turn it into the commit on
   `main`, which release automation reads. CI runs format, lint, types, tests, the commit
   check and the title check. The maintainer reviews and merges.

## Commits

Conventional Commits, checked by a `commitizen` hook and in CI:

```text
<type>(<scope>): <subject>

<body: what and why, wrapped at 100 columns, optional>

<footer: BREAKING CHANGE: ..., Refs #12, optional>
```

### Types

| Type | Use for | Release effect |
| --- | --- | --- |
| `feat` | A capability users did not have before | minor version |
| `fix` | Wrong behaviour corrected | patch version |
| `perf` | Same behaviour, faster or cheaper | patch version |
| `refactor` | Code change with no behaviour change | none |
| `docs` | README, docs, specs, roadmap, comments | none (listed in the changelog) |
| `test` | Tests only | none |
| `build` | Dependencies, packaging, Nix, scripts | none (listed in the changelog) |
| `ci` | GitHub Actions, Dependabot, release automation | none |
| `chore` | Housekeeping that fits nowhere else | none |
| `style` | Formatting, no logic change | none |
| `revert` | Reverts a previous commit; subject names it | depends on what is reverted |

A breaking change adds `!` after the scope, `feat(cli)!: ...`, and a `BREAKING CHANGE:` footer
explaining the migration. Before 1.0 it bumps the minor version, after 1.0 the major.

### Scopes

Lower-case, kebab-case, the area touched: `ingest`, `query`, `verify`, `evaluate`, `store`,
`embedder`, `pdf`, `cli`, `config`, `testdata`, `nix`, `site`, `deps`, `release`. A scope is
optional for changes that span the project (`docs: ...`, `build: ...`).

### Subject and body

- Imperative, present tense: "add", "fix", "remove", not "added" or "adds".
- No trailing period; at most 100 characters for the header.
- Add a body when the why is not obvious from the diff. Reference issues in the footer:
  `Refs #12`, `Closes #12`.
- One concern per commit.

### Examples

```text
feat(query): combine text and each reference image
fix(store): skip vectors from another embedding model
perf(store): score regions in one matrix product
refactor(ingest): share batch embedding between adapters
docs(site): add the Nix toolbox section
test(ingest): re-ingesting a source does not duplicate regions
build(nix): pin the project Python in the dev shell
ci: check commit messages on pull requests
chore: remove scratch indexes
revert: "feat(query): combine text and each reference image"
```

## Licence of contributions

Contributions are accepted under the project's MIT licence; by opening a pull request you
agree to it. Test fixtures must be fictional or public domain; never contribute customer
documents, model weights, previews, indexes or secrets.

## Releases

Release automation (release-please) opens and maintains a release pull request on `main`
with the changelog and version bump. Merging it tags the release, publishes GitHub release
notes, and attaches the built wheel and source archive. Nothing is published to PyPI. Do not
edit the version or the released sections of `CHANGELOG.md` by hand; the version lives in
`pyproject.toml`, `src/pagelens/__init__.py` and `nix/modules/package.nix`, all updated by
the release PR.

## Code conventions

- Python 3.11+, four spaces, complete type annotations, `mypy --strict`. Ruff formats and
  lints; do not hand-format.
- `snake_case` modules and functions, `PascalCase` classes, noun-based domain types.
- Business rules in `application/`; provider-specific code behind protocols in `ports.py`.
  No adapter imports from `application/`.
- Do not import heavyweight model packages at module import time.
- Rules that must hold are enforced in code, not only in a prompt.
- Name tests after observable behaviour, for example
  `test_query_combines_text_and_each_reference_image`.
