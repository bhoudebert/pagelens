from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Literal

import numpy as np
from numpy.typing import NDArray
from pydantic import BaseModel, ConfigDict, Field

FloatArray = NDArray[np.float32]


class EvidenceMode(StrEnum):
    """Evidence that may satisfy a verified query."""

    VISUAL = "visual"
    ANY = "any"


class BoundingBox(BaseModel):
    """A normalized page-relative rectangle."""

    model_config = ConfigDict(frozen=True)

    x0: float = Field(ge=0.0, le=1.0)
    y0: float = Field(ge=0.0, le=1.0)
    x1: float = Field(ge=0.0, le=1.0)
    y1: float = Field(ge=0.0, le=1.0)


@dataclass(frozen=True, slots=True)
class Document:
    id: str
    source_path: Path
    content_hash: str
    page_count: int
    embedding_model: str
    indexed_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class DraftRegion:
    id: str
    document_id: str
    page: int
    bbox: BoundingBox
    text: str
    preview_path: Path


@dataclass(frozen=True, slots=True)
class IndexedRegion:
    region: DraftRegion
    vector: FloatArray


class Verification(BaseModel):
    status: Literal["confirmed", "rejected", "uncertain"]
    evidence_source: Literal["visual", "text", "both", "none"] = "none"
    object_type: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    reference: str | None = None
    evidence: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)


@dataclass(frozen=True, slots=True)
class SearchResult:
    region_id: str
    source_path: Path
    page: int
    bbox: BoundingBox
    text: str
    preview_path: Path
    visual_score: float
    lexical_rank: int | None = None
    verification: Verification | None = None

    @property
    def score(self) -> float:
        """Fuse visual similarity with a deliberately small exact-text boost."""
        if self.lexical_rank is None:
            return self.visual_score
        return self.visual_score + 0.05 / self.lexical_rank


@dataclass(frozen=True, slots=True)
class CollectionStats:
    documents: int
    pages: int
    regions: int
    embedding_models: tuple[str, ...]
