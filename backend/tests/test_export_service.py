from __future__ import annotations

from pathlib import Path

from app.services.export_service import export_rows_to_csv
from app.schemas import ExportRowsRequest, TableCell, TableRow


def test_export_rows_to_csv_creates_file(isolated_settings: Path) -> None:
    payload = ExportRowsRequest(
        filename="test_export",
        rows=[
            TableRow(
                row_index=0,
                cells=[
                    TableCell(
                        row_index=0,
                        col_index=0,
                        text="Name",
                        confidence=1.0,
                    ),
                    TableCell(
                        row_index=0,
                        col_index=1,
                        text="Amount",
                        confidence=1.0,
                    ),
                ],
            ),
            TableRow(
                row_index=1,
                cells=[
                    TableCell(
                        row_index=1,
                        col_index=0,
                        text="Alice",
                        confidence=0.95,
                    ),
                    TableCell(
                        row_index=1,
                        col_index=1,
                        text="1500",
                        confidence=0.94,
                    ),
                ],
            ),
        ],
    )

    file_path = export_rows_to_csv(payload)

    assert file_path.exists()
    assert file_path.suffix == ".csv"

    content = file_path.read_text(encoding="utf-8")
    assert "Name,Amount" in content
    assert "Alice,1500" in content