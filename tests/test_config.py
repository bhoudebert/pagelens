from pathlib import Path

import pytest

from pagelens.config import Settings


def test_default_verifier_is_vision_capable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("PAGELENS_OLLAMA_MODEL", raising=False)
    settings = Settings.from_env(tmp_path)

    assert settings.ollama_model == "qwen3-vl:8b-instruct"


def test_default_embedder_is_multimodal(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("PAGELENS_EMBEDDING_MODEL", raising=False)
    settings = Settings.from_env(tmp_path)

    assert settings.embedding_model == "embeddinggemma-2:440m-q8_0-text-vision"
