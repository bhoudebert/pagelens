# CLI reference

## Running the CLI

The same commands work however you launch them. Only the prefix differs.

| Setup | Prefix | Example |
| --- | --- | --- |
| Installed (`pip install -e .`, `uv sync`) | `pagelens` | `pagelens query "motorcycle" --verify` |
| Module | `python -m pagelens` | `python -m pagelens query --help` |
| Nix, one-off | `nix run path:. --` | `nix run path:. -- query "motorcycle" --verify` |
| Nix shell | `pagelens` after `nix shell path:.` | `pagelens query "motorcycle" --verify` |

**With `nix run`, the `--` is mandatory.** It separates Nix's own options from pagelens's.
Without it, Nix tries to read `--verify`, `--json`, `--limit` and the like itself and fails
with `error: unrecognised flag '--verify'`. Plain words such as `query` are fine; the first
`--option` is what breaks.

### Discovering commands

```bash
nix run path:. -- --help             # list commands
nix run path:. -- query --help       # options and examples for one command
nix run path:. -- evaluate --help
```

Every `--help` page ends with, or contains, a ready-to-paste example for both the installed
and the `nix run path:. --` forms.

---

Global: `pagelens --version`, `pagelens --help`. Also runnable as `python -m pagelens`.
Exit codes: `0` success, `1` evaluation failed, `2` usage or runtime error.

All commands accept `--data-dir PATH` (default `.pagelens`).

## `init`

Create an empty collection.

## `status`

Print document, page and region counts and the embedding models present.

## `ingest PATH`

Render and index a PDF, or every PDF under a directory (recursive).

| Option | Description |
| --- | --- |
| `--model TEXT` | Ollama embedding model for this run. |
| `--ocr / --no-ocr` | OCR pages with no native text (default on; needs Tesseract). |

## `query [TEXT]`

Search with text, images, or both. At least one is required.

| Option | Description |
| --- | --- |
| `-i, --image PATH` | Reference image; repeatable. |
| `-n, --limit INT` | Maximum results, 1–500 (default 20). |
| `--model TEXT` | Embedding model the collection was built with. |
| `--verify` | Confirm candidates with the vision model (requires text). |
| `--evidence [visual\|any]` | `visual`: object must be depicted. `any`: text also counts. |
| `--include-rejected` | Keep rejected candidates in verified output. |
| `--all-regions` | Show every overlapping region instead of one per page. |
| `--json` | Emit JSON: `pdf`, `page`, `bbox`, `score`, `visual_score`, `lexical_rank`, `preview`, `text`, optional `verification`. |

## `evaluate [GROUND_TRUTH]`

Run the scenarios in a ground-truth file (default `testdata/ground-truth.json`).

| Option | Description |
| --- | --- |
| `--verify / --no-verify` | Also check confirmations and forbidden matches. |
| `--scenario ID` | Run only this scenario; repeatable. |
| `-n, --limit INT` | Candidates examined per scenario (default 20). |
| `--model TEXT` | Embedding model the collection was built with. |
