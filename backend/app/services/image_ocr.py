from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from statistics import mean

from PIL import Image
import pytesseract
from pytesseract import Output
from pytesseract.pytesseract import TesseractNotFoundError

from app.schemas import ExtractionResult
from app.services.table_builder import (
    OCRWordBlock,
    average_confidence,
    build_rows_from_text,
    build_rows_from_word_blocks,
)


class OCRUnavailableError(RuntimeError):
    pass


class OCRProcessingError(RuntimeError):
    pass


@dataclass
class OCRPayload:
    raw_text: str
    words: list[OCRWordBlock]
    confidence: float


def preprocess_image(image: Image.Image) -> Image.Image:
    rgb_image = image.convert("RGB")
    grayscale_image = rgb_image.convert("L")
    return grayscale_image


def _safe_int(value: object) -> int | None:
    try:
        if value is None or value == "":
            return None
        return int(float(str(value)))
    except (TypeError, ValueError):
        return None


def _normalize_tesseract_confidence(value: object) -> float:
    try:
        numeric = float(str(value))
    except (TypeError, ValueError):
        return 0.0

    if numeric < 0:
        return 0.0
    return max(0.0, min(1.0, numeric / 100.0))


def _extract_word_blocks(image: Image.Image) -> list[OCRWordBlock]:
    data = pytesseract.image_to_data(image, output_type=Output.DICT)

    texts = data.get("text", [])
    words: list[OCRWordBlock] = []

    for index, text in enumerate(texts):
        cleaned = str(text).strip()
        if not cleaned:
            continue

        words.append(
            OCRWordBlock(
                text=cleaned,
                confidence=_normalize_tesseract_confidence(data.get("conf", [""])[index]),
                block_num=_safe_int(data.get("block_num", [""])[index]),
                par_num=_safe_int(data.get("par_num", [""])[index]),
                line_num=_safe_int(data.get("line_num", [""])[index]),
                left=_safe_int(data.get("left", [""])[index]),
                top=_safe_int(data.get("top", [""])[index]),
            )
        )

    return words


def run_ocr_on_pil_image(image: Image.Image) -> OCRPayload:
    processed_image = preprocess_image(image)

    try:
        raw_text = pytesseract.image_to_string(processed_image) or ""
        words = _extract_word_blocks(processed_image)
    except TesseractNotFoundError as exc:
        raise OCRUnavailableError(
            "Tesseract OCR n'est pas installe ou n'est pas disponible dans le PATH. "
            "Installez Tesseract et reessayez."
        ) from exc
    except Exception as exc:
        raise OCRProcessingError(f"Echec de l'OCR de l'image : {exc}") from exc

    confidences = [word.confidence for word in words if word.text.strip()]
    overall_confidence = mean(confidences) if confidences else 0.0

    return OCRPayload(
        raw_text=raw_text.strip(),
        words=words,
        confidence=max(0.0, min(1.0, overall_confidence)),
    )


def extract_from_image(path: Path) -> ExtractionResult:
    if not path.exists():
        raise OCRProcessingError(f"Fichier image introuvable : {path}")

    if path.stat().st_size == 0:
        raise OCRProcessingError("Le fichier image importe est vide.")

    try:
        with Image.open(path) as image:
            payload = run_ocr_on_pil_image(image)
    except OCRUnavailableError:
        raise
    except OCRProcessingError:
        raise
    except Exception as exc:
        raise OCRProcessingError(f"Impossible d'ouvrir le fichier image : {exc}") from exc

    rows = build_rows_from_word_blocks(
        payload.words,
        fallback_text=payload.raw_text,
        default_confidence=max(payload.confidence, 0.70),
    )

    if not rows and payload.raw_text:
        rows = build_rows_from_text(payload.raw_text, default_confidence=0.70)

    confidence = average_confidence(rows) if rows else payload.confidence

    return ExtractionResult(
        filename=path.name,
        document_type="image",
        extracted_text=payload.raw_text,
        rows=rows,
        confidence=confidence,
    )