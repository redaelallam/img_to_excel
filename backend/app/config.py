from __future__ import annotations

import os
from pathlib import Path


def _split_csv_env(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings:
    APP_NAME = os.getenv("APP_NAME", "Agro Juice Scanner")
    APP_VERSION = os.getenv("APP_VERSION", "0.8.0")
    DEBUG = os.getenv("DEBUG", "true").strip().lower() == "true"

    BACKEND_DIR = Path(__file__).resolve().parents[1]
    PROJECT_ROOT = BACKEND_DIR.parent

    DATA_DIR = Path(os.getenv("DATA_DIR", str(BACKEND_DIR / "data"))).resolve()
    TEMP_DIR = Path(os.getenv("TEMP_DIR", str(BACKEND_DIR / "temp"))).resolve()
    UPLOAD_DIR = Path(
        os.getenv("UPLOAD_DIR", str(TEMP_DIR / "uploads"))
    ).resolve()
    EXPORT_DIR = Path(
        os.getenv("EXPORT_DIR", str(TEMP_DIR / "exports"))
    ).resolve()

    TEMPLATE_FILE = Path(
        os.getenv("TEMPLATE_FILE", str(DATA_DIR / "templates.json"))
    ).resolve()

    FRONTEND_ORIGINS = _split_csv_env(
        os.getenv(
            "FRONTEND_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        )
    )

    ALLOWED_EXTENSIONS = {
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
        ".pdf",
    }

    @classmethod
    def ensure_base_directories(cls) -> None:
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.TEMP_DIR.mkdir(parents=True, exist_ok=True)
        cls.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        cls.EXPORT_DIR.mkdir(parents=True, exist_ok=True)

        if not cls.TEMPLATE_FILE.exists():
            cls.TEMPLATE_FILE.write_text("[]", encoding="utf-8")


settings = Settings()