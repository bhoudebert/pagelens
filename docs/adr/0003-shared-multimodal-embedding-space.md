# 0003. Embed text and images in one space through Ollama

- Status: accepted
- Date: 2026-10-24

## Context

Queries are text, images, or both, and pages may have no text layer. Retrieval must compare
a sentence with a picture. A Torch or Transformers runtime would add a heavy, platform-
sensitive dependency.

## Decision

Use a multimodal embedding model served by Ollama (`embeddinggemma-2:440m-q8_0-text-vision`
by default) so text and images land in one normalised 768-dimensional space. The model is
configurable; changing it requires re-ingesting, because vectors from different models are
not comparable. Each stored document records its embedding model, and search only considers
matching documents.

## Consequences

No in-process ML runtime; Ollama is a required local service. Quality depends on the chosen
model and Ollama version.

## Alternatives considered

OpenCLIP or SigLIP in-process: strong, but pulls in Torch. Hosted embedding APIs: breaks the
local-first, private-by-default promise.
