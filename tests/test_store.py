from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from pagelens.adapters.store_sqlite import SQLiteRegionStore, _fts_expression
from pagelens.domain.models import BoundingBox, Document, DraftRegion, IndexedRegion


def _document(identifier: str, source: Path) -> Document:
    return Document(
        id=identifier,
        source_path=source,
        content_hash=f"hash-{identifier}",
        page_count=1,
        embedding_model="test-model",
        indexed_at=datetime.now(UTC),
    )


def _region(identifier: str, document_id: str, text: str, vector: list[float]) -> IndexedRegion:
    return IndexedRegion(
        region=DraftRegion(
            id=identifier,
            document_id=document_id,
            page=1,
            bbox=BoundingBox(x0=0, y0=0, x1=1, y1=1),
            text=text,
            preview_path=Path(f"{identifier}.jpg"),
        ),
        vector=np.array(vector, dtype=np.float32),
    )


def test_store_combines_visual_and_lexical_search(tmp_path: Path) -> None:
    store = SQLiteRegionStore(tmp_path / "index.sqlite3")
    document = _document("doc-1", tmp_path / "catalog.pdf")
    store.replace_document(
        document,
        [
            _region("pump", document.id, "WP-450 centrifugal water pump", [1.0, 0.0]),
            _region("chair", document.id, "wooden chair", [0.0, 1.0]),
        ],
    )

    results = store.search(
        query_vectors=np.array([[0.9, 0.1]], dtype=np.float32),
        query_text="water pump",
        embedding_model="test-model",
        limit=2,
    )

    assert [result.region_id for result in results] == ["pump", "chair"]
    assert results[0].lexical_rank == 1
    assert results[0].visual_score > results[1].visual_score


def test_reingestion_replaces_document_at_same_path(tmp_path: Path) -> None:
    store = SQLiteRegionStore(tmp_path / "index.sqlite3")
    source = tmp_path / "catalog.pdf"
    first = _document("old", source)
    second = _document("new", source)
    store.replace_document(first, [_region("old-region", first.id, "old", [1.0, 0.0])])
    store.replace_document(second, [_region("new-region", second.id, "new", [0.0, 1.0])])

    stats = store.stats()
    results = store.search(
        query_vectors=np.array([[0.0, 1.0]], dtype=np.float32),
        query_text=None,
        embedding_model="test-model",
        limit=10,
    )

    assert stats.documents == 1
    assert stats.regions == 1
    assert [result.region_id for result in results] == ["new-region"]


def test_fts_expression_is_safe_for_punctuation() -> None:
    assert _fts_expression('CB750 "Hornet" + pump') == '"CB750" OR "Hornet" OR "pump"'
