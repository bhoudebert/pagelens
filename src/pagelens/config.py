from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Settings:
    data_dir: Path
    embedding_model: str
    ollama_model: str
    ollama_url: str
    render_dpi: int
    tile_size: int
    tile_overlap: int

    @classmethod
    def from_env(cls, data_dir: Path | None = None) -> Settings:
        return cls(
            data_dir=data_dir or Path(os.getenv("PAGELENS_DATA_DIR", ".pagelens")).expanduser(),
            embedding_model=os.getenv(
                "PAGELENS_EMBEDDING_MODEL",
                "embeddinggemma-2:440m-q8_0-text-vision",
            ),
            ollama_model=os.getenv("PAGELENS_OLLAMA_MODEL", "qwen3-vl:8b-instruct"),
            ollama_url=os.getenv("PAGELENS_OLLAMA_URL", "http://127.0.0.1:11434"),
            render_dpi=int(os.getenv("PAGELENS_RENDER_DPI", "144")),
            tile_size=int(os.getenv("PAGELENS_TILE_SIZE", "768")),
            tile_overlap=int(os.getenv("PAGELENS_TILE_OVERLAP", "128")),
        )

    @property
    def database_path(self) -> Path:
        return self.data_dir / "index.sqlite3"

    @property
    def preview_dir(self) -> Path:
        return self.data_dir / "previews"

    def ensure_directories(self) -> None:
        self.preview_dir.mkdir(parents=True, exist_ok=True)
