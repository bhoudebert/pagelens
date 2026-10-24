from collections.abc import Sequence
from pathlib import Path

import numpy as np
import pytest
from numpy.typing import NDArray

from pagelens.adapters.pdf_pymupdf import PyMuPdfRegionExtractor
from pagelens.adapters.store_sqlite import SQLiteRegionStore
from pagelens.application.ingest import IngestDocuments, discover_pdfs

MANUALS = Path(__file__).parent.parent / "testdata" / "manuals"


class ConstantEmbedder:
    model_id = "fake"

    def embed_texts(self, texts: Sequence[str]) -> NDArray[np.float32]:
        return np.ones((len(texts), 4), dtype=np.float32)

    def embed_images(self, images: Sequence[Path]) -> NDArray[np.float32]:
        return np.ones((len(images), 4), dtype=np.float32)


class ShortEmbedder(ConstantEmbedder):
    def embed_images(self, images: Sequence[Path]) -> NDArray[np.float32]:
        return np.ones((max(len(images) - 1, 0), 4), dtype=np.float32)


def _use_case(tmp_path: Path, embedder: ConstantEmbedder) -> IngestDocuments:
    return IngestDocuments(
        extractor=PyMuPdfRegionExtractor(enable_ocr=False),
        embedder=embedder,
        store=SQLiteRegionStore(tmp_path / "index.sqlite3"),
        preview_root=tmp_path / "previews",
    )


def test_discover_pdfs_finds_nested_files_in_stable_order() -> None:
    names = [path.name for path in discover_pdfs(MANUALS)]
    assert names == sorted(names)
    assert "pump-catalog.pdf" in names


def test_discover_pdfs_rejects_non_pdf_and_missing_paths(tmp_path: Path) -> None:
    text_file = tmp_path / "notes.txt"
    text_file.write_text("x")
    with pytest.raises(ValueError, match="not a PDF"):
        discover_pdfs(text_file)
    with pytest.raises(FileNotFoundError):
        discover_pdfs(tmp_path / "missing")


def test_reingesting_a_source_does_not_duplicate_regions(tmp_path: Path) -> None:
    source = MANUALS / "pump-catalog.pdf"
    store = SQLiteRegionStore(tmp_path / "index.sqlite3")
    use_case = _use_case(tmp_path, ConstantEmbedder())

    first = use_case.execute([source])
    second = use_case.execute([source])

    assert first == second
    assert store.stats().documents == 1
    assert store.stats().regions == first.regions


def test_ingest_fails_when_embedder_returns_wrong_vector_count(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="different number of vectors"):
        _use_case(tmp_path, ShortEmbedder()).execute([MANUALS / "pump-catalog.pdf"])
