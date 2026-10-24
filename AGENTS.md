# Repository Guidelines

## Project Structure & Module Organization

Production Python code lives under `src/pagelens/`: `application/` contains use cases, `domain/` contains stable data types, and `adapters/` integrates PyMuPDF, SQLite, and Ollama. Tests mirror behavior under `tests/`. Dendritic flake-parts modules live in `nix/modules/`; OpenSpec capabilities and proposals live in `openspec/`. Runtime indexes and previews belong in ignored `.pagelens/` directories.

Document any departure from this layout in the root `README.md`. Avoid placing implementation files directly in the repository root; reserve it for project metadata, configuration, and contributor documentation.

## Build, Test, and Development Commands

Enter the pinned environment with `nix develop`, then use:

- `make format` — apply Ruff formatting and safe lint fixes.
- `make test` — run pytest with coverage.
- `make quality` — run formatting checks, Ruff, mypy, and tests.
- `nix flake check` — validate Nix formatting and static analysis.

Run the CLI with `python -m pagelens.cli --help` or `nix run . -- --help`.

## Coding Style & Naming Conventions

Target Python 3.11+, use four spaces and complete type annotations, and let Ruff format imports and code. Use `snake_case` for modules/functions, `PascalCase` for classes, and noun-based domain types. Keep business rules in `application/` and provider-specific behavior behind protocols in `ports.py`; avoid importing heavyweight model packages at module import time.

## Testing Guidelines

Use pytest and name tests after observable behavior, for example `test_query_combines_text_and_each_reference_image`. Unit tests must be deterministic and offline: use temporary PDFs and fake embedders instead of downloading weights or calling Ollama. Cover provenance, re-ingestion, multimodal fusion, and failure behavior when changing retrieval logic.

## Way of working

Every change follows [`docs/EVOLVING.md`](docs/EVOLVING.md): idea, ADR when the shape of the
system changes (`docs/adr/`), spec first (`openspec/specs/`), code with tests, evaluation on
`testdata/ground-truth.json` for retrieval changes, docs, pull request.

## Commit & Pull Request Guidelines

Commits and PR titles follow Conventional Commits (`feat`, `fix`, `perf`, `refactor`, `docs`,
`test`, `build`, `ci`, `chore`, `style`, `revert`; optional kebab-case scope; header up to 100
characters; imperative subject). Pull requests are squash-merged, so the title is the commit on
`main`; release-please builds versions and `CHANGELOG.md` from them, so do not edit released
changelog sections or version numbers by hand. Full rules: `CONTRIBUTING.md`.

Keep each commit focused. Update OpenSpec for requirement changes and add an ADR for architectural
decisions. Pull requests explain the problem and solution, list verification commands, link related
issues, and include representative CLI output. Never commit customer PDFs, model weights, generated
previews, indexes, or secrets; the fictional fixtures under `testdata/` are the explicit PDF exception.
