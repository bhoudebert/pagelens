# 0001. Record architecture decisions

- Status: accepted
- Date: 2026-10-24

## Context

Choices such as the embedding provider, the store and the verification policy are made in
conversations and pull requests, which are hard to find later.

## Decision

Significant choices are recorded as short numbered records in `docs/adr/`, from
`template.md`. A record is not rewritten after acceptance; a later record supersedes it.
Behaviour is specified in `openspec/specs/`; records explain why the system is shaped as it
is.

## Consequences

Newcomers and agents can read why before changing what. Each significant change costs a
few minutes of writing.

## Alternatives considered

Commit messages and PR descriptions only: too scattered. Rationale inside the specs: mixes
"what" with "why".
