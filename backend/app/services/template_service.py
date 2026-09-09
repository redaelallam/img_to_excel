from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
import tempfile
from uuid import uuid4

from app.config import settings
from app.schemas import TemplateInfo, TemplateSaveRequest
from app.utils.files import ensure_directories


class TemplateStorageError(RuntimeError):
    pass


def _ensure_template_file() -> None:
    ensure_directories()
    if not settings.TEMPLATE_FILE.exists():
        settings.TEMPLATE_FILE.write_text("[]", encoding="utf-8")


def _read_raw_templates() -> list[dict]:
    _ensure_template_file()

    try:
        content = settings.TEMPLATE_FILE.read_text(encoding="utf-8").strip()
        if not content:
            return []
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise TemplateStorageError("templates.json contient un JSON invalide.") from exc
    except OSError as exc:
        raise TemplateStorageError(f"Impossible de lire templates.json : {exc}") from exc

    if not isinstance(data, list):
        raise TemplateStorageError("templates.json doit contenir un tableau JSON.")

    return data


def _atomic_write_json(path: Path, data: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            suffix=".tmp",
            delete=False,
        ) as temp_file:
            json.dump(data, temp_file, indent=2, ensure_ascii=False)
            temp_path = Path(temp_file.name)

        os.replace(temp_path, path)
    except OSError as exc:
        raise TemplateStorageError(f"Impossible d'ecrire templates.json : {exc}") from exc


def list_templates() -> list[TemplateInfo]:
    raw_templates = _read_raw_templates()

    templates: list[TemplateInfo] = []
    for item in raw_templates:
        try:
            templates.append(TemplateInfo(**item))
        except Exception:
            continue

    return templates


def save_template(payload: TemplateSaveRequest) -> TemplateInfo:
    raw_templates = _read_raw_templates()

    template = TemplateInfo(
        id=uuid4().hex,
        name=payload.name.strip(),
        document_type=payload.document_type.strip(),
        column_names=[column.strip() for column in payload.column_names],
        notes=payload.notes.strip(),
        created_at=datetime.now(timezone.utc).isoformat(),
    )

    raw_templates.append(template.model_dump())
    _atomic_write_json(settings.TEMPLATE_FILE, raw_templates)

    return template