import type {
  ExtractResponse,
  ExportRowsRequest,
  SaveTemplateResponse,
  TemplateSaveRequest,
  TemplatesResponse,
} from "./types";

function normalizeApiBaseUrl(url: string): string {
  return url.trim().replace(/\/+$/, "");
}

const RAW_API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";
const API_BASE_URL = normalizeApiBaseUrl(RAW_API_BASE_URL);

async function parseJsonResponse<T>(response: Response): Promise<T> {
  const text = await response.text();

  let parsed: unknown = null;
  if (text) {
    try {
      parsed = JSON.parse(text);
    } catch {
      parsed = null;
    }
  }

  if (!response.ok) {
    if (
      parsed &&
      typeof parsed === "object" &&
      parsed !== null &&
      "detail" in parsed &&
      typeof (parsed as { detail: unknown }).detail === "string"
    ) {
      throw new Error((parsed as { detail: string }).detail);
    }

    if (text) {
      throw new Error(text);
    }

    throw new Error(`Request failed with status ${response.status}`);
  }

  if (parsed === null) {
    throw new Error("Le serveur a renvoye un JSON invalide.");
  }

  return parsed as T;
}

async function parseBlobError(response: Response): Promise<never> {
  const text = await response.text();

  try {
    const parsed = JSON.parse(text) as { detail?: string };
    if (parsed.detail) {
      throw new Error(parsed.detail);
    }
  } catch {
    throw new Error(text || `La requete a echoue avec le statut ${response.status}`);
  }

  throw new Error(text || `La requete a echoue avec le statut ${response.status}`);
}

export async function getHealth(): Promise<{
  status: string;
  app_name: string;
  version: string;
}> {
  const response = await fetch(`${API_BASE_URL}/health`, {
    method: "GET",
  });

  return parseJsonResponse(response);
}

export async function extractDocument(file: File): Promise<ExtractResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/extract`, {
    method: "POST",
    body: formData,
  });

  return parseJsonResponse<ExtractResponse>(response);
}

export async function listTemplates(): Promise<TemplatesResponse> {
  const response = await fetch(`${API_BASE_URL}/templates`, {
    method: "GET",
  });

  return parseJsonResponse<TemplatesResponse>(response);
}

export async function saveTemplate(
  payload: TemplateSaveRequest,
): Promise<SaveTemplateResponse> {
  const response = await fetch(`${API_BASE_URL}/templates`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  return parseJsonResponse<SaveTemplateResponse>(response);
}

async function exportFile(
  endpoint: "xlsx" | "csv" | "json",
  payload: ExportRowsRequest,
): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/export/${endpoint}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    await parseBlobError(response);
  }

  return response.blob();
}

export function exportXlsx(payload: ExportRowsRequest): Promise<Blob> {
  return exportFile("xlsx", payload);
}

export function exportCsv(payload: ExportRowsRequest): Promise<Blob> {
  return exportFile("csv", payload);
}

export function exportJson(payload: ExportRowsRequest): Promise<Blob> {
  return exportFile("json", payload);
}

export { API_BASE_URL };