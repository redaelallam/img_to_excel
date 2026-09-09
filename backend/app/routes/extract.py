from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.schemas import ExtractResponse
from app.services.document_service import (
    DocumentProcessingError,
    extract_document_from_path,
)
from app.utils.files import (
    ensure_directories,
    is_allowed_extension,
    sanitize_filename,
    save_upload_file,
)

router = APIRouter(tags=["extract"])


@router.post("/extract", response_model=ExtractResponse)
async def extract_document(file: UploadFile = File(...)) -> ExtractResponse:
    ensure_directories()

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucun nom de fichier n'a ete fourni.",
        )

    if not is_allowed_extension(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Type de fichier non pris en charge. Formats acceptes : png, jpg, jpeg, webp, pdf.",
        )

    saved_path = await save_upload_file(file)

    if saved_path.stat().st_size == 0:
        return ExtractResponse(
            success=False,
            message="Le fichier importe est vide.",
            result=None,
        )

    try:
        result = extract_document_from_path(saved_path)
        result = result.model_copy(
            update={"filename": sanitize_filename(file.filename)}
        )
    except DocumentProcessingError as exc:
        return ExtractResponse(
            success=False,
            message=str(exc),
            result=None,
        )

    return ExtractResponse(
        success=True,
        message="Extraction terminee avec succes.",
        result=result,
    )