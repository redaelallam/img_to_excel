from fastapi import APIRouter, HTTPException, status

from app.schemas import (
    SaveTemplateResponse,
    TemplateSaveRequest,
    TemplatesResponse,
)
from app.services.template_service import (
    TemplateStorageError,
    list_templates,
    save_template,
)

router = APIRouter(tags=["templates"])


@router.get("/templates", response_model=TemplatesResponse)
def get_templates() -> TemplatesResponse:
    try:
        templates = list_templates()
    except TemplateStorageError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    return TemplatesResponse(success=True, templates=templates)


@router.post("/templates", response_model=SaveTemplateResponse)
def create_template(payload: TemplateSaveRequest) -> SaveTemplateResponse:
    try:
        template = save_template(payload)
    except TemplateStorageError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    return SaveTemplateResponse(
        success=True,
        message="Modele enregistre avec succes.",
        template=template,
    )