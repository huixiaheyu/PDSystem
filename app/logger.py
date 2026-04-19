from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

LOG_DIRECTORY_NAME = "PD-System-logs"
BASE_DIR = Path(__file__).resolve().parent.parent


class AppLogger:
    def __init__(self) -> None:
        self._log_dir = self._resolve_log_dir()

    def log_event(self, category: str, message: str, **fields: Any) -> None:
        timestamp = datetime.now()
        record = self._format_record(timestamp, category, message, fields)
        try:
            self._log_dir.mkdir(parents=True, exist_ok=True)
            self._log_file_path(timestamp).open("a", encoding="utf-8").write(record + "\n")
        except OSError:
            return

    def info(self, message: str, **fields: Any) -> None:
        self.log_event("INFO", message, **fields)

    def warning(self, message: str, **fields: Any) -> None:
        self.log_event("WARNING", message, **fields)

    def error(self, message: str, **fields: Any) -> None:
        self.log_event("ERROR", message, **fields)

    def _resolve_log_dir(self) -> Path:
        return BASE_DIR / LOG_DIRECTORY_NAME

    def _log_file_path(self, timestamp: datetime) -> Path:
        return self._log_dir / f"{timestamp:%Y-%m-%d}.log"

    def _format_record(
        self,
        timestamp: datetime,
        category: str,
        message: str,
        fields: dict[str, Any],
    ) -> str:
        parts = [f"[{timestamp:%Y-%m-%d %H:%M:%S}]", category, message]
        for key, value in fields.items():
            parts.append(f"{key}={value}")
        return " | ".join(parts)


logger = AppLogger()
