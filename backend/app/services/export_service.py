from __future__ import annotations

import csv
import json
from pathlib import Path
from uuid import uuid4

from openpyxl import Workbook

from app.config import settings
from app.schemas import ExportRowsRequest, TableRow
from app.utils.files import ensure_directories


class ExportValidationError(RuntimeError):
    pass


def _sanitize_base_filename(filename: str) -> str:
    cleaned = "".join(ch for ch in filename.strip() if ch.isalnum() or ch in ("-", "_"))
    return cleaned or "export"


def _rows_to_matrix(rows: list[TableRow]) -> list[list[str]]:
    if not rows:
        return []

    max_col_index = -1
    for row in rows:
        for cell in row.cells:
            if cell.col_index > max_col_index:
                max_col_index = cell.col_index

    if max_col_index < 0:
        return []

    matrix: list[list[str]] = []
    sorted_rows = sorted(rows, key=lambda row: row.row_index)

    for row in sorted_rows:
        row_values = [""] * (max_col_index + 1)
        for cell in row.cells:
            if 0 <= cell.col_index <= max_col_index:
                row_values[cell.col_index] = cell.text
        matrix.append(row_values)

    return matrix


def _validate_export_rows(payload: ExportRowsRequest) -> list[list[str]]:
    matrix = _rows_to_matrix(payload.rows)
    if not matrix:
        raise ExportValidationError("Aucune ligne de tableau n'a ete fournie pour l'export.")

    has_any_data = any(any(cell.strip() for cell in row) for row in matrix)
    if not has_any_data:
        raise ExportValidationError("Le tableau fourni est vide et ne peut pas etre exporte.")

    return matrix


def _build_export_path(filename: str, extension: str) -> Path:
    ensure_directories()
    base_name = _sanitize_base_filename(filename)
    return settings.EXPORT_DIR / f"{base_name}_{uuid4().hex[:8]}.{extension}"


def export_rows_to_xlsx(payload: ExportRowsRequest) -> Path:
    matrix = _validate_export_rows(payload)
    destination = _build_export_path(payload.filename, "xlsx")

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Sheet1"

    for row in matrix:
        sheet.append(row)

    workbook.save(destination)
    return destination


def export_rows_to_csv(payload: ExportRowsRequest) -> Path:
    matrix = _validate_export_rows(payload)
    destination = _build_export_path(payload.filename, "csv")

    with destination.open("w", newline="", encoding="utf-8") as file_obj:
        writer = csv.writer(file_obj)
        writer.writerows(matrix)

    return destination


def export_rows_to_json(payload: ExportRowsRequest) -> Path:
    matrix = _validate_export_rows(payload)
    destination = _build_export_path(payload.filename, "json")

    data = {
        "filename": payload.filename,
        "rows": [
            {
                "row_index": row.row_index,
                "cells": [
                    {
                        "row_index": cell.row_index,
                        "col_index": cell.col_index,
                        "text": cell.text,
                        "confidence": cell.confidence,
                    }
                    for cell in row.cells
                ],
            }
            for row in payload.rows
        ],
        "matrix": matrix,
    }

    destination.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return destination