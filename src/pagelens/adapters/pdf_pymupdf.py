from __future__ import annotations

import hashlib
from pathlib import Path

import pymupdf
from PIL import Image

from pagelens.domain.models import BoundingBox, Document, DraftRegion


class PyMuPdfRegionExtractor:
    def __init__(
        self,
        dpi: int = 144,
        tile_size: int = 768,
        overlap: int = 128,
        enable_ocr: bool = True,
    ) -> None:
        if dpi < 72:
            raise ValueError("dpi must be at least 72")
        if tile_size < 128:
            raise ValueError("tile size must be at least 128 pixels")
        if overlap < 0 or overlap >= tile_size:
            raise ValueError("overlap must be non-negative and smaller than tile size")
        self._dpi = dpi
        self._tile_size = tile_size
        self._overlap = overlap
        self._enable_ocr = enable_ocr

    def extract(
        self,
        source: Path,
        preview_root: Path,
        embedding_model: str,
    ) -> tuple[Document, list[DraftRegion]]:
        source = source.resolve()
        content_hash = _sha256_file(source)
        document_id = hashlib.sha256(f"{source}\0{content_hash}".encode()).hexdigest()[:24]
        output_dir = preview_root / document_id
        output_dir.mkdir(parents=True, exist_ok=True)

        regions: list[DraftRegion] = []
        with pymupdf.open(source) as pdf:  # type: ignore[no-untyped-call]
            document = Document(
                id=document_id,
                source_path=source,
                content_hash=content_hash,
                page_count=pdf.page_count,
                embedding_model=embedding_model,
            )
            for page_index, page in enumerate(pdf):
                pixmap = page.get_pixmap(dpi=self._dpi, alpha=False)
                page_image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
                text_blocks = _text_blocks(page, self._enable_ocr)
                tiles = _tiles(pixmap.width, pixmap.height, self._tile_size, self._overlap)
                for region_index, pixel_box in enumerate(tiles):
                    preview_path = output_dir / f"p{page_index + 1:05d}-r{region_index:03d}.jpg"
                    page_image.crop(pixel_box).save(preview_path, format="JPEG", quality=90)
                    pdf_box = (
                        pixel_box[0] * 72 / self._dpi,
                        pixel_box[1] * 72 / self._dpi,
                        pixel_box[2] * 72 / self._dpi,
                        pixel_box[3] * 72 / self._dpi,
                    )
                    region_text = _intersecting_text(text_blocks, pdf_box)
                    normalized = BoundingBox(
                        x0=pixel_box[0] / pixmap.width,
                        y0=pixel_box[1] / pixmap.height,
                        x1=pixel_box[2] / pixmap.width,
                        y1=pixel_box[3] / pixmap.height,
                    )
                    region_id = hashlib.sha256(
                        f"{document_id}:{page_index + 1}:{pixel_box}".encode()
                    ).hexdigest()[:32]
                    regions.append(
                        DraftRegion(
                            id=region_id,
                            document_id=document_id,
                            page=page_index + 1,
                            bbox=normalized,
                            text=region_text,
                            preview_path=preview_path,
                        )
                    )
        return document, regions


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _axis_positions(length: int, tile_size: int, overlap: int) -> list[int]:
    if length <= tile_size:
        return [0]
    stride = tile_size - overlap
    positions = list(range(0, length - tile_size + 1, stride))
    final = length - tile_size
    if positions[-1] != final:
        positions.append(final)
    return positions


def _tiles(
    width: int, height: int, tile_size: int, overlap: int
) -> list[tuple[int, int, int, int]]:
    x_positions = _axis_positions(width, tile_size, overlap)
    y_positions = _axis_positions(height, tile_size, overlap)
    return [
        (x, y, min(x + tile_size, width), min(y + tile_size, height))
        for y in y_positions
        for x in x_positions
    ]


def _text_blocks(
    page: pymupdf.Page, enable_ocr: bool
) -> list[tuple[float, float, float, float, str]]:
    raw_blocks = page.get_text("blocks")  # type: ignore[no-untyped-call]
    if enable_ocr and not any(str(block[4]).strip() for block in raw_blocks):
        try:
            textpage = page.get_textpage_ocr(dpi=300, full=True)  # type: ignore[no-untyped-call]
            raw_blocks = page.get_text("blocks", textpage=textpage)  # type: ignore[no-untyped-call]
        except RuntimeError:
            # Visual retrieval remains available when Tesseract is not configured.
            pass
    blocks: list[tuple[float, float, float, float, str]] = []
    for block in raw_blocks:
        text = str(block[4]).strip()
        if text:
            blocks.append(
                (
                    float(block[0]),
                    float(block[1]),
                    float(block[2]),
                    float(block[3]),
                    text,
                )
            )
    return blocks


def _intersecting_text(
    blocks: list[tuple[float, float, float, float, str]],
    region: tuple[float, float, float, float],
) -> str:
    x0, y0, x1, y1 = region
    selected = [
        block
        for block in blocks
        if block[0] < x1 and block[2] > x0 and block[1] < y1 and block[3] > y0
    ]
    selected.sort(key=lambda block: (round(block[1], 1), block[0]))
    return "\n".join(block[4] for block in selected)
