from __future__ import annotations

import re
import sqlite3
from collections.abc import Sequence
from pathlib import Path

import numpy as np

from pagelens.domain.models import (
    BoundingBox,
    CollectionStats,
    Document,
    FloatArray,
    IndexedRegion,
    SearchResult,
)

SCHEMA_VERSION = 1


class SQLiteRegionStore:
    def __init__(self, path: Path) -> None:
        self._path = path

    def _connect(self) -> sqlite3.Connection:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self._path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS collection_meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    source_path TEXT NOT NULL UNIQUE,
                    content_hash TEXT NOT NULL,
                    page_count INTEGER NOT NULL,
                    embedding_model TEXT NOT NULL,
                    indexed_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS regions (
                    id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                    page INTEGER NOT NULL,
                    bbox_json TEXT NOT NULL,
                    text TEXT NOT NULL,
                    preview_path TEXT NOT NULL,
                    vector BLOB NOT NULL
                );
                CREATE INDEX IF NOT EXISTS regions_document ON regions(document_id);
                CREATE VIRTUAL TABLE IF NOT EXISTS region_fts USING fts5(
                    region_id UNINDEXED,
                    text,
                    tokenize='unicode61'
                );
                """
            )
            connection.execute(
                "INSERT OR IGNORE INTO collection_meta(key, value) VALUES ('schema_version', ?)",
                (str(SCHEMA_VERSION),),
            )

    def replace_document(
        self,
        document: Document,
        regions: Sequence[IndexedRegion],
    ) -> None:
        self.initialize()
        with self._connect() as connection:
            previous = connection.execute(
                "SELECT id FROM documents WHERE source_path = ?", (str(document.source_path),)
            ).fetchone()
            if previous:
                old_ids = connection.execute(
                    "SELECT id FROM regions WHERE document_id = ?", (previous["id"],)
                ).fetchall()
                connection.executemany(
                    "DELETE FROM region_fts WHERE region_id = ?",
                    ((row["id"],) for row in old_ids),
                )
                connection.execute("DELETE FROM documents WHERE id = ?", (previous["id"],))

            connection.execute(
                """
                INSERT INTO documents(
                    id, source_path, content_hash, page_count, embedding_model, indexed_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    document.id,
                    str(document.source_path),
                    document.content_hash,
                    document.page_count,
                    document.embedding_model,
                    document.indexed_at.isoformat(),
                ),
            )
            for indexed in regions:
                region = indexed.region
                vector = np.asarray(indexed.vector, dtype=np.float32)
                connection.execute(
                    """
                    INSERT INTO regions(
                        id, document_id, page, bbox_json, text, preview_path, vector
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        region.id,
                        region.document_id,
                        region.page,
                        region.bbox.model_dump_json(),
                        region.text,
                        str(region.preview_path),
                        vector.tobytes(),
                    ),
                )
                connection.execute(
                    "INSERT INTO region_fts(region_id, text) VALUES (?, ?)",
                    (region.id, region.text),
                )

    def search(
        self,
        query_vectors: FloatArray,
        query_text: str | None,
        embedding_model: str,
        limit: int,
    ) -> list[SearchResult]:
        self.initialize()
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT r.*, d.source_path
                FROM regions r
                JOIN documents d ON d.id = r.document_id
                WHERE d.embedding_model = ?
                """,
                (embedding_model,),
            ).fetchall()
            lexical_ranks = self._lexical_ranks(connection, query_text, embedding_model)

        query_vectors = _normalize_rows(query_vectors)
        results: list[SearchResult] = []
        for row in rows:
            vector = np.frombuffer(row["vector"], dtype=np.float32)
            if vector.shape[0] != query_vectors.shape[1]:
                continue
            visual_score = float(np.max(query_vectors @ vector))
            results.append(
                SearchResult(
                    region_id=str(row["id"]),
                    source_path=Path(row["source_path"]),
                    page=int(row["page"]),
                    bbox=BoundingBox.model_validate_json(row["bbox_json"]),
                    text=str(row["text"]),
                    preview_path=Path(row["preview_path"]),
                    visual_score=visual_score,
                    lexical_rank=lexical_ranks.get(str(row["id"])),
                )
            )
        results.sort(key=lambda result: result.score, reverse=True)
        return results[:limit]

    def _lexical_ranks(
        self,
        connection: sqlite3.Connection,
        query_text: str | None,
        embedding_model: str,
    ) -> dict[str, int]:
        expression = _fts_expression(query_text)
        if not expression:
            return {}
        rows = connection.execute(
            """
            SELECT f.region_id, bm25(region_fts) AS rank_score
            FROM region_fts f
            JOIN regions r ON r.id = f.region_id
            JOIN documents d ON d.id = r.document_id
            WHERE region_fts MATCH ? AND d.embedding_model = ?
            ORDER BY rank_score
            """,
            (expression, embedding_model),
        ).fetchall()
        return {str(row["region_id"]): rank for rank, row in enumerate(rows, start=1)}

    def stats(self) -> CollectionStats:
        self.initialize()
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) AS documents, COALESCE(SUM(page_count), 0) AS pages
                FROM documents
                """
            ).fetchone()
            assert row is not None
            region_row = connection.execute("SELECT COUNT(*) FROM regions").fetchone()
            assert region_row is not None
            region_count = region_row[0]
            models = connection.execute(
                "SELECT DISTINCT embedding_model FROM documents ORDER BY embedding_model"
            ).fetchall()
        return CollectionStats(
            documents=int(row["documents"]),
            pages=int(row["pages"]),
            regions=int(region_count),
            embedding_models=tuple(str(model[0]) for model in models),
        )


def _normalize_rows(vectors: FloatArray) -> FloatArray:
    vectors = np.asarray(vectors, dtype=np.float32)
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return (vectors / np.maximum(norms, 1e-12)).astype(np.float32)


def _fts_expression(query: str | None) -> str | None:
    if not query:
        return None
    tokens = re.findall(r"[^\W_]+(?:[-.][^\W_]+)*", query, flags=re.UNICODE)
    if not tokens:
        return None
    return " OR ".join(f'"{token}"' for token in tokens)
