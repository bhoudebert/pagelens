# Limitations and roadmap

Pagelens is a demonstrator of a sound architecture, not a finished product. These are the
current boundaries.

## Known limitations

| Area | Limitation | Mitigation today |
| --- | --- | --- |
| Verification | With `--evidence any`, the vision model can confirm a page that does not contain the requested reference. On the bundled corpus, `exact-reference` confirms `service-bulletin.pdf` p. 1 (a radiator drawing) when verifying 20 candidates. | Treat `confirmed` as strong evidence, not proof; use `--evidence visual` where possible; the `evaluate --verify` harness exposes regressions. |
| Scale | Search is brute-force over all vectors in SQLite; every query loads all regions. Suitable for thousands of pages, not millions. | Ports allow a vector-database adapter (see roadmap). |
| Ranking | Scores are cosine similarity plus a small lexical boost. They are not calibrated probabilities. | Verification, thresholds chosen per collection. |
| Small objects | Objects far smaller than a tile can be diluted in the embedding. | Smaller `PAGELENS_TILE_SIZE`, then re-ingest. |
| Exact identity | Look-alike products can score highly; similarity is not identity. | Use verification metadata and part-number text search. |
| OCR | Optional and Tesseract-based; no layout analysis. | Visual retrieval does not depend on it. |
| Models | Retrieval and verification quality depend on the chosen local models and Ollama version. | Pinned defaults; swap through environment variables. |
| Concurrency | Single-process, single-writer SQLite; no service API. | CLI use. |
| Security | No authentication or multi-tenancy; designed for one user's local files. | See [`SECURITY.md`](../SECURITY.md). |

## Roadmap

1. **Approximate nearest neighbours** – Qdrant or sqlite-vec adapter behind `RegionStore`.
2. **Incremental ingestion** – skip unchanged files by content hash; background re-index.
3. **Stronger verification** – few-shot prompts, calibration set, and a second-opinion pass
   for `--evidence any`.
4. **Layout-aware regions** – detect figures and tables instead of fixed tiles.
5. **Result viewer** – small local web UI showing the page with the bounding box highlighted.
6. **Learned reranking** – cross-encoder reranker over the top candidates.
7. **Service mode** – HTTP API for integration, with authentication.
