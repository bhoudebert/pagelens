# User guide

## Concepts

- **Collection** – a directory (default `.pagelens/`) holding the SQLite index and page
  previews. One collection uses one embedding model.
- **Region** – an overlapping tile of a rendered page, with the text that overlaps it.
- **Result** – the best region per PDF page: PDF path, one-based page, bounding box,
  relevance, preview image.
- **Verification** – an optional vision-model pass that confirms, rejects, or marks a
  candidate uncertain and extracts supported metadata.

> Using Nix? Prefix every command below with `nix run path:. --` (the `--` is required, or
> Nix rejects flags like `--verify`), or run `nix shell path:.` once and type `pagelens ...`.

## 1. Prepare

```bash
ollama serve &                                          # if not already running
ollama pull embeddinggemma-2:440m-q8_0-text-vision
ollama pull qwen3-vl:8b-instruct                        # only for --verify
```

## 2. Index

```bash
pagelens init
pagelens ingest ./manuals
pagelens status
```

Re-ingesting a path replaces its previous version; nothing is duplicated. Scanned pages
without a text layer are OCR'd when Tesseract is installed (`--no-ocr` disables this).
Visual search works either way.

## 3. Search

| Goal | Command |
| --- | --- |
| Find by description | `pagelens query "centrifugal water pump"` |
| Find by photo | `pagelens query --image part.jpg` |
| Combine both | `pagelens query "same pump" --image a.jpg --image b.jpg` |
| Exact part number | `pagelens query "AF-P-1042"` |
| Machine output | `pagelens query "water pump" --json` |

Several `--image` options are treated as independent views; each result keeps its best
match across them.

## 4. Verify

Scores rank candidates; they are not probabilities. Add `--verify` to have the vision model
check each candidate:

```bash
pagelens query "water pump" --verify                       # object must be visible
pagelens query "water pump" --verify --evidence any        # text-only mentions count too
pagelens query "water pump" --verify --include-rejected    # audit what was filtered
```

Choose the evidence policy deliberately. `visual` answers "where is it **shown**?"; `any`
answers "where is it **mentioned or shown**?". Category words are literal: `pump` includes
fuel pumps, `water pump` does not.

## 5. Measure on your own data

Write a ground-truth file shaped like [`testdata/ground-truth.json`](../testdata/ground-truth.json)
(`queries[]` with `relevant` and `must_not_confirm` PDF/page pairs), then:

```bash
pagelens evaluate my-truth.json --data-dir .pagelens
pagelens evaluate my-truth.json --verify
```

Exit code is non-zero when any scenario fails, so it works in CI.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `PAGELENS_DATA_DIR` | `.pagelens` | Collection directory |
| `PAGELENS_EMBEDDING_MODEL` | `embeddinggemma-2:440m-q8_0-text-vision` | Retrieval model |
| `PAGELENS_OLLAMA_MODEL` | `qwen3-vl:8b-instruct` | Verification model |
| `PAGELENS_OLLAMA_URL` | `http://127.0.0.1:11434` | Ollama server |
| `PAGELENS_RENDER_DPI` | `144` | Page render resolution |
| `PAGELENS_TILE_SIZE` | `768` | Region size in pixels |
| `PAGELENS_TILE_OVERLAP` | `128` | Region overlap in pixels |

Changing the embedding model, DPI, or tiling requires re-ingesting: vectors from different
models are not comparable.

## Troubleshooting

| Symptom | Cause / fix |
| --- | --- |
| `Ollama embedding request failed` | Ollama is not running or `PAGELENS_OLLAMA_URL` is wrong. |
| `model ... not found` | `ollama pull` the model named in the message. |
| `No compatible indexed regions found` | Collection is empty or indexed with another model; check `pagelens status`. |
| Scanned pages return no text | Install Tesseract; visual retrieval still works without it. |
| Verification is slow | The 8B vision model runs per candidate; lower `--limit`. |
