# 0007. Conventional Commits, squash merges, automated releases

- Status: accepted
- Date: 2026-10-24

## Context

Changes arrive from people and coding agents. Versions and changelogs should follow from
the history without manual work.

## Decision

Commit messages and pull request titles follow Conventional Commits with a fixed type list.
A `commitizen` pre-commit hook checks messages locally; CI checks the PR title and the
commits of the pull request. Pull requests are squash-merged, so the title becomes the
commit on `main`. release-please reads `main` and maintains a release pull request with
the version bump and changelog; merging it tags the release and attaches the built wheel
and source archive. `main` is protected: pull request and green CI required.

## Consequences

A release costs one merge. Non-conventional titles are rejected early. Contributors learn
the convention; `CONTRIBUTING.md` documents it. Before 1.0, breaking changes bump the minor
version.

## Alternatives considered

Manual tagging and changelog: forgotten in practice. Merge commits: noisier history.
