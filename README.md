# Pagelens

**Find which page of which PDF shows it.**

Pagelens is a local-first multimodal search tool for PDF collections. Describe an object in
words, hand it a reference photo, or both, and Pagelens returns the PDF, the one-based page,
the exact region, and a saved preview — even when the page never names the object. Nothing
leaves your machine.

```text
$ pagelens query "water pump" --verify --limit 5

 Relevance  PDF                  Page  Result     Evidence
     0.789  pump-catalog.pdf        2  confirmed  centrifugal water pump · Aquaflow Systems · WP-450 · AF-P-1042
     0.739  image-only-scan.pdf     1  confirmed  water pump
     0.717  vehicle-catalog.pdf     2  confirmed  water pump · Utility room arrangement UR-12
Hidden 2 rejected candidate(s); use --include-rejected to inspect them.
```

Real output from the bundled demo corpus (condensed). The scanned page has no text layer and
the third hit is a small pump inside a large layout.

## Why it is different

| Typical PDF search | Pagelens |
| --- | --- |
| Matches words | Matches **what is depicted**: photos, scans, vector drawings |
| Fails on image-only scans | Embeds the rendered page; OCR is optional, not required |
| Returns a document | Returns **document, page, region, preview** |
| A similarity score is the answer | Scores rank candidates; an optional vision model **confirms or rejects** each one |
| Cloud API | Runs on your hardware through [Ollama](https://ollama.com) |
| "Seems to work" | Ships a **ground-truth evaluation** you can run on every change |

## How it works

```text
PDF ─► render pages ─► overlapping regions ─► multimodal embeddings ─► SQLite
                  └──► native / OCR text ───────────────────────────┘

query (text and/or images) ─► embed ─► cosine + exact-text boost ─► best region per page
                                                                          │
                                         optional vision verification ◄───┘
```

1. **Index** – every page is rendered (so vector art counts) and cut into overlapping
   regions. Text blocks are attached to the regions they overlap.
2. **Retrieve** – text and reference images are embedded in one shared vector space.
   Multiple reference views are kept separate, not averaged. A small lexical boost helps
   exact part numbers.
3. **Verify (optional)** – a vision model sees the crop and the full page and returns a
   structured verdict, extracted metadata, and which kind of evidence it used.

See [`docs/architecture.md`](docs/architecture.md) for the design.

## Quick start

Requirements: Python 3.11–3.13 and [Ollama](https://ollama.com) ≥ 0.12.7.
[Tesseract](https://github.com/tesseract-ocr/tesseract) is optional and only needed to read
text from scanned pages.

```bash
# 1. Models (one-time, ~7 GB)
ollama pull embeddinggemma-2:440m-q8_0-text-vision   # retrieval
ollama pull qwen3-vl:8b-instruct                      # optional verification

# 2. Install
pip install -e .          # or: uv sync

# 3. Try it on the bundled fictional manuals
scripts/demo.sh --verify
```

Prefer Nix? Run the packaged CLI with `nix run path:. -- <pagelens arguments>`.

> **Always put `--` after the flake reference.** Without it, Nix parses options such as
> `--verify` or `--json` itself and fails with `error: unrecognised flag '--verify'`.
> `nix run path:. -- query "motorcycle" --verify` is correct;
> `nix run path:. query "motorcycle" --verify` is not. To avoid the separator entirely, use
> `nix shell path:.` (then call `pagelens ...` directly) or `nix develop path:.`.

### Discover the commands

```bash
pagelens --help            # commands: init, status, ingest, query, evaluate
pagelens query --help      # every option, with examples
# Nix:
nix run path:. -- --help
nix run path:. -- query --help
```

### Use it on your own documents

Examples use the installed `pagelens`. Under Nix, replace `pagelens` with
`nix run path:. --` (see the note above).

```bash
pagelens init
pagelens ingest ./manuals                      # file or directory, recursive
pagelens query "industrial water pump"
pagelens query --image ./photo-of-the-part.jpg
pagelens query "same pump model" --image ./photo.jpg --verify
pagelens query "AF-P-1042" --json              # machine-readable output
```

Data lives in `.pagelens/` (override with `--data-dir` or `PAGELENS_DATA_DIR`).
More in the [user guide](docs/user-guide.md) and the [CLI reference](docs/cli-reference.md).

## Measured, not claimed

`testdata/` holds four fictional manuals and page-level ground truth covering labelled
objects, image-only scans, text-only mentions, vector drawings, small objects, and hard
negatives.

```bash
pagelens evaluate testdata/ground-truth.json            # candidate recall
pagelens evaluate testdata/ground-truth.json --verify   # + false-confirmation checks
# Nix: nix run path:. -- evaluate testdata/ground-truth.json --verify
```

On the bundled corpus, retrieval recall is 6/6 scenarios. The verified run is stricter and
currently flags one known false confirmation — see
[limitations](docs/limitations-and-roadmap.md). Reporting that openly is the point of the
harness.

## Documentation

| Topic | File |
| --- | --- |
| Using Pagelens end to end | [`docs/user-guide.md`](docs/user-guide.md) |
| Every command and option, and how to launch them (pip, Nix) | [`docs/cli-reference.md`](docs/cli-reference.md) |
| Design and boundaries | [`docs/architecture.md`](docs/architecture.md) |
| Model choices and privacy | [`docs/model-selection.md`](docs/model-selection.md) |
| Known limits and roadmap | [`docs/limitations-and-roadmap.md`](docs/limitations-and-roadmap.md) |
| Behavioural requirements | [`openspec/specs/`](openspec/specs/multimodal-pdf-search/spec.md) |
| Test corpus | [`testdata/README.md`](testdata/README.md) |

## Development

```bash
nix run path:.#quality         # Ruff, mypy, pytest + coverage, pinned toolchain
make quality                   # same checks inside `nix develop path:.` or a uv venv
make demo                      # end-to-end run against local Ollama
```

Unit tests are deterministic and offline. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Project status

Pre-1.0 (`0.x`). The CLI and SQLite schema may change between minor versions; changes are
recorded in [`CHANGELOG.md`](CHANGELOG.md) and follow [Semantic Versioning](https://semver.org/).
Licensed under the [MIT License](LICENSE).
