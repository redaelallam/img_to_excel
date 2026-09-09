import { useEffect, useMemo, useState } from "react";

import {
  exportCsv,
  exportJson,
  exportXlsx,
  extractDocument,
  getHealth,
} from "./api";
import FileUpload from "./components/FileUpload";
import ResultTable from "./components/ResultTable";
import type { ExtractionResult, TableCell, TableRow } from "./types";

type ExportFormat = "xlsx" | "csv" | "json";

function cloneRows(rows: TableRow[]): TableRow[] {
  return rows.map((row) => ({
    row_index: row.row_index,
    cells: row.cells.map((cell) => ({ ...cell })),
  }));
}

function getColumnCount(rows: TableRow[]): number {
  return rows.reduce((max, row) => Math.max(max, row.cells.length), 0);
}

function reindexRows(rows: TableRow[]): TableRow[] {
  return rows.map((row, newRowIndex) => ({
    row_index: newRowIndex,
    cells: row.cells
      .map((cell, colIndex) => ({
        ...cell,
        row_index: newRowIndex,
        col_index: colIndex,
      }))
      .sort((a, b) => a.col_index - b.col_index),
  }));
}

function normalizeRow(row: TableRow, columnCount: number): TableRow {
  const cells: TableCell[] = [];

  for (let colIndex = 0; colIndex < columnCount; colIndex += 1) {
    const existing = row.cells.find((cell) => cell.col_index === colIndex);
    cells.push(
      existing
        ? {
            ...existing,
            col_index: colIndex,
          }
        : {
            row_index: row.row_index,
            col_index: colIndex,
            text: "",
            confidence: 0.5,
          },
    );
  }

  return {
    ...row,
    cells,
  };
}

function getBaseFilename(filename: string | null): string {
  if (!filename) {
    return "docusheet_export";
  }

  const dotIndex = filename.lastIndexOf(".");
  if (dotIndex <= 0) {
    return filename;
  }

  return filename.slice(0, dotIndex);
}

function triggerBlobDownload(blob: Blob, filename: string): void {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();

  window.setTimeout(() => {
    window.URL.revokeObjectURL(url);
  }, 500);
}

