from __future__ import annotations

import base64
import json
import urllib.error
import urllib.request
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import numpy as np

from pagelens.domain.models import FloatArray


class OllamaMultimodalEmbedder:
    """Shared text/image embeddings through Ollama's multimodal embed API."""

    def __init__(
        self,
        base_url: str,
        model_id: str,
        timeout: float = 120.0,
        batch_size: int = 8,
    ) -> None:
        self._endpoint = f"{base_url.rstrip('/')}/api/embed"
        self._model_id = model_id
        self._timeout = timeout
        self._batch_size = batch_size

    @property
    def model_id(self) -> str:
        return self._model_id

    def embed_texts(self, texts: Sequence[str]) -> FloatArray:
        inputs = [f"task: search result | query: {text}" for text in texts]
        return self._embed_batches(inputs)

    def embed_images(self, images: Sequence[Path]) -> FloatArray:
        inputs: list[dict[str, str]] = []
        for path in images:
            encoded = base64.b64encode(path.read_bytes()).decode("ascii")
            inputs.append({"image": encoded})
        return self._embed_batches(inputs)

    def _embed_batches(self, inputs: Sequence[Any]) -> FloatArray:
        vectors: list[FloatArray] = []
        for offset in range(0, len(inputs), self._batch_size):
            batch = list(inputs[offset : offset + self._batch_size])
            payload = self._request(batch)
            raw_vectors = payload.get("embeddings")
            if not isinstance(raw_vectors, list) or len(raw_vectors) != len(batch):
                raise RuntimeError("Ollama returned an invalid number of embeddings")
            vectors.append(_normalize(np.asarray(raw_vectors, dtype=np.float32)))
        return np.concatenate(vectors) if vectors else np.empty((0, 0), dtype=np.float32)

    def _request(self, inputs: list[Any]) -> dict[str, Any]:
        body = json.dumps(
            {
                "model": self._model_id,
                "input": inputs,
                "dimensions": 768,
                "truncate": True,
                "keep_alive": "5m",
            }
        ).encode()
        request = urllib.request.Request(
            self._endpoint,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                payload = json.load(response)
        except (urllib.error.URLError, TimeoutError) as error:
            raise RuntimeError(f"Ollama embedding request failed: {error}") from error
        if not isinstance(payload, dict):
            raise RuntimeError("Ollama returned an invalid embedding response")
        return payload


def _normalize(vectors: FloatArray) -> FloatArray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return (vectors / np.maximum(norms, 1e-12)).astype(np.float32)
