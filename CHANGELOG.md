# Changelog

All notable changes are documented here. The format follows Keep a Changelog and the
project follows Semantic Versioning.

## [Unreleased]

### Changed

- Renamed the project, package, CLI, and environment variables from `foundimage` /
  `FOUNDIMAGE_*` to `pagelens` / `PAGELENS_*`; default data directory is now `.pagelens/`.
- Rewrote the README for evaluators and added a user guide, CLI reference, and
  limitations/roadmap.
- Dev shell now pins the project Python and `PYTHONPATH`, so `make quality` works inside
  `nix develop`.

### Added

- Project governance: `CONTRIBUTING.md` (workflow, Conventional Commits, scopes), code of
  conduct, `SUPPORT.md`, `NOTICE.md`, `ROADMAP.md`, `docs/EVOLVING.md`, decision records in
  `docs/adr/`, issue and pull-request templates, `CODEOWNERS`, Dependabot, CodeQL.
- Release automation with release-please (version bump and changelog from Conventional
  Commits; wheel and sdist attached to the GitHub release) and a PR title check.
- Static project website in `site/` with a GitHub Pages deployment workflow.
- `--help` text shows `nix run path:. -- ...` usage (the `--` is required).
- `python -m pagelens` entry point, `scripts/demo.sh` / `make demo`, CI workflow,
  `CONTRIBUTING.md`, and `SECURITY.md`.
- Tests for ingestion, re-ingestion idempotence, and the CLI ingest/query/evaluate workflow.

- Initial local multimodal PDF-search project structure.
- Lightweight Ollama multimodal embeddings without an in-process Torch runtime.
- Qwen3-VL 8B Instruct as the local image-and-text verification model.
- Synthetic manuals, raster assets, hard negatives, and page-level retrieval ground truth.
- Page-grouped query results with concise evidence and an `--all-regions` diagnostic mode.
- Full-page verification context, category-aware decisions, explicit one-based pages, and
  rejected-result filtering.
- Visual-only and text-or-visual verification policies plus page-level ground-truth
  evaluation from the CLI.

