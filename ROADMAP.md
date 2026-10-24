# Roadmap and ideas

Not commitments. Ordered by expected value for someone searching technical PDF collections.
Known limits are in [`docs/limitations-and-roadmap.md`](docs/limitations-and-roadmap.md).

## Help wanted

Open to anyone; no API key needed for most (see [`CONTRIBUTING.md`](CONTRIBUTING.md)):

- **Evaluation cases** for queries Pagelens handles badly, with the pages that must and must
  not match. Use fictional or public documents.
- **A better verification prompt** that fixes the known `exact-reference` false confirmation
  without breaking the other scenarios.
- **Another embedder or store** behind `MultimodalEmbedder` / `RegionStore`.

## Next

1. **Approximate nearest neighbours** behind `RegionStore` (Qdrant or sqlite-vec), so query
   time stops growing linearly with the collection. The plan for very large corpora
   (quantization, metadata filters, staged queries, sharding) is in
   [`docs/scaling.md`](docs/scaling.md) and [ADR 0008](docs/adr/0008-scale-by-shrinking-the-index-then-replacing-the-store.md).
2. **Incremental ingestion**: skip unchanged files by content hash; background re-index.
3. **Stronger verification**: few-shot prompts, a calibration set, a second-opinion pass
   for `--evidence any`.
4. **Layout-aware regions**: detect figures and tables instead of fixed tiles.
5. **A local viewer** that shows the page with the bounding box highlighted.

## Later

- Learned reranking over the top candidates.
- An authenticated HTTP service mode for integration.
- Quotas, accounts and a shared cache if offered as a hosted service.
