from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class TableState:
    table_id: int
    running: bool = False
    started_at: datetime | None = None
    preset_minutes: int = 0
    logged_status: str = "idle"

    def start(self, started_at: datetime, preset_minutes: int) -> None:
        self.running = True
        self.started_at = started_at
        self.preset_minutes = preset_minutes
        self.logged_status = "normal"

    def add_minutes(self, minutes: int) -> None:
        if minutes > 0:
            self.preset_minutes += minutes

    def reset(self) -> None:
        self.running = False
        self.started_at = None
        self.preset_minutes = 0
        self.logged_status = "idle"
