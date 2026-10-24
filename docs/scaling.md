# Scaling beyond SQLite

The default store is one SQLite file with brute-force cosine search. It suits thousands to
low millions of regions on one machine. This page describes what changes for a large
manufacturer with millions of manuals. The decision is recorded in
[ADR 0008](adr/0008-scale-by-shrinking-the-index-then-replacing-the-store.md).

## Size the problem

Fixed tiling yields about 6 regions per A4 page at the default settings (the demo corpus has
9 pages and 54 regions). A 768-dimension `float32` vector is about 3 KB.

| Corpus | Pages | Regions | Raw vectors |
| --- | --- | --- | --- |
| 10,000 manuals × 100 pages | 1 M | 6 M | ~18 GB |
| 1,000,000 manuals | 100 M | 600 M | ~1.8 TB |
| Billions of manuals | 10¹¹ | 10¹² | petabytes |

The last row is not one index. It is a federated system partitioned by product line, brand
and language.

## 1. Index less

- **Fewer vectors.** Replace fixed tiles with layout-aware regions: embed figures, drawings
  and tables; skip cover pages and pure-text pages; deduplicate identical pages across
  revisions and languages by content hash.
- **Smaller vectors.** The embedding request already carries a `dimensions` value. Reducing
  768 to 256 (Matryoshka-style truncation) cuts size 3×. Quantize on top: int8 is 4×
  smaller, binary 32×, product quantization more. Keep full-precision vectors only to
  re-score the top candidates.
- **No stored crops.** Keep the bounding box and render previews on demand from the PDF in
  object storage.

## 2. Replace the store with an ANN index

| Scale | Approach | Candidates |
| --- | --- | --- |
| Up to ~100 M vectors | HNSW with quantization on one strong node or a small cluster | Qdrant, pgvector + pgvectorscale, OpenSearch |
| Beyond | Disk-based ANN (DiskANN, IVF-PQ), sharded | Milvus, Vespa, Elasticsearch/OpenSearch |

- Use the engine's BM25 for exact part numbers in place of SQLite FTS5.
- **Filter by metadata first.** Real queries are scoped ("this product family", "after
  2018"). Adding `product_family`, `language`, `revision` and access-control fields lets the
  engine cut candidates by orders of magnitude before similarity search.

## 3. Stage the query

```text
metadata filter ─► ANN over quantized vectors ─► rerank top 200–1000 with full vectors
                                                      ─► vision-model verify top 5–20
```

Verification is one model call per candidate; it stays a last step on a handful of results.

## 4. Make ingestion a pipeline

- Embedding about 600 M images at about 50 per second per GPU is roughly 140 GPU-days: plan a
  worker fleet behind a queue, with idempotent jobs and content-hash skipping.
- Changing the embedding model means re-embedding everything. Build the new index beside the
  old one and switch over; documents already record their embedding model.
- Enforce per-document access control at query time, not after retrieval.

## What changes in this repository

- `application/` stays. Add an adapter beside `adapters/store_sqlite.py` that implements
  `RegionStore`.
- Extend the `RegionStore` port with search filters, batch upserts and deletion by document.
- Make `MultimodalEmbedder` batch- and queue-friendly.
- Move from CLI-only to a service with the CLI as a client; SQLite's single writer does not
  fit.
- Keep `evaluate`, and add per-product-line ground truth plus recall-at-k measured against an
  exact brute-force baseline, to quantify what quantization and ANN cost in accuracy.

## Recommended path

Pilot 1–5 product lines (millions of regions): a vector engine with metadata filters, int8
quantization and the staged query. Use the pilot to measure recall loss and GPU cost, then
plan the rollout from those numbers.
