from pathlib import Path

import pymupdf

from pagelens.adapters.pdf_pymupdf import PyMuPdfRegionExtractor, _axis_positions


def test_axis_positions_cover_final_edge() -> None:
    assert _axis_positions(1000, 400, 100) == [0, 300, 600]
    assert _axis_positions(1050, 400, 100) == [0, 300, 600, 650]
    assert _axis_positions(300, 400, 100) == [0]


def test_extractor_renders_tiles_and_associates_text(tmp_path: Path) -> None:
    pdf_path = tmp_path / "manual.pdf"
    document = pymupdf.open()
    page = document.new_page(width=300, height=300)
    page.insert_text((30, 40), "WP-450 WATER PUMP")
    document.save(pdf_path)
    document.close()

    extractor = PyMuPdfRegionExtractor(dpi=72, tile_size=200, overlap=50, enable_ocr=False)
    indexed_document, regions = extractor.extract(pdf_path, tmp_path / "previews", "test-model")

    assert indexed_document.page_count == 1
    assert len(regions) == 4
    assert any("WP-450 WATER PUMP" in region.text for region in regions)
    assert all(region.preview_path.is_file() for region in regions)
    assert all(region.page == 1 for region in regions)
