import json
from collections.abc import Sequence
from pathlib import Path

import numpy as np
import pytest
from numpy.typing import NDArray
from typer.testing import CliRunner

from pagelens import cli

MANUALS = Path(__file__).parent.parent / "testdata" / "manuals"
GROUND_TRUTH = Path(__file__).parent.parent / "testdata" / "ground-truth.json"


class ConstantEmbedder:
    def __init__(self, base_url: str, model_id: str) -> None:
        self.model_id = model_id

    def embed_texts(self, texts: Sequence[str]) -> NDArray[np.float32]:
        return np.ones((len(texts), 4), dtype=np.float32)

    def embed_images(self, images: Sequence[Path]) -> NDArray[np.float32]:
        return np.ones((len(images), 4), dtype=np.float32)


@pytest.fixture(autouse=True)
def offline_embedder(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "OllamaMultimodalEmbedder", ConstantEmbedder)


def test_ingest_then_query_returns_grounded_json(tmp_path: Path) -> None:
    runner = CliRunner()
    data_dir = str(tmp_path / "collection")

    ingested = runner.invoke(
        cli.app, ["ingest", str(MANUALS / "pump-catalog.pdf"), "--no-ocr", "--data-dir", data_dir]
    )
    queried = runner.invoke(
        cli.app, ["query", "water pump", "--json", "--limit", "3", "--data-dir", data_dir]
    )

    assert ingested.exit_code == 0, ingested.output
    assert queried.exit_code == 0, queried.output
    results = json.loads(queried.stdout)
    assert len(results) == 3
    assert {"pdf", "page", "bbox", "score", "preview"} <= results[0].keys()
    assert all(result["page"] >= 1 for result in results)


def test_query_without_text_or_image_fails_with_usage_error(tmp_path: Path) -> None:
    result = CliRunner().invoke(cli.app, ["query", "--data-dir", str(tmp_path)])
    assert result.exit_code == 2
    assert "provide query text" in result.output


def test_ingest_rejects_directory_without_pdfs(tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    result = CliRunner().invoke(cli.app, ["ingest", str(empty), "--data-dir", str(tmp_path)])
    assert result.exit_code == 2
    assert "no PDFs found" in result.output


def test_evaluate_rejects_unknown_scenario(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        cli.app,
        ["evaluate", str(GROUND_TRUTH), "--scenario", "nope", "--data-dir", str(tmp_path)],
    )
    assert result.exit_code == 2
    assert "unknown scenario" in result.output
