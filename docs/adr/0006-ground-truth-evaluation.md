# 0006. Evaluate against page-level ground truth

- Status: accepted
- Date: 2026-10-24

## Context

Retrieval and verification changes are easy to judge by anecdote. Customers need evidence
that the system works and an honest view of where it does not.

## Decision

Ship fictional manuals with page-level ground truth (`testdata/`), and an `evaluate`
command that runs the normal pipeline. Without `--verify` it measures recall; with it, it
also fails on forbidden confirmations. Exit code is non-zero on failure.

## Consequences

Changes are scored; regressions show up in CI-style runs. The corpus is small and synthetic,
so results are indicative, not a benchmark. Needs real models to run, so it is not part of
the offline unit suite.

## Alternatives considered

Unit tests with fake embedders only: cannot catch model behaviour. A public benchmark:
does not reflect technical manuals.
