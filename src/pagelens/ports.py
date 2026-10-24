from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Protocol

from pagelens.domain.models import (
    CollectionStats,
    Document,
    DraftRegion,
    FloatArray,
    IndexedRegion,
    SearchResult,
    Verification,
)


class PdfRegionExtractor(Protocol):
    def extract(
        self,
        source: Path,
        preview_root: Path,
        embedding_model: str,
    ) -> tuple[Document, list[DraftRegion]]: ...


class MultimodalEmbedder(Protocol):
    @property
    def model_id(self) -> str: ...

    def embed_texts(self, texts: Sequence[str]) -> FloatArray: ...

    def embed_images(self, images: Sequence[Path]) -> FloatArray: ...


class RegionStore(Protocol):
    def initialize(self) -> None: ...

    def replace_document(
        self,
        document: Document,
        regions: Sequence[IndexedRegion],
    ) -> None: ...

    def search(
        self,
        query_vectors: FloatArray,
        query_text: str | None,
        embedding_model: str,
        limit: int,
    ) -> list[SearchResult]: ...

    def stats(self) -> CollectionStats: ...


class CandidateVerifier(Protocol):
    def verify(self, query: str, candidate: SearchResult) -> Verification: ...
