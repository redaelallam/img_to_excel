export type DocumentType = "image" | "pdf" | "scanned_pdf" | "unknown";

export interface TableCell {
  row_index: number;
  col_index: number;
  text: string;
  confidence: number;
}

export interface TableRow {
  row_index: number;
  cells: TableCell[];
}

export interface ExtractionResult {
  filename: string;
  document_type: DocumentType;
  extracted_text: string;
  rows: TableRow[];
  confidence: number;
}

export interface ExtractResponse {
  success: boolean;
  message: string;
  result: ExtractionResult | null;
}

export interface TemplateInfo {
  id: string;
  name: string;
  document_type: string;
  column_names: string[];
  notes: string;
  created_at: string;
}

export interface TemplateSaveRequest {
  name: string;
  document_type: string;
  column_names: string[];
  notes: string;
}

export interface TemplatesResponse {
  success: boolean;
  templates: TemplateInfo[];
}

export interface SaveTemplateResponse {
  success: boolean;
  message: string;
  template: TemplateInfo;
}

export interface ExportRowsRequest {
  filename: string;
  rows: TableRow[];
}