from __future__ import annotations

from pathlib import Path

from app.schemas import ExtractionResult
from app.services.image_ocr import (
    OCRProcessingError,
    OCRUnavailableError,
    extract_from_image,
)
from app.services.pdf_service import PDFProcessingError, extract_from_pdf


class DocumentProcessingError(RuntimeError):
    pass


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def extract_document_from_path(path: Path) -> ExtractionResult:
    if not path.exists():
        raise DocumentProcessingError("Le fichier importe enregistre est introuvable.")

    if path.stat().st_size == 0:
        raise DocumentProcessingError("Le fichier importe est vide.")

    suffix = path.suffix.lower()

    try:
        if suffix in IMAGE_EXTENSIONS:
            return extract_from_image(path)
        if suffix == ".pdf":
            return extract_from_pdf(path)

        return ExtractionResult(
            filename=path.name,
            document_type="unknown",
            extracted_text="",
            rows=[],
            confidence=0.0,
        )
    except (OCRUnavailableError, OCRProcessingError, PDFProcessingError) as exc:
        raise DocumentProcessingError(str(exc)) from exc
    except Exception as exc:
        raise DocumentProcessingError(f"Echec du traitement du document : {exc}") from exc