from dataclasses import dataclass

from PyQt6.QtCore import QSettings


ORGANIZATION_NAME = "PDSystem"
APPLICATION_NAME = "TableTimer"


@dataclass(slots=True)
class AppConfig:
    table_count: int = 8
    default_hours: int = 1
    default_minutes: int = 0
    warning_minutes: int = 10
    start_fullscreen: bool = False

    @classmethod
    def defaults(cls) -> "AppConfig":
        return cls()

    @classmethod
    def load(cls) -> "AppConfig":
        defaults = cls.defaults()
        settings = QSettings(ORGANIZATION_NAME, APPLICATION_NAME)
        return cls(
            table_count=clamp_table_count(_read_int(settings, "table_count", defaults.table_count)),
            default_hours=clamp_hours(_read_int(settings, "default_hours", defaults.default_hours)),
            default_minutes=clamp_minutes(_read_int(settings, "default_minutes", defaults.default_minutes)),
            warning_minutes=clamp_warning_minutes(_read_int(settings, "warning_minutes", defaults.warning_minutes)),
            start_fullscreen=_read_bool(settings, "start_fullscreen", defaults.start_fullscreen),
        )

    def save(self) -> None:
        settings = QSettings(ORGANIZATION_NAME, APPLICATION_NAME)
        settings.setValue("table_count", self.table_count)
        settings.setValue("default_hours", self.default_hours)
        settings.setValue("default_minutes", self.default_minutes)
        settings.setValue("warning_minutes", self.warning_minutes)
        settings.setValue("start_fullscreen", self.start_fullscreen)
        settings.sync()


def _read_int(settings: QSettings, key: str, default: int) -> int:
    value = settings.value(key, default)
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _read_bool(settings: QSettings, key: str, default: bool) -> bool:
    value = settings.value(key, default)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def clamp_table_count(value: int) -> int:
    return max(1, min(value, 99))


def clamp_hours(value: int) -> int:
    return max(0, min(value, 23))


def clamp_minutes(value: int) -> int:
    return max(0, min(value, 59))


def clamp_warning_minutes(value: int) -> int:
    return max(0, min(value, 24 * 60))
