# Changelog

All notable changes are documented here. The format follows Keep a Changelog and the
project follows Semantic Versioning.

## [0.2.0](https://github.com/bhoudebert/pagelens/compare/v0.1.0...v0.2.0) (2026-10-24)


### Features

* **init:** add first version ([e3d5593](https://github.com/bhoudebert/pagelens/commit/e3d5593a5dbfcbc4f16eed515ecc13ef3b9e7698))


### Documentation

* add project site, contributor workflow and release automation ([#1](https://github.com/bhoudebert/pagelens/issues/1)) ([e2df6dd](https://github.com/bhoudebert/pagelens/commit/e2df6ddca90215cef28470ca6172f0d3ee6deef5))
* describe how to scale beyond SQLite ([#14](https://github.com/bhoudebert/pagelens/issues/14)) ([c257db7](https://github.com/bhoudebert/pagelens/commit/c257db74b1aad521aa36854a02bbec16a1a16473))
* **preview:** add social preview and doc ([#11](https://github.com/bhoudebert/pagelens/issues/11)) ([e8eb7cf](https://github.com/bhoudebert/pagelens/commit/e8eb7cf67a4da9f24480481d7fb509891f9a1e61))


### Build and tooling

* **deps:** update GitHub Actions and Python dependency ranges ([#13](https://github.com/bhoudebert/pagelens/issues/13)) ([b9a6e2b](https://github.com/bhoudebert/pagelens/commit/b9a6e2b904dcb5a8fc342259fde4e4e2fd33a075))

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
