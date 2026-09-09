import { useEffect, useState } from "react";

import type { TemplateInfo } from "../types";

type TemplatePanelProps = {
  templates: TemplateInfo[];
  isLoading: boolean;
  isSaving: boolean;
  hasRows: boolean;
  currentDocumentType: string;
  onSaveTemplate: (payload: {
    name: string;
    documentType: string;
    notes: string;
  }) => Promise<void>;
};

function formatDocumentType(documentType: string): string {
  const labels: Record<string, string> = {
    invoice: "Facture",
    marksheet: "Relevé de notes",
    image: "Image",
    pdf: "PDF",
    scanned_pdf: "PDF numérisé",
    unknown: "Inconnu",
  };

  return labels[documentType] ?? documentType;
}

function TemplatePanel({
  templates,
  isLoading,
  isSaving,
  hasRows,
  currentDocumentType,
  onSaveTemplate,
}: TemplatePanelProps) {
  const [name, setName] = useState("");
  const [documentType, setDocumentType] = useState(currentDocumentType);
  const [notes, setNotes] = useState("");

  useEffect(() => {
    setDocumentType(currentDocumentType);
  }, [currentDocumentType]);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const trimmedName = name.trim();
    if (!trimmedName || !hasRows) {
      return;
    }

    await onSaveTemplate({
      name: trimmedName,
      documentType: documentType.trim() || "unknown",
      notes: notes.trim(),
    });

    setName("");
    setNotes("");
  };

  return (
    <aside className="panel template-panel">
      <div className="panel-header">
        <h2>Modeles</h2>
        <span className="panel-tag">Enregistrer et reutiliser</span>
      </div>

      <div className="panel-section">
        <h3 className="section-title">Enregistrer le modele actuel</h3>

        <form className="template-form" onSubmit={handleSubmit}>
          <label className="form-field">
            <span>Nom du modele</span>
            <input
              type="text"
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="ex. Modele de facture"
              disabled={isSaving || !hasRows}
            />
          </label>

          <label className="form-field">
            <span>Type de document</span>
            <input
              type="text"
              value={documentType}
              onChange={(event) => setDocumentType(event.target.value)}
              placeholder="facture"
              disabled={isSaving}
            />
          </label>

          <label className="form-field">
            <span>Notes</span>
            <textarea
              value={notes}
              onChange={(event) => setNotes(event.target.value)}
              placeholder="Notes facultatives sur ce modele"
              rows={4}
              disabled={isSaving || !hasRows}
            />
          </label>

          <button
            type="submit"
            className="primary-button full-width"
            disabled={isSaving || !hasRows || !name.trim()}
          >
            {isSaving ? "Enregistrement..." : "Enregistrer le modele"}
          </button>
        </form>

        {!hasRows ? (
          <p className="muted-text note-text">
            Extrayez et verifiez un tableau avant de l'enregistrer comme modele.
          </p>
        ) : null}
      </div>

      <div className="panel-section">
        <h3 className="section-title">Modeles enregistres</h3>

        {isLoading ? (
          <p className="muted-text">Chargement des modeles...</p>
        ) : templates.length === 0 ? (
          <div className="empty-state compact">
            <h3>Aucun modele</h3>
            <p>Les modeles d'extraction enregistres apparaitront ici.</p>
          </div>
        ) : (
          <div className="template-list">
            {templates.map((template) => (
              <div className="template-card" key={template.id}>
                <h3>{template.name}</h3>
                <p className="template-type">
                  {formatDocumentType(template.document_type)}
                </p>
                <p className="template-notes">{template.notes || "Aucune note"}</p>
                {template.column_names.length > 0 ? (
                  <div className="template-columns">
                    {template.column_names.map((column) => (
                      <span
                        className="column-pill"
                        key={`${template.id}-${column}`}
                      >
                        {column}
                      </span>
                    ))}
                  </div>
                ) : null}
              </div>
            ))}
          </div>
        )}
      </div>
    </aside>
  );
}

export default TemplatePanel;