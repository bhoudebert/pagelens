from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path

import numpy as np

from pagelens.domain.models import FloatArray, SearchResult
from pagelens.ports import CandidateVerifier, MultimodalEmbedder, RegionStore


class SearchCollection:
    def __init__(
        self,
        embedder: MultimodalEmbedder,
        store: RegionStore,
        verifier: CandidateVerifier | None = None,
    ) -> None:
        self._embedder = embedder
        self._store = store
        self._verifier = verifier

    def execute(
        self,
        text: str | None,
        images: Sequence[Path],
        limit: int,
        verify: bool = False,
        group_by_page: bool = True,
    ) -> list[SearchResult]:
        normalized_text = text.strip() if text else None
        if not normalized_text and not images:
            raise ValueError("provide query text, at least one image, or both")
        if limit < 1:
            raise ValueError("limit must be at least 1")

        vectors: list[FloatArray] = []
        if normalized_text:
            vectors.extend(self._embedder.embed_texts([normalized_text]))
        if images:
            missing = [str(path) for path in images if not path.is_file()]
            if missing:
                raise FileNotFoundError(", ".join(missing))
            vectors.extend(self._embedder.embed_images(images))

        query_vectors = np.stack(vectors).astype(np.float32)
        retrieval_limit = max(limit * 12, 100) if group_by_page else limit
        candidates = self._store.search(
            query_vectors=query_vectors,
            query_text=normalized_text,
            embedding_model=self._embedder.model_id,
            limit=retrieval_limit,
        )
        if group_by_page:
            candidates = _best_region_per_page(candidates)[:limit]
        if not verify:
            return candidates
        if not normalized_text:
            raise ValueError("verification requires text explaining what should match")
        if self._verifier is None:
            raise ValueError("verification was requested but no verifier is configured")

        return [
            replace(candidate, verification=self._verifier.verify(normalized_text, candidate))
            for candidate in candidates
        ]


def _best_region_per_page(candidates: Sequence[SearchResult]) -> list[SearchResult]:
    """Keep the strongest crop as representative evidence for each PDF page."""
    seen: set[tuple[Path, int]] = set()
    grouped: list[SearchResult] = []
    for candidate in candidates:
        key = (candidate.source_path, candidate.page)
        if key not in seen:
            seen.add(key)
            grouped.append(candidate)
    return grouped