function App() {
  const [healthStatus, setHealthStatus] = useState<string>(
    "Verification du serveur...",
  );
  const [healthError, setHealthError] = useState<string>("");
  const [result, setResult] = useState<ExtractionResult | null>(null);
  const [editableRows, setEditableRows] = useState<TableRow[]>([]);
  const [selectedFileName, setSelectedFileName] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [extractError, setExtractError] = useState<string>("");

  const [actionError, setActionError] = useState<string>("");
  const [actionSuccess, setActionSuccess] = useState<string>("");
  const [exportingFormat, setExportingFormat] = useState<ExportFormat | null>(
    null,
  );

  const hasRows = editableRows.length > 0;
  const exportBaseName = useMemo(
    () => getBaseFilename(result?.filename ?? selectedFileName),
    [result?.filename, selectedFileName],
  );

  useEffect(() => {
    const loadHealth = async () => {
      try {
        const data = await getHealth();
        setHealthStatus(`${data.status} • ${data.app_name} v${data.version}`);
        setHealthError("");
      } catch (error) {
        setHealthStatus("Serveur indisponible");
        setHealthError(
          error instanceof Error
            ? error.message
            : "Connexion au serveur impossible.",
        );
      }
    };

    void loadHealth();
  }, []);

  const clearActionMessages = () => {
    setActionError("");
    setActionSuccess("");
  };

  const handleFileSelect = async (file: File) => {
    setSelectedFileName(file.name);
    setResult(null);
    setEditableRows([]);
    setExtractError("");
    clearActionMessages();
    setIsLoading(true);

    try {
      const response = await extractDocument(file);

      if (!response.success || !response.result) {
        throw new Error(response.message || "Echec de l'extraction.");
      }

      setResult(response.result);
      setEditableRows(cloneRows(response.result.rows));
      setExtractError("");
      setActionSuccess(
        "Extraction terminee. Vous pouvez maintenant verifier et modifier les donnees.",
      );
    } catch (error) {
      setResult(null);
      setEditableRows([]);
      setExtractError(
        error instanceof Error ? error.message : "Echec de l'extraction.",
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleCellChange = (
    rowIndex: number,
    colIndex: number,
    value: string,
  ) => {
    clearActionMessages();

    setEditableRows((previousRows) =>
      previousRows.map((row) => {
        if (row.row_index !== rowIndex) {
          return row;
        }

        const existingCell = row.cells.find(
          (cell) => cell.col_index === colIndex,
        );

        if (existingCell) {
          return {
            ...row,
            cells: row.cells.map((cell) =>
              cell.col_index === colIndex ? { ...cell, text: value } : cell,
            ),
          };
        }

        return {
          ...row,
          cells: [
            ...row.cells,
            {
              row_index: rowIndex,
              col_index: colIndex,
              text: value,
              confidence: 0.5,
            },
          ].sort((a, b) => a.col_index - b.col_index),
        };
      }),
    );
  };

  const handleAddRow = () => {
    clearActionMessages();

    setEditableRows((previousRows) => {
      const columnCount = Math.max(getColumnCount(previousRows), 1);
      const newRowIndex = previousRows.length;

      const newRow: TableRow = {
        row_index: newRowIndex,
        cells: Array.from({ length: columnCount }, (_, colIndex) => ({
          row_index: newRowIndex,
          col_index: colIndex,
          text: "",
          confidence: 0.5,
        })),
      };

      return [...previousRows, newRow];
    });
  };

  const handleDeleteRow = (rowIndex: number) => {
    clearActionMessages();

    setEditableRows((previousRows) =>
      reindexRows(previousRows.filter((row) => row.row_index !== rowIndex)),
    );
  };

  const handleAddColumn = () => {
    clearActionMessages();

    setEditableRows((previousRows) => {
      if (previousRows.length === 0) {
        return [
          {
            row_index: 0,
            cells: [
              {
                row_index: 0,
                col_index: 0,
                text: "",
                confidence: 0.5,
              },
            ],
          },
        ];
      }

      const nextColumnIndex = getColumnCount(previousRows);

      return previousRows.map((row) => ({
        ...row,
        cells: [
          ...row.cells,
          {
            row_index: row.row_index,
            col_index: nextColumnIndex,
            text: "",
            confidence: 0.5,
          },
        ],
      }));
    });
  };

  const handleDeleteColumn = () => {
    clearActionMessages();

    setEditableRows((previousRows) => {
      const columnCount = getColumnCount(previousRows);
      if (columnCount === 0) {
        return previousRows;
      }

      return previousRows.map((row) => {
        const trimmedCells = row.cells
          .filter((cell) => cell.col_index !== columnCount - 1)
          .map((cell, index) => ({
            ...cell,
            col_index: index,
          }));

        return {
          ...row,
          cells: trimmedCells,
        };
      });
    });
  };

  const handleExport = async (format: ExportFormat) => {
    if (!hasRows) {
      setActionError("Aucune donnee de tableau a exporter.");
      setActionSuccess("");
      return;
    }

    clearActionMessages();
    setExportingFormat(format);

    const payload = {
      filename: exportBaseName,
      rows: editableRows,
    };

    try {
      const blob =
        format === "xlsx"
          ? await exportXlsx(payload)
          : format === "csv"
            ? await exportCsv(payload)
            : await exportJson(payload);

      triggerBlobDownload(blob, `${exportBaseName}.${format}`);
      setActionSuccess(
        `Export ${format.toUpperCase()} telecharge avec succes.`,
      );
    } catch (error) {
      setActionError(
        error instanceof Error ? error.message : "Echec de l'export.",
      );
    } finally {
      setExportingFormat(null);
    }
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand-content">
          <div className="brand-row">
            <img className="brand-logo" src="/logo.jpg" alt="Logo AJP" />
            <div>
              <p className="eyebrow">Agro Juice Scanner</p>
              <h1>Espace de travail : du document au tableur</h1>
            </div>
          </div>
          <p className="subtitle">
            Importez des documents, extrayez les donnees structurees, verifiez
            les tableaux et exportez des resultats propres pour tableur.
          </p>
        </div>

        <div className="backend-status-card">
          <span className="status-dot" />
          <div>
            <p className="status-title">Etat du serveur</p>
            <p className="status-text">{healthStatus}</p>
          </div>
        </div>
      </header>

      {healthError ? (
        <div className="banner error-banner">{healthError}</div>
      ) : null}

      {extractError ? (
        <div className="banner error-banner">{extractError}</div>
      ) : null}

      {actionError ? (
        <div className="banner error-banner">{actionError}</div>
      ) : null}

      {actionSuccess ? (
        <div className="banner success-banner">{actionSuccess}</div>
      ) : null}

      <main className="dashboard-grid">
        <section className="main-column">
          <FileUpload
            isLoading={isLoading}
            selectedFileName={selectedFileName}
            onFileSelect={handleFileSelect}
          />

          <section className="panel export-panel">
            <div className="panel-header">
              <h2>Export</h2>
              <span className="panel-tag">Telechargement</span>
            </div>

            <div className="export-actions">
              <button
                type="button"
                className="primary-button"
                disabled={!hasRows || exportingFormat !== null}
                onClick={() => handleExport("xlsx")}
              >
                {exportingFormat === "xlsx"
                  ? "Exportation..."
                  : "Exporter en XLSX"}
              </button>

              <button
                type="button"
                className="secondary-button"
                disabled={!hasRows || exportingFormat !== null}
                onClick={() => handleExport("csv")}
              >
                {exportingFormat === "csv"
                  ? "Exportation..."
                  : "Exporter en CSV"}
              </button>

              <button
                type="button"
                className="secondary-button"
                disabled={!hasRows || exportingFormat !== null}
                onClick={() => handleExport("json")}
              >
                {exportingFormat === "json"
                  ? "Exportation..."
                  : "Exporter en JSON"}
              </button>
            </div>

            {!hasRows ? (
              <p className="muted-text note-text">
                Les boutons d'exportation deviennent actifs apres l'extraction
                de lignes ou l'ajout manuel de lignes.
              </p>
            ) : null}
          </section>

          <ResultTable
            result={result}
            rows={editableRows}
            isLoading={isLoading}
            selectedFileName={selectedFileName}
            onCellChange={handleCellChange}
            onAddRow={handleAddRow}
            onDeleteRow={handleDeleteRow}
            onAddColumn={handleAddColumn}
            onDeleteColumn={handleDeleteColumn}
          />
        </section>

      </main>
    </div>
  );
}

export default App;
