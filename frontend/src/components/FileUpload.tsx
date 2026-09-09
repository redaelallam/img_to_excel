import { useRef, useState } from "react";

const ALLOWED_EXTENSIONS = [".png", ".jpg", ".jpeg", ".webp", ".pdf"];
const ACCEPT_VALUE = ALLOWED_EXTENSIONS.join(",");

type FileUploadProps = {
  isLoading: boolean;
  selectedFileName: string | null;
  onFileSelect: (file: File) => void;
};

function hasAllowedExtension(fileName: string): boolean {
  const lower = fileName.toLowerCase();
  return ALLOWED_EXTENSIONS.some((extension) => lower.endsWith(extension));
}

function FileUpload({
  isLoading,
  selectedFileName,
  onFileSelect,
}: FileUploadProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [localError, setLocalError] = useState("");

  const handleValidatedFile = (file: File | null) => {
    if (!file) {
      return;
    }

    if (!hasAllowedExtension(file.name)) {
      setLocalError("Type de fichier non pris en charge. Utilisez PNG, JPG, JPEG, WEBP ou PDF.");
      return;
    }

    setLocalError("");
    onFileSelect(file);
  };

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null;
    handleValidatedFile(file);

    event.target.value = "";
  };

  const handleBrowseClick = () => {
    inputRef.current?.click();
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);

    const file = event.dataTransfer.files?.[0] ?? null;
    handleValidatedFile(file);
  };

  return (
    <section className="panel upload-panel">
      <div className="panel-header">
        <h2>Importation</h2>
        <span className="panel-tag">Pret</span>
      </div>

      <div
        className={`upload-dropzone ${isDragging ? "drag-active" : ""}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        role="button"
        tabIndex={0}
        onClick={handleBrowseClick}
        onKeyDown={(event) => {
          if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            handleBrowseClick();
          }
        }}
      >
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPT_VALUE}
          className="hidden-input"
          onChange={handleInputChange}
          disabled={isLoading}
        />

        <div className="upload-icon">{isLoading ? "…" : "↑"}</div>
        <h3>{isLoading ? "Importation et extraction..." : "Deposez un fichier ici"}</h3>
        <p>
          Cliquez pour choisir un fichier ou faites glisser un document ici pour l'extraire.
        </p>

        <div className="upload-meta">
          <span>Formats acceptes : PNG, JPG, JPEG, WEBP, PDF</span>
        </div>

        <button
          type="button"
          className="primary-button"
          disabled={isLoading}
          onClick={(event) => {
            event.stopPropagation();
            handleBrowseClick();
          }}
        >
          {isLoading ? "Traitement..." : "Choisir un fichier"}
        </button>

        <div className="selected-file">
          <strong>Fichier selectionne :</strong>{" "}
          {selectedFileName ? selectedFileName : "Aucun fichier"}
        </div>

        {localError ? <div className="inline-error">{localError}</div> : null}
      </div>
    </section>
  );
}

export default FileUpload;