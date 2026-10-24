# 0002. Keep providers behind ports

- Status: accepted
- Date: 2026-10-24

## Context

The pipeline depends on a PDF renderer, an embedding model, a vector store and a vision
model. Each is likely to change, and tests must run without any of them.

## Decision

`application/` depends only on the protocols in `ports.py` (`PdfRegionExtractor`,
`MultimodalEmbedder`, `RegionStore`, `CandidateVerifier`). `adapters/` implements them
(PyMuPDF, Ollama, SQLite). The CLI is the only place that wires adapters together.

## Consequences

Tests use deterministic fakes and stay offline. A new store or embedder is one new adapter.
The cost is a thin layer of indirection and a rule reviewers must enforce: no adapter
imports in `application/`.

## Alternatives considered

Calling Ollama and SQLite directly from the use cases: shorter, but untestable offline and
hard to replace.
