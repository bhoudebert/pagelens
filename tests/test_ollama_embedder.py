from __future__ import annotations

import io
import json
from pathlib import Path
from unittest.mock import patch

import numpy as np

from pagelens.adapters.embedding_ollama import OllamaMultimodalEmbedder


def test_embeds_text_with_search_instruction() -> None:
    response = io.BytesIO(json.dumps({"embeddings": [[3.0, 4.0]]}).encode())

    with patch("urllib.request.urlopen", return_value=response) as urlopen:
        vectors = OllamaMultimodalEmbedder("http://ollama", "embed-model").embed_texts(
            ["water pump"]
        )

    request = urlopen.call_args.args[0]
    payload = json.loads(request.data)
    assert payload["model"] == "embed-model"
    assert payload["input"] == ["task: search result | query: water pump"]
    np.testing.assert_allclose(vectors, [[0.6, 0.8]])


def test_embeds_image_as_base64(tmp_path: Path) -> None:
    image = tmp_path / "region.jpg"
    image.write_bytes(b"image bytes")
    response = io.BytesIO(json.dumps({"embeddings": [[1.0, 0.0]]}).encode())

    with patch("urllib.request.urlopen", return_value=response) as urlopen:
        vectors = OllamaMultimodalEmbedder("http://ollama", "embed-model").embed_images([image])

    request = urlopen.call_args.args[0]
    payload = json.loads(request.data)
    assert "image" in payload["input"][0]
    np.testing.assert_allclose(vectors, [[1.0, 0.0]])
