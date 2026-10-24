<!-- Title: Conventional Commits, e.g. "feat(query): combine text and reference images". The title becomes the commit on main. -->
<!-- The path every change follows: docs/EVOLVING.md -->

## Summary

<!-- What changes and why, in a few lines. -->

## Decision and spec

<!-- ADR added, or "none needed" (docs/adr/). Spec requirement added or changed (openspec/specs/...), or "no behaviour change". -->

## Verified

<!-- What was run: make quality, `pagelens evaluate` (with and without --verify), a real Ollama run. State what was NOT verified, and any scenario that fails. -->

## Checklist (docs/EVOLVING.md)

- [ ] ADR when the shape of the system changes
- [ ] Spec updated first when behaviour changes
- [ ] Providers stay behind `ports.py`; no adapter imports in `application/`
- [ ] Tests with the code, offline and deterministic; `make quality` passes
- [ ] Ground truth extended or re-run when retrieval or verification changed
- [ ] Docs updated (`docs/`, README, CLI reference); site if a user would notice
- [ ] Commits and PR title follow Conventional Commits
