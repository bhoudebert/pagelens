# Synthetic evaluation corpus

This directory contains fictional data for manual retrieval tests. It is safe to commit and
contains no customer documents or real product claims.

## Coverage

- `pump-catalog.pdf`: labelled pump plus fuel-pump and compressor hard negatives.
- `service-bulletin.pdf`: unrelated cooling-assembly drawing without the word “pump” and a
  text-only water-pump procedure.
- `vehicle-catalog.pdf`: visually identified fictional motorcycle and a small pump embedded
  in a large layout.
- `image-only-scan.pdf`: pump photograph with no searchable page text.
- `ground-truth.json`: relevant pages and negative expectations for representative queries.

## Rebuild

```bash
./testdata/build-manuals.sh
```

Chromium prints the HTML fixtures from `sources/` to A4 PDFs. Generated raster assets were
created specifically for this repository; prompts avoided brands, labels, and watermarks.
After rebuilding a PDF, ingest it again so its stored regions and previews match the new
file. Re-ingesting a source path replaces its existing indexed version.

> Nix users: keep the `--` in every `nix run path:. -- <command> --option` line below, or
> Nix rejects options such as `--verify`.

## Ground-truth evaluation

```bash
ollama pull embeddinggemma-2:440m-q8_0-text-vision
ollama pull qwen3-vl:8b-instruct
nix run path:. -- init --data-dir .pagelens-test
nix run path:. -- ingest testdata/manuals --data-dir .pagelens-test
nix run path:. -- evaluate testdata/ground-truth.json --data-dir .pagelens-test
nix run path:. -- evaluate testdata/ground-truth.json --data-dir .pagelens-test --verify
```

The service bulletin fixture was updated to remove the pump-like symbol. If you already
have `.pagelens-test`, refresh that one source before evaluating:

```bash
nix run path:. -- ingest testdata/manuals/service-bulletin.pdf \
  --data-dir .pagelens-test
```

The non-verified run measures whether expected pages were retrieved in the top 20. The
verified run compares only `confirmed` PDF/page pairs and also enforces
`must_not_confirm`. Both commands exit non-zero when a scenario fails. Restrict an
expensive VLM run with, for example, `--scenario water-pumps-visual`.

## Scenarios

- `water-pumps-visual`: requires a visibly depicted water pump; the text-only bulletin,
  fuel pump, compressor, and unrelated cooling assembly must not be confirmed.
- `water-pumps-any-evidence`: also accepts the bulletin's explicit text-only procedure.
- `pump-visual-broad`: deliberately accepts both water and fuel pumps, demonstrating that
  `pump` is broader than `water pump`.
- `exact-reference`: finds `AF-P-1042` from labels or text.
- `motorcycle-visual`: finds the unlabeled motorcycle and rejects visually unrelated pages.
- `compressor`: isolates the compressor hard negative used by water-pump searches.

For an individual result audit, run:

```bash
nix run path:. -- query "water pump" --data-dir .pagelens-test --limit 20 --verify
nix run path:. -- query "water pump" --data-dir .pagelens-test --limit 20 \
  --verify --evidence any --include-rejected
```

