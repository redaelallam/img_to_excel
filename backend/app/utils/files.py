from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.config import settings


def ensure_directories() -> None:
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    settings.TEMP_DIR.mkdir(parents=True, exist_ok=True)
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    settings.EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    if not settings.TEMPLATE_FILE.exists():
        settings.TEMPLATE_FILE.write_text("[]", encoding="utf-8")


def get_file_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def is_allowed_extension(filename: str) -> bool:
    return get_file_extension(filename) in settings.ALLOWED_EXTENSIONS


def sanitize_filename(filename: str) -> str:
    path = Path(filename)
    safe_stem = "".join(ch for ch in path.stem if ch.isalnum() or ch in ("-", "_"))
    safe_stem = safe_stem or "file"
    return f"{safe_stem}{path.suffix.lower()}"


def build_upload_path(filename: str) -> Path:
    extension = get_file_extension(filename)
    unique_name = f"{uuid4().hex}{extension}"
    return settings.UPLOAD_DIR / unique_name


async def save_upload_file(upload_file: UploadFile) -> Path:
    ensure_directories()

    destination = build_upload_path(upload_file.filename or "upload.bin")
    content = await upload_file.read()
    destination.write_bytes(content)

    await upload_file.close()
    return destination