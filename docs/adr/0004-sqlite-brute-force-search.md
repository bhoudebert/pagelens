# 0004. Start with SQLite and brute-force cosine search

- Status: accepted
- Date: 2026-10-24

## Context

The first users index small and medium collections on one machine. Operating a vector
database would raise the cost of trying the tool.

## Decision

Store vectors, text, provenance and an FTS5 index in one SQLite file. Search loads regions
for the active embedding model, scores them with cosine similarity, and adds a small
lexical boost for exact text. The `RegionStore` port allows a vector-database adapter later.

## Consequences

Zero infrastructure and atomic re-ingestion. Query cost grows linearly with the collection;
documented as a limit and on the roadmap.

## Alternatives considered

Qdrant or sqlite-vec from the start: better scale, more moving parts before there is a
need.
