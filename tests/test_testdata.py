from __future__ import annotations

import json
from pathlib import Path

import pymupdf

ROOT = Path(__file__).parents[1]
MANUALS = ROOT / "testdata" / "manuals"


def test_ground_truth_references_existing_pages() -> None:
    truth = json.loads((ROOT / "testdata" / "ground-truth.json").read_text())

    for filename, document_truth in truth["documents"].items():
        path = MANUALS / filename
        assert path.is_file()
        with pymupdf.open(path) as document:
            for page in document_truth["pages"]:
                assert 1 <= int(page) <= document.page_count


def test_corpus_covers_text_absence_and_presence() -> None:
    with pymupdf.open(MANUALS / "image-only-scan.pdf") as document:
        assert document[0].get_text().strip() == ""

    with pymupdf.open(MANUALS / "service-bulletin.pdf") as document:
        assert "pump" not in document[0].get_text().casefold()
        assert "water pump" in document[1].get_text().casefold()

    with pymupdf.open(MANUALS / "vehicle-catalog.pdf") as document:
        assert "motorcycle" not in document[0].get_text().casefold()


def test_ground_truth_distinguishes_visual_text_and_broad_queries() -> None:
    truth = json.loads((ROOT / "testdata" / "ground-truth.json").read_text())
    scenarios = {scenario["id"]: scenario for scenario in truth["queries"]}

    visual = scenarios["water-pumps-visual"]
    any_evidence = scenarios["water-pumps-any-evidence"]
    broad = scenarios["pump-visual-broad"]

    assert ["service-bulletin.pdf", 2] in visual["must_not_confirm"]
    assert ["service-bulletin.pdf", 2] in any_evidence["relevant"]
    assert ["pump-catalog.pdf", 3] in visual["must_not_confirm"]
    assert ["pump-catalog.pdf", 3] in broad["relevant"]
