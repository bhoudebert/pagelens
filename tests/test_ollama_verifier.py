from __future__ import annotations

import io
import json
from pathlib import Path
from unittest.mock import patch

import pymupdf

from pagelens.adapters.ollama import OllamaVerifier
from pagelens.domain.models import BoundingBox, EvidenceMode, SearchResult


def test_verifier_receives_crop_and_one_based_full_page(tmp_path: Path) -> None:
    pdf_path = tmp_path / "manual.pdf"
    document = pymupdf.open()
    document.new_page().insert_text((72, 72), "MOTORCYCLE")
    document.save(pdf_path)
    document.close()
    preview = tmp_path / "crop.jpg"
    preview.write_bytes(b"crop")
    candidate = SearchResult(
        region_id="region",
        source_path=pdf_path,
        page=1,
        bbox=BoundingBox(x0=0, y0=0, x1=1, y1=1),
        text="HX-750 street model",
        preview_path=preview,
        visual_score=0.8,
    )
    verification = {
        "status": "confirmed",
        "evidence_source": "visual",
        "object_type": "motorcycle",
        "manufacturer": None,
        "model": "HX-750",
        "reference": None,
        "evidence": ["A motorcycle is clearly visible."],
        "confidence": 0.98,
    }
    response = io.BytesIO(json.dumps({"message": {"content": json.dumps(verification)}}).encode())

    with patch("urllib.request.urlopen", return_value=response) as urlopen:
        result = OllamaVerifier("http://ollama", "vision-model").verify("motorcycle", candidate)

    request = urlopen.call_args.args[0]
    payload = json.loads(request.data)
    assert len(payload["messages"][0]["images"]) == 2
    assert "broad category" in payload["messages"][0]["content"]
    assert "text-only mention does not count" in payload["messages"][0]["content"]
    assert result.status == "confirmed"


def test_any_evidence_mode_allows_explicit_page_text(tmp_path: Path) -> None:
    pdf_path = tmp_path / "manual.pdf"
    document = pymupdf.open()
    document.new_page().insert_text((72, 72), "Water pump replacement procedure")
    document.save(pdf_path)
    document.close()
    preview = tmp_path / "crop.jpg"
    preview.write_bytes(b"crop")
    candidate = SearchResult(
        region_id="region",
        source_path=pdf_path,
        page=1,
        bbox=BoundingBox(x0=0, y0=0, x1=1, y1=1),
        text="Water pump replacement procedure",
        preview_path=preview,
        visual_score=0.8,
    )
    verification = {
        "status": "confirmed",
        "evidence_source": "text",
        "object_type": "water pump",
        "manufacturer": None,
        "model": None,
        "reference": None,
        "evidence": ["The procedure explicitly names a water pump."],
        "confidence": 0.95,
    }
    response = io.BytesIO(json.dumps({"message": {"content": json.dumps(verification)}}).encode())

    with patch("urllib.request.urlopen", return_value=response) as urlopen:
        OllamaVerifier("http://ollama", "vision-model", evidence_mode=EvidenceMode.ANY).verify(
            "water pump", candidate
        )

    request = urlopen.call_args.args[0]
    prompt = json.loads(request.data)["messages"][0]["content"]
    assert "Evidence policy (any)" in prompt
    assert "supplied page text" in prompt


def test_visual_policy_rejects_a_text_only_model_confirmation(tmp_path: Path) -> None:
    pdf_path = tmp_path / "manual.pdf"
    document = pymupdf.open()
    document.new_page().insert_text((72, 72), "Water pump replacement procedure")
    document.save(pdf_path)
    document.close()
    preview = tmp_path / "crop.jpg"
    preview.write_bytes(b"crop")
    candidate = SearchResult(
        region_id="region",
        source_path=pdf_path,
        page=1,
        bbox=BoundingBox(x0=0, y0=0, x1=1, y1=1),
        text="Water pump replacement procedure",
        preview_path=preview,
        visual_score=0.8,
    )
    verification = {
        "status": "confirmed",
        "evidence_source": "text",
        "object_type": "water pump",
        "manufacturer": None,
        "model": None,
        "reference": None,
        "evidence": ["The page says water pump."],
        "confidence": 0.99,
    }
    response = io.BytesIO(json.dumps({"message": {"content": json.dumps(verification)}}).encode())

    with patch("urllib.request.urlopen", return_value=response):
        result = OllamaVerifier("http://ollama", "vision-model").verify("water pump", candidate)

    assert result.status == "rejected"
    assert result.evidence_source == "text"
