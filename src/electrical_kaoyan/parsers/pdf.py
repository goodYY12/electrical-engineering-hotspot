from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


@dataclass(frozen=True)
class PdfExtraction:
    pages: tuple[str, ...]
    tables: tuple[tuple[tuple[str | None, ...], ...], ...]
    needs_ocr: bool


def extract_pdf(path: Path) -> PdfExtraction:
    reader = PdfReader(str(path))
    pages = tuple((page.extract_text() or "").strip() for page in reader.pages)
    character_count = sum(len(page) for page in pages)
    tables: list[tuple[tuple[str | None, ...], ...]] = []
    try:
        import pdfplumber
        with pdfplumber.open(path) as document:
            for page in document.pages:
                for table in page.extract_tables() or []:
                    tables.append(tuple(tuple(cell for cell in row) for row in table))
    except ImportError:
        pass
    return PdfExtraction(pages=pages, tables=tuple(tables), needs_ocr=character_count < 20)
