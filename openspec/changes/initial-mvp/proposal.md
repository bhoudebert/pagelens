# Change: Initial multimodal PDF-search MVP

## Why

Users need to locate visually depicted equipment and its nearby references without relying
on the PDF containing the same words as the query.

## What changes

- Add deterministic PDF rendering and overlapping region generation.
- Add shared Ollama text/image embeddings.
- Add a local SQLite collection with vector and lexical retrieval.
- Add optional Ollama vision verification, visual/text evidence policies, and metadata
  extraction.
- Add a CLI for initialization, ingestion, search, collection inspection, and synthetic
  ground-truth evaluation.

## Impact

This introduces storage schema version 1 and CLI version 0.1.0. Model changes require
explicit reindexing.

