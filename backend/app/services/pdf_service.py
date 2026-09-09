from __future__ import annotations

from pathlib import Path
from statistics import mean

from PIL import Image
import pdfplumber

from app.schemas import ExtractionResult, TableCell, TableRow
from app.services.image_ocr import (
    OCRProcessingError,
    OCRUnavailableError,
    run_ocr_on_pil_image,
)
from app.services.table_builder import (
    average_confidence,
    build_rows_from_text,
    build_rows_from_word_blocks,
)


class PDFProcessingError(RuntimeError):
    pass


def _rows_from_pdf_tables(tables: list[list[list[str | None]]]) -> list[TableRow]:
    rows: list[TableRow] = []
    next_row_index = 0

    for table in tables:
        for raw_row in table:
            if not raw_row:
                continue

            normalized = [(cell or "").strip() for cell in raw_row]
            if not any(normalized):
                continue

            cells = [
                TableCell(
                    row_index=next_row_index,
                    col_index=col_index,
                    text=value,
                    confidence=0.95,
                )
                for col_index, value in enumerate(normalized)
            ]
            rows.append(TableRow(row_index=next_row_index, cells=cells))
            next_row_index += 1

    return rows


def _render_page_to_pil(page: object) -> Image.Image:
    render_topil = getattr(page, "render_topil", None)
    if callable(render_topil):
        return render_topil(scale=2)

    render = getattr(page, "render", None)
    if callable(render):
        rendered = render(scale=2)
        for method_name in ("to_pil", "to_pil_image", "to_image"):
            converter = getattr(rendered, method_name, None)
            if callable(converter):
                return converter()

    raise PDFProcessingError("Impossible de restituer la page PDF pour la solution OCR de secours.")


def _render_pdf_pages(path: Path) -> list[Image.Image]:
    try:
        import pypdfium2 as pdfium
    except ImportError as exc:
        raise PDFProcessingError(
            "La solution OCR de secours pour les PDF numerises necessite pypdfium2. "
            "Installez-le avec : pip install pypdfium2"
        ) from exc

    images: list[Image.Image] = []
    pdf = pdfium.PdfDocument(str(path))
    try:
        for page_index in range(len(pdf)):
            page = pdf.get_page(page_index)
            try:
                pil_image = _render_page_to_pil(page)
                images.append(pil_image.convert("RGB"))
            finally:
                close_method = getattr(page, "close", None)
                if callable(close_method):
                    close_method()
    except Exception as exc:
        raise PDFProcessingError(f"Echec de la restitution des pages PDF : {exc}") from exc
    finally:
        close_pdf = getattr(pdf, "close", None)
        if callable(close_pdf):
            close_pdf()

    return images


def _reindex_rows(rows: list[TableRow], start_index: int) -> list[TableRow]:
    reindexed_rows: list[TableRow] = []

    for offset, row in enumerate(rows):
        new_row_index = start_index + offset
        cells = [
            TableCell(
                row_index=new_row_index,
                col_index=cell.col_index,
                text=cell.text,
                confidence=cell.confidence,
            )
            for cell in row.cells
        ]
        reindexed_rows.append(TableRow(row_index=new_row_index, cells=cells))

    return reindexed_rows


def _extract_using_ocr_fallback(path: Path) -> ExtractionResult:
    rendered_pages = _render_pdf_pages(path)
    all_text_parts: list[str] = []
    all_rows: list[TableRow] = []
    page_confidences: list[float] = []

    next_row_index = 0
    for image in rendered_pages:
        try:
            payload = run_ocr_on_pil_image(image)
        finally:
            image.close()

        if payload.raw_text:
            all_text_parts.append(payload.raw_text)

        page_rows = build_rows_from_word_blocks(
            payload.words,
            fallback_text=payload.raw_text,
            default_confidence=max(payload.confidence, 0.65),
        )
        page_rows = _reindex_rows(page_rows, next_row_index)
        next_row_index += len(page_rows)

        all_rows.extend(page_rows)
        page_confidences.append(payload.confidence)

    combined_text = "\n\n".join(part for part in all_text_parts if part.strip()).strip()
    overall_confidence = average_confidence(all_rows)
    if not overall_confidence and page_confidences:
        overall_confidence = max(0.0, min(1.0, mean(page_confidences)))

    return ExtractionResult(
        filename=path.name,
        document_type="scanned_pdf",
        extracted_text=combined_text,
        rows=all_rows,
        confidence=overall_confidence,
    )


def extract_from_pdf(path: Path) -> ExtractionResult:
    if not path.exists():
        raise PDFProcessingError(f"Fichier PDF introuvable : {path}")

    if path.stat().st_size == 0:
        raise PDFProcessingError("Le fichier PDF importe est vide.")

    all_text_parts: list[str] = []
    all_tables: list[list[list[str | None]]] = []

    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = (page.extract_text() or "").strip()
                if page_text:
                    all_text_parts.append(page_text)

                try:
                    page_tables = page.extract_tables() or []
                    if page_tables:
                        all_tables.extend(page_tables)
                except Exception:
                    # Table extraction can fail on some PDFs; text extraction may still work.
                    continue
    except Exception as exc:
        raise PDFProcessingError(f"Echec de la lecture du PDF : {exc}") from exc

    combined_text = "\n\n".join(part for part in all_text_parts if part).strip()

    if combined_text:
        rows = _rows_from_pdf_tables(all_tables)
        if not rows:
            rows = build_rows_from_text(combined_text, default_confidence=0.88)

        return ExtractionResult(
            filename=path.name,
            document_type="pdf",
            extracted_text=combined_text,
            rows=rows,
            confidence=average_confidence(rows),
        )

    try:
        return _extract_using_ocr_fallback(path)
    except OCRUnavailableError:
        raise
    except OCRProcessingError:
        raise
    except PDFProcessingError:
        raise
    except Exception as exc:
        raise PDFProcessingError(f"Echec de la solution OCR de secours du PDF numerise : {exc}") from exc