from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config import settings
from app.main import app


@pytest.fixture()
def isolated_settings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    data_dir = tmp_path / "data"
    temp_dir = tmp_path / "temp"
    upload_dir = temp_dir / "uploads"
    export_dir = temp_dir / "exports"
    template_file = data_dir / "templates.json"

    monkeypatch.setattr(settings, "DATA_DIR", data_dir)
    monkeypatch.setattr(settings, "TEMP_DIR", temp_dir)
    monkeypatch.setattr(settings, "UPLOAD_DIR", upload_dir)
    monkeypatch.setattr(settings, "EXPORT_DIR", export_dir)
    monkeypatch.setattr(settings, "TEMPLATE_FILE", template_file)

    data_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)
    upload_dir.mkdir(parents=True, exist_ok=True)
    export_dir.mkdir(parents=True, exist_ok=True)

    template_file.write_text(
        json.dumps(
            [
                {
                    "id": "test_template_1",
                    "name": "Test Invoice Template",
                    "document_type": "invoice",
                    "column_names": ["Item", "Qty", "Price"],
                    "notes": "Template used in backend smoke tests.",
                    "created_at": "2026-04-13T00:00:00+00:00",
                }
            ],
            indent=2,
        ),
        encoding="utf-8",
    )

    return tmp_path


@pytest.fixture()
def client(isolated_settings: Path) -> TestClient:
    return TestClient(app)