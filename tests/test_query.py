from collections.abc import Sequence
from pathlib import Path

import numpy as np
import pytest
from numpy.typing import NDArray

from pagelens.application.query import SearchCollection
from pagelens.domain.models import (
    BoundingBox,
    CollectionStats,
    Document,
    IndexedRegion,
    SearchResult,
)


class FakeEmbedder:
    model_id = "fake"

    def embed_texts(self, texts: Sequence[str]) -> NDArray[np.float32]:
        return np.array([[1.0, 0.0] for _ in texts], dtype=np.float32)

    def embed_images(self, images: Sequence[Path]) -> NDArray[np.float32]:
        return np.array([[0.0, 1.0] for _ in images], dtype=np.float32)


class RecordingStore:
    query_vectors: NDArray[np.float32] | None = None
    requested_limit: int | None = None
    results: list[SearchResult]

    def __init__(self, results: list[SearchResult] | None = None) -> None:
        self.results = results or []

    def initialize(self) -> None:
        pass

    def replace_document(self, document: Document, regions: Sequence[IndexedRegion]) -> None:
        raise NotImplementedError

    def search(
        self,
        query_vectors: NDArray[np.float32],
        query_text: str | None,
        embedding_model: str,
        limit: int,
    ) -> list[SearchResult]:
        self.query_vectors = query_vectors
        self.requested_limit = limit
        return self.results[:limit]

    def stats(self) -> CollectionStats:
        return CollectionStats(0, 0, 0, ())


def _result(identifier: str, pdf: str, page: int, score: float) -> SearchResult:
    return SearchResult(
        region_id=identifier,
        source_path=Path(pdf),
        page=page,
        bbox=BoundingBox(x0=0, y0=0, x1=1, y1=1),
        text="evidence",
        preview_path=Path(f"{identifier}.jpg"),
        visual_score=score,
    )


def test_query_combines_text_and_each_reference_image(tmp_path: Path) -> None:
    image_a = tmp_path / "a.jpg"
    image_b = tmp_path / "b.jpg"
    image_a.touch()
    image_b.touch()
    store = RecordingStore()

    SearchCollection(FakeEmbedder(), store).execute(
        text="same motorcycle",
        images=[image_a, image_b],
        limit=10,
    )

    assert store.query_vectors is not None
    assert store.query_vectors.shape == (3, 2)
    np.testing.assert_array_equal(store.query_vectors[0], [1.0, 0.0])
    np.testing.assert_array_equal(store.query_vectors[1], [0.0, 1.0])
    assert store.requested_limit == 120


def test_query_requires_at_least_one_modality() -> None:
    with pytest.raises(ValueError, match="provide query text"):
        SearchCollection(FakeEmbedder(), RecordingStore()).execute(None, [], 10)


def test_query_returns_best_region_per_page_by_default() -> None:
    store = RecordingStore(
        [
            _result("best", "manual.pdf", 2, 0.9),
            _result("overlap", "manual.pdf", 2, 0.8),
            _result("other", "manual.pdf", 4, 0.7),
        ]
    )

    results = SearchCollection(FakeEmbedder(), store).execute("pump", [], 10)

    assert [result.region_id for result in results] == ["best", "other"]


def test_query_can_return_all_regions_for_debugging() -> None:
    store = RecordingStore(
        [
            _result("best", "manual.pdf", 2, 0.9),
            _result("overlap", "manual.pdf", 2, 0.8),
        ]
    )

    results = SearchCollection(FakeEmbedder(), store).execute("pump", [], 10, group_by_page=False)

    assert [result.region_id for result in results] == ["best", "overlap"]
    assert store.requested_limit == 10


def test_verification_requires_text(tmp_path: Path) -> None:
    image = tmp_path / "example.jpg"
    image.touch()
    with pytest.raises(ValueError, match="requires text"):
        SearchCollection(FakeEmbedder(), RecordingStore()).execute(None, [image], 10, verify=True)
