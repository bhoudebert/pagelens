# Contributing

## Setup

```bash
nix develop path:.        # pinned toolchain, or:
uv sync --dev             # plain Python 3.11–3.13
```

## Before opening a pull request

```bash
make quality              # ruff format --check, ruff check, mypy --strict, pytest + coverage
```

`nix run path:.#quality` and `nix flake check path:.` run the same gates in a clean
environment.

## Guidelines

- Keep business rules in `src/pagelens/application/`; provider code lives behind protocols
  in `ports.py` and implementations in `adapters/`.
- Unit tests must be deterministic and offline: temporary PDFs, fake embedders, no Ollama.
  Cover provenance, re-ingestion, multimodal fusion, and failure behaviour when touching
  retrieval.
- User-visible changes update `CHANGELOG.md`; requirement changes update `openspec/`.
- Never commit customer PDFs, model weights, previews, indexes, or secrets. The fictional
  fixtures in `testdata/` are the only PDFs allowed.
- Commit subjects are short and imperative (`Add image similarity scoring`).
