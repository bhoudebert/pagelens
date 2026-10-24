from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from pagelens.domain.models import Document, IndexedRegion
from pagelens.ports import MultimodalEmbedder, PdfRegionExtractor, RegionStore


@dataclass(frozen=True, slots=True)
class IngestReport:
    documents: int
    pages: int
    regions: int


class IngestDocuments:
    def __init__(
        self,
        extractor: PdfRegionExtractor,
        embedder: MultimodalEmbedder,
        store: RegionStore,
        preview_root: Path,
        progress: Callable[[Document], None] | None = None,
    ) -> None:
        self._extractor = extractor
        self._embedder = embedder
        self._store = store
        self._preview_root = preview_root
        self._progress = progress

    def execute(self, sources: Sequence[Path]) -> IngestReport:
        documents = pages = regions = 0
        for source in sources:
            document, drafts = self._extractor.extract(
                source, self._preview_root, self._embedder.model_id
            )
            vectors = self._embedder.embed_images([draft.preview_path for draft in drafts])
            if len(vectors) != len(drafts):
                msg = "embedding provider returned a different number of vectors than images"
                raise ValueError(msg)
            indexed = [
                IndexedRegion(region=draft, vector=vector)
                for draft, vector in zip(drafts, vectors, strict=True)
            ]
            self._store.replace_document(document, indexed)
            documents += 1
            pages += document.page_count
            regions += len(indexed)
            if self._progress:
                self._progress(document)
        return IngestReport(documents=documents, pages=pages, regions=regions)


def discover_pdfs(path: Path) -> list[Path]:
    if path.is_file():
        if path.suffix.casefold() != ".pdf":
            raise ValueError(f"not a PDF: {path}")
        return [path.resolve()]
    if not path.is_dir():
        raise FileNotFoundError(path)
    return sorted(item.resolve() for item in path.rglob("*.pdf") if item.is_file())
