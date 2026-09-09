from __future__ import annotations

from dataclasses import dataclass
import re
from statistics import mean

from app.schemas import TableCell, TableRow


@dataclass
class OCRWordBlock:
    text: str
    confidence: float
    block_num: int | None = None
    par_num: int | None = None
    line_num: int | None = None
    left: int | None = None
    top: int | None = None


def _normalize_confidence(value: float) -> float:
    return max(0.0, min(1.0, value))


def build_rows_from_text(
    raw_text: str,
    default_confidence: float = 0.75,
) -> list[TableRow]:
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    rows: list[TableRow] = []

    for row_index, line in enumerate(lines):
        parts = [
            part.strip()
            for part in re.split(r"\s{2,}|\t|\s*\|\s*", line)
            if part.strip()
        ]

        if not parts:
            parts = [line]

        cells = [
            TableCell(
                row_index=row_index,
                col_index=col_index,
                text=part,
                confidence=_normalize_confidence(default_confidence),
            )
            for col_index, part in enumerate(parts)
        ]
        rows.append(TableRow(row_index=row_index, cells=cells))

    return rows


def build_rows_from_word_blocks(
    words: list[OCRWordBlock],
    fallback_text: str = "",
    default_confidence: float = 0.75,
) -> list[TableRow]:
    filtered_words = [word for word in words if word.text.strip()]
    if not filtered_words:
        return build_rows_from_text(fallback_text, default_confidence=default_confidence)

    grouped: dict[tuple[int, int, int], list[OCRWordBlock]] = {}
    for index, word in enumerate(filtered_words):
        key = (
            word.block_num if word.block_num is not None else 0,
            word.par_num if word.par_num is not None else 0,
            word.line_num if word.line_num is not None else index,
        )
        grouped.setdefault(key, []).append(word)

    ordered_groups = sorted(
        grouped.values(),
        key=lambda group: (
            min(item.top if item.top is not None else 10**9 for item in group),
            min(item.left if item.left is not None else 10**9 for item in group),
        ),
    )

    rows: list[TableRow] = []
    for row_index, group in enumerate(ordered_groups):
        ordered_words = sorted(
            group,
            key=lambda word: (
                word.left if word.left is not None else 10**9,
                word.top if word.top is not None else 10**9,
            ),
        )

        cells = [
            TableCell(
                row_index=row_index,
                col_index=col_index,
                text=word.text.strip(),
                confidence=_normalize_confidence(
                    word.confidence if word.confidence > 0 else default_confidence
                ),
            )
            for col_index, word in enumerate(ordered_words)
        ]
        rows.append(TableRow(row_index=row_index, cells=cells))

    return rows


def average_confidence(rows: list[TableRow]) -> float:
    values = [
        cell.confidence
        for row in rows
        for cell in row.cells
        if cell.text.strip()
    ]
    if not values:
        return 0.0
    return _normalize_confidence(mean(values))