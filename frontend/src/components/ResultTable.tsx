import type { ExtractionResult, TableCell, TableRow } from "../types";

type ResultTableProps = {
  result: ExtractionResult | null;
  rows: TableRow[];
  isLoading: boolean;
  selectedFileName: string | null;
  onCellChange: (rowIndex: number, colIndex: number, value: string) => void;
  onAddRow: () => void;
  onDeleteRow: (rowIndex: number) => void;
  onAddColumn: () => void;
  onDeleteColumn: () => void;
};

function getColumnCount(rows: TableRow[]): number {
  let maxCols = 0;

  rows.forEach((row) => {
    maxCols = Math.max(maxCols, row.cells.length);
  });

  return maxCols;
}

function getCell(row: TableRow, colIndex: number): TableCell | undefined {
  return row.cells.find((cell) => cell.col_index === colIndex);
}

function getConfidenceClass(confidence: number): string {
  if (confidence < 0.5) {
    return "low-confidence-cell";
  }

  if (confidence < 0.75) {
    return "medium-confidence-cell";
  }

  return "";
}

function formatDocumentType(documentType: string): string {
  const labels: Record<string, string> = {
    image: "Image",
    pdf: "PDF",
    scanned_pdf: "PDF numérisé",
    unknown: "Inconnu",
  };

  return labels[documentType] ?? documentType;
}

function ResultTable({
  result,
  rows,
  isLoading,
  selectedFileName,
  onCellChange,
  onAddRow,
  onDeleteRow,
  onAddColumn,
  onDeleteColumn,
}: ResultTableProps) {
  const columnCount = getColumnCount(rows);
  const hasRows = rows.length > 0;

  return (
    <section className="panel result-panel">
      <div className="panel-header">
        <h2>Resultats</h2>
        <span className="panel-tag">Verification</span>
      </div>

      {!selectedFileName && !isLoading && !result ? (
        <div className="empty-state">
          <h3>Aucun fichier importe</h3>
          <p>
            Importez une image ou un PDF pour voir ici le type de document detecte,
            le texte extrait et l'apercu du tableau modifiable.
          </p>
        </div>
      ) : null}

      {selectedFileName && isLoading ? (
        <div className="empty-state">
          <h3>Extraction du contenu...</h3>
          <p>
            Traitement de <strong>{selectedFileName}</strong>. Cela peut prendre un
            moment pour les PDF ou images volumineux.
          </p>
        </div>
      ) : null}

      {result ? (
        <div className="result-content">
          <div className="result-summary">
            <div className="summary-item">
              <span className="summary-label">Nom du fichier</span>
              <span className="summary-value">{result.filename}</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Type de document</span>
              <span className="summary-value">
                {formatDocumentType(result.document_type)}
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Fiabilite</span>
              <span className="summary-value">
                {(result.confidence * 100).toFixed(0)}%
              </span>
            </div>
          </div>

          <div className="text-preview">
            <h3>Texte extrait</h3>
            <pre>
              {result.extracted_text || "Aucun texte extrait n'a ete renvoye."}
            </pre>
          </div>

          <div className="table-preview">
            <div className="section-heading-row">
              <h3>Tableau modifiable</h3>
              <div className="table-action-bar">
                <button
                  type="button"
                  className="secondary-button"
                  onClick={onAddRow}
                >
                  Ajouter une ligne
                </button>
                <button
                  type="button"
                  className="secondary-button"
                  onClick={onAddColumn}
                >
                  Ajouter une colonne
                </button>
                <button
                  type="button"
                  className="secondary-button"
                  onClick={onDeleteColumn}
                  disabled={columnCount === 0}
                >
                  Supprimer la derniere colonne
                </button>
              </div>
            </div>

            {!hasRows ? (
              <div className="empty-state compact">
                <h3>Aucune ligne disponible</h3>
                <p>Ajoutez une ligne pour commencer a modifier le tableau.</p>
              </div>
            ) : (
              <div className="table-scroll">
                <table>
                  <thead>
                    <tr>
                      {Array.from({ length: columnCount }, (_, index) => (
                        <th key={`header-${index}`}>Colonne {index + 1}</th>
                      ))}
                      <th className="action-column-header">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((row) => (
                      <tr key={row.row_index}>
                        {Array.from({ length: columnCount }, (_, colIndex) => {
                          const cell = getCell(row, colIndex);
                          const value = cell?.text ?? "";
                          const confidence = cell?.confidence ?? 0;

                          return (
                            <td
                              key={`${row.row_index}-${colIndex}`}
                              className={getConfidenceClass(confidence)}
                            >
                              <input
                                type="text"
                                className="cell-input"
                                value={value}
                                onChange={(event) =>
                                  onCellChange(
                                    row.row_index,
                                    colIndex,
                                    event.target.value,
                                  )
                                }
                              />
                            </td>
                          );
                        })}
                        <td className="row-action-cell">
                          <button
                            type="button"
                            className="danger-button"
                            onClick={() => onDeleteRow(row.row_index)}
                          >
                            Supprimer la ligne
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            <p className="muted-text note-text">
              Les cellules peu fiables sont mises en evidence pour etre verifiees en premier.
            </p>
          </div>
        </div>
      ) : null}
    </section>
  );
}

export default ResultTable;