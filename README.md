# Agro Juice Scanner

Agro Juice Scanner est une application complete de conversion de documents en tableurs. Elle extrait les donnees structurees des images et des PDF, permet de verifier et modifier le tableau extrait, d'enregistrer des modeles reutilisables et d'exporter le resultat dans des formats compatibles avec les tableurs.

## Fonctionnalites

Fonctionnalites actuellement disponibles :

- Importation d'images et de fichiers PDF
- Extraction OCR des images
- Extraction du texte des PDF avec `pdfplumber`
- Solution OCR de secours pour les PDF numerises
- Tableau extrait modifiable dans l'interface
- Ajout et suppression de lignes
- Ajout et suppression de colonnes
- Mise en evidence des cellules peu fiables
- Exportation en XLSX, CSV et JSON
- Enregistrement et consultation de modeles
- Verification de l'etat du serveur
- Configuration locale du frontend et du backend

## Technologies

### Frontend

- React
- TypeScript
- Vite

### Backend

- FastAPI
- Python 3.11

### OCR et extraction

- OCR Tesseract via `pytesseract`
- `pdfplumber`
- `pypdfium2`
- Pillow

## Structure du projet

```text
docsheet/
  README.md
  frontend/
    .env.example
    package.json
    tsconfig.json
    vite.config.ts
    index.html
    src/
      api.ts
      App.tsx
      main.tsx
      styles.css
      types.ts
      components/
        FileUpload.tsx
        ResultTable.tsx
        TemplatePanel.tsx
  backend/
    .env.example
    requirements.txt
    data/
      templates.json
    temp/
      exports/
      uploads/
    app/
      __init__.py
      config.py
      main.py
      schemas.py
      routes/
        __init__.py
        health.py
        extract.py
        export.py
        templates.py
      services/
        __init__.py
        document_service.py
        export_service.py
        image_ocr.py
        pdf_service.py
        table_builder.py
        template_service.py
      utils/
        __init__.py
        files.py
    tests/
      conftest.py
      test_smoke.py
      test_export_service.py
```
