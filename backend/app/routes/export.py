from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse

from app.schemas import ExportRowsRequest
from app.services.export_service import (
    ExportValidationError,
    export_rows_to_csv,
    export_rows_to_json,
    export_rows_to_xlsx,
)

router = APIRouter(tags=["export"])


@router.post("/export/xlsx")
def export_xlsx(payload: ExportRowsRequest) -> FileResponse:
    try:
        file_path = export_rows_to_xlsx(payload)
    except ExportValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return FileResponse(
        path=file_path,
        filename=file_path.name,
        media_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
    )


@router.post("/export/csv")
def export_csv(payload: ExportRowsRequest) -> FileResponse:
    try:
        file_path = export_rows_to_csv(payload)
    except ExportValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return FileResponse(
        path=file_path,
        filename=file_path.name,
        media_type="text/csv",
    )


@router.post("/export/json")
def export_json(payload: ExportRowsRequest) -> FileResponse:
    try:
        file_path = export_rows_to_json(payload)
    except ExportValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return FileResponse(
        path=file_path,
        filename=file_path.name,
        media_type="application/json",
    )