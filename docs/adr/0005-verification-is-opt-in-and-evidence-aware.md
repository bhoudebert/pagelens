# 0005. Verification is opt-in and applies an evidence policy

- Status: accepted
- Date: 2026-10-24

## Context

Vector similarity ranks candidates but does not prove that an object is present, and
text-only mentions are not the same as a depicted object.

## Decision

A vision model verifies candidates only on request (`--verify`). It sees the crop and the
full page and returns a structured verdict, metadata, and the kind of evidence it used.
Two policies exist: `visual` (default; the object must be depicted) and `any` (text may
confirm). In `visual` mode the application downgrades a confirmation that did not use
visual evidence. The verifier never introduces candidates.

## Consequences

Retrieval stays fast and cheap by default; confirmation costs one model call per candidate.
The vision model can still be wrong: see the known `exact-reference` failure in the
limitations.

## Alternatives considered

Always verifying: too slow. Trusting the score: overclaims. Letting the verifier search:
hides retrieval errors.
