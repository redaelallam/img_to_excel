from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str


class TableCell(BaseModel):
    row_index: int = Field(..., ge=0)
    col_index: int = Field(..., ge=0)
    text: str
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class TableRow(BaseModel):
    row_index: int = Field(..., ge=0)
    cells: list[TableCell]


class ExtractionResult(BaseModel):
    filename: str
    document_type: Literal["image", "pdf", "scanned_pdf", "unknown"]
    extracted_text: str
    rows: list[TableRow] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class ExtractResponse(BaseModel):
    success: bool
    message: str
    result: ExtractionResult | None = None


class TemplateSaveRequest(BaseModel):
    name: str = Field(..., min_length=1)
    document_type: str = Field(..., min_length=1)
    column_names: list[str] = Field(default_factory=list)
    notes: str = ""


class TemplateInfo(BaseModel):
    id: str
    name: str
    document_type: str
    column_names: list[str]
    notes: str
    created_at: str


class TemplatesResponse(BaseModel):
    success: bool
    templates: list[TemplateInfo]


class SaveTemplateResponse(BaseModel):
    success: bool
    message: str
    template: TemplateInfo


class ExportRowsRequest(BaseModel):
    filename: str = "export"
    rows: list[TableRow] = Field(default_factory=list)


class ExportMockResponse(BaseModel):
    success: bool
    message: str
    export_type: Literal["xlsx", "csv", "json"]
    filename: str
    row_count: int