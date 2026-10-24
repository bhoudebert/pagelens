# 0008. Scale by shrinking the index, then replacing the store

- Status: proposed
- Date: 2026-10-24

## Context

[ADR 0004](0004-sqlite-brute-force-search.md) chose SQLite and brute-force search for
simplicity. A large manufacturer may have millions of manuals, which means hundreds of
millions of regions and terabytes of vectors, far beyond a single-file brute-force scan.

## Decision

When scale requires it, first reduce what is indexed (layout-aware regions, deduplication,
truncated and quantized vectors, no stored crops), then replace the store with an
approximate-nearest-neighbour engine behind the existing `RegionStore` port, with metadata
filtering, hybrid BM25 search and a staged query (filter, ANN, rerank, optional verify).
Ingestion becomes a queue-driven worker pipeline. Details are in
[`docs/scaling.md`](../scaling.md).

## Consequences

`application/` is unchanged; a new adapter and a richer port are needed. Accuracy is traded
for cost and must be measured against a brute-force baseline with the ground-truth harness.
A service deployment replaces CLI-only use at that scale. Re-embedding on model change
becomes a planned migration.

## Alternatives considered

Scaling SQLite (sharded files, sqlite-vec): fine for moderate growth, weak for multi-node
filtering and concurrency. Indexing at page level only: far fewer vectors, but loses small
objects (see the limitations). Doing nothing: acceptable for the demo scale this project
targets today.
