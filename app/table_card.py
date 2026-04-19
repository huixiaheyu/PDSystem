from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QWheelEvent
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


ROW_STYLE = """
QFrame {
    background-color: #ffffff;
    border: 2px solid #ffb3c7;
    border-radius: 8px;
}
QFrame:hover {
    background-color: #fff7fb;
}
QFrame[statusState="warning"] {
    background-color: #fff6dd;
    border: 2px solid #ffb84d;
    border-left: 6px solid #ff9800;
    border-radius: 8px;
}
QFrame[statusState="warning"]:hover {
    background-color: #fff1cf;
}
QFrame[statusState="overtime"] {
    background-color: #ffe4ee;
    border: 2px solid #ff6b9a;
    border-left: 6px solid #d6336c;
    border-radius: 8px;
}
QFrame[statusState="overtime"]:hover {
    background-color: #ffd7e7;
}
QFrame[headerRow="true"] {
    background-color: #fff7fb;
    border: 2px solid #ffd36e;
    border-radius: 8px;
}
QFrame[headerRow="true"]:hover {
    background-color: #fff7fb;
}
"""

INPUT_STYLE = (
    "QSpinBox {min-width: 64px; min-height: 38px; padding: 0 10px; border: 2px solid #ffb3c7; "
    "border-radius: 4px; background: #ffffff; color: #5b245d; font-size: 15px; font-weight: 700; outline: none;}"
    "QSpinBox:focus {border: 2px solid #7b61ff; background: #ffffff; outline: none;}"
    "QSpinBox::up-button, QSpinBox::down-button {width: 0px; height: 0px; border: none; background: transparent;}"
    "QSpinBox::up-arrow, QSpinBox::down-arrow {width: 0px; height: 0px;}"
)

PRIMARY_BUTTON_STYLE = (
    "QPushButton {min-width: 92px; min-height: 40px; padding: 0 14px; border: 2px solid #7b61ff; border-radius: 4px;"
    "background-color: #7b61ff; color: #ffffff; font-size: 14px; font-weight: 800; outline: none;}"
    "QPushButton:hover {background-color: #6a52ea;}"
    "QPushButton:pressed {background-color: #5941d3;}"
    "QPushButton:focus {outline: none;}"
)

DANGER_BUTTON_STYLE = (
    "QPushButton {min-width: 92px; min-height: 40px; padding: 0 14px; border: 2px solid #ff6b6b; border-radius: 4px;"
    "background-color: #ff6b6b; color: #ffffff; font-size: 14px; font-weight: 800; outline: none;}"
    "QPushButton:hover {background-color: #f05d5d;}"
    "QPushButton:pressed {background-color: #e24f4f;}"
    "QPushButton:focus {outline: none;}"
)

DISABLED_BUTTON_STYLE = (
    "QPushButton {min-width: 92px; min-height: 40px; padding: 0 14px; border: 2px solid #d5d3dd; border-radius: 4px;"
    "background-color: #eceaf2; color: #9b95ab; font-size: 14px; font-weight: 800; outline: none;}"
    "QPushButton:hover {background-color: #eceaf2;}"
    "QPushButton:pressed {background-color: #eceaf2;}"
    "QPushButton:focus {outline: none;}"
)

TABLE_TITLE_STYLE = "font-size: 20px; font-weight: 800; color: #ff4f8b; border: none;"
TABLE_SUBTITLE_STYLE = "font-size: 11px; font-weight: 700; color: #24a86a; border: none;"
PRESET_VALUE_STYLE = "font-size: 17px; font-weight: 800; color: #ff7a00; border: none;"
COUNTDOWN_VALUE_STYLE = "font-size: 34px; font-weight: 800; color: #7b61ff; border: none;"
COUNTDOWN_WARNING_STYLE = "font-size: 34px; font-weight: 900; color: #ff9800; border: none;"
COUNTDOWN_OVERTIME_STYLE = "font-size: 34px; font-weight: 900; color: #d6336c; border: none;"
TIME_UNIT_LABEL_STYLE = "font-size: 13px; font-weight: 700; color: #24a86a; border: none;"
STATUS_BADGE_STYLE = (
    "font-size: 12px; font-weight: 800; border: none; "
    "color: {text_color}; background-color: {background_color}; border-radius: 4px; padding: 7px 10px;"
)


TABLE_COLUMN_WIDTH = 120
STATUS_COLUMN_WIDTH = 96
PRESET_COLUMN_WIDTH = 92
COUNTDOWN_COLUMN_WIDTH = 228
COUNTDOWN_MINIMUM_WIDTH = 228
INPUT_COLUMN_WIDTH = 236
ACTION_COLUMN_WIDTH = 78
ROW_HORIZONTAL_PADDING = 16
ROW_COLUMN_SPACING = 18


class NoWheelSpinBox(QSpinBox):
    def wheelEvent(self, event: QWheelEvent) -> None:
        event.ignore()


class TableCard(QFrame):
    def __init__(self, table_id: int, default_hours: int, default_minutes: int, parent=None) -> None:
        super().__init__(parent)
        self.table_id = table_id
        self._start_handler = None
        self._stop_handler = None
        self._add_time_handler = None

        self.setMinimumHeight(82)
        self.setObjectName(f"table-row-{table_id}")
        self.setStyleSheet(ROW_STYLE)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(ROW_HORIZONTAL_PADDING, 12, ROW_HORIZONTAL_PADDING, 12)
        layout.setSpacing(ROW_COLUMN_SPACING)

        self.table_cell = QWidget()
        self.table_cell.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.table_cell.setStyleSheet("background: transparent;")
        self.table_cell.setMinimumWidth(TABLE_COLUMN_WIDTH)
        self.table_cell.setMaximumWidth(TABLE_COLUMN_WIDTH)
        title_wrap = QVBoxLayout(self.table_cell)
        title_wrap.setContentsMargins(0, 0, 0, 0)
        title_wrap.setSpacing(2)

        self.title_label = QLabel(f"{table_id:02d}号桌")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.title_label.setStyleSheet(TABLE_TITLE_STYLE)
        title_wrap.addWidget(self.title_label)

        self.table_subtitle_label = QLabel("Table")
        self.table_subtitle_label.setStyleSheet(TABLE_SUBTITLE_STYLE)
        title_wrap.addWidget(self.table_subtitle_label)

        layout.addWidget(self.table_cell, 0, Qt.AlignmentFlag.AlignVCenter)

        self.status_value_label = QLabel("空闲")
        self.status_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_value_label.setMinimumWidth(STATUS_COLUMN_WIDTH)
        self.status_value_label.setMaximumWidth(STATUS_COLUMN_WIDTH)
        layout.addWidget(self.status_value_label, 0, Qt.AlignmentFlag.AlignVCenter)

        self.preset_value_label = QLabel("01:00")
        self.preset_value_label.setMinimumWidth(PRESET_COLUMN_WIDTH)
        self.preset_value_label.setMaximumWidth(PRESET_COLUMN_WIDTH)
        self.preset_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preset_value_label.setStyleSheet(PRESET_VALUE_STYLE)
        layout.addWidget(self.preset_value_label, 0, Qt.AlignmentFlag.AlignVCenter)

        self.countdown_value_label = QLabel("--:--:--")
        self.countdown_value_label.setMinimumWidth(COUNTDOWN_MINIMUM_WIDTH)
        self.countdown_value_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.countdown_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.countdown_value_label.setStyleSheet(COUNTDOWN_VALUE_STYLE)
        layout.addWidget(self.countdown_value_label, 1, Qt.AlignmentFlag.AlignVCenter)

        self.input_cell = QWidget()
        self.input_cell.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.input_cell.setStyleSheet("background: transparent;")
        self.input_cell.setMinimumWidth(INPUT_COLUMN_WIDTH)
        self.input_cell.setMaximumWidth(INPUT_COLUMN_WIDTH)
        preset_layout = QHBoxLayout(self.input_cell)
        preset_layout.setContentsMargins(0, 0, 0, 0)
        preset_layout.setSpacing(8)

        self.hours_input = NoWheelSpinBox()
        self.hours_input.setRange(0, 23)
        self.hours_input.setStyleSheet(INPUT_STYLE)
        preset_layout.addWidget(self.hours_input)

        self.hours_unit_label = QLabel("时")
        self.hours_unit_label.setStyleSheet(TIME_UNIT_LABEL_STYLE)
        preset_layout.addWidget(self.hours_unit_label)

        self.minutes_input = NoWheelSpinBox()
        self.minutes_input.setRange(0, 59)
        self.minutes_input.setStyleSheet(INPUT_STYLE)
        preset_layout.addWidget(self.minutes_input)

        self.minutes_unit_label = QLabel("分")
        self.minutes_unit_label.setStyleSheet(TIME_UNIT_LABEL_STYLE)
        preset_layout.addWidget(self.minutes_unit_label)

        preset_layout.addStretch()
        layout.addWidget(self.input_cell, 0, Qt.AlignmentFlag.AlignVCenter)

        self.add_time_button = QPushButton("加时")
        self.add_time_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_time_button.setStyleSheet(PRIMARY_BUTTON_STYLE)
        self.add_time_button.setMinimumWidth(ACTION_COLUMN_WIDTH)
        self.add_time_button.setMaximumWidth(ACTION_COLUMN_WIDTH)
        self.add_time_button.clicked.connect(self._handle_add_time)
        layout.addWidget(self.add_time_button, 0, Qt.AlignmentFlag.AlignVCenter)

        self.action_button = QPushButton("开始")
        self.action_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.action_button.setStyleSheet(PRIMARY_BUTTON_STYLE)
        self.action_button.setMinimumWidth(ACTION_COLUMN_WIDTH)
        self.action_button.setMaximumWidth(ACTION_COLUMN_WIDTH)
        self.action_button.clicked.connect(self._handle_action)
        layout.addWidget(self.action_button, 0, Qt.AlignmentFlag.AlignVCenter)

        self.set_inputs(default_hours, default_minutes)
        self.set_idle()

    def set_action_handlers(self, start_handler, stop_handler, add_time_handler) -> None:
        self._start_handler = start_handler
        self._stop_handler = stop_handler
        self._add_time_handler = add_time_handler

    def set_inputs(self, hours: int, minutes: int) -> None:
        self.hours_input.setValue(hours)
        self.minutes_input.setValue(minutes)
        self.preset_value_label.setText(f"{hours:02d}:{minutes:02d}")

    def get_input_minutes(self) -> int:
        return self.hours_input.value() * 60 + self.minutes_input.value()

    def _set_status_badge(self, text: str, text_color: str, background_color: str) -> None:
        self.status_value_label.setText(text)
        self.status_value_label.setStyleSheet(
            STATUS_BADGE_STYLE.format(text_color=text_color, background_color=background_color)
        )

    def _set_row_status_state(self, status: str) -> None:
        self.setProperty("statusState", status)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def set_idle(self) -> None:
        self.hours_input.setEnabled(True)
        self.minutes_input.setEnabled(True)
        self.preset_value_label.setText(f"{self.hours_input.value():02d}:{self.minutes_input.value():02d}")
        self.countdown_value_label.setText("--:--:--")
        self.countdown_value_label.setStyleSheet(COUNTDOWN_VALUE_STYLE)
        self._set_row_status_state("idle")
        self._set_status_badge("空闲", "#4b5563", "#f3f4f6")
        self.add_time_button.setEnabled(False)
        self.add_time_button.setStyleSheet(DISABLED_BUTTON_STYLE)
        self.action_button.setText("开始")
        self.action_button.setStyleSheet(PRIMARY_BUTTON_STYLE)

    def set_running(self, preset_text: str, countdown_text: str, status: str) -> None:
        self.preset_value_label.setText(preset_text)
        self.countdown_value_label.setText(countdown_text)
        self.hours_input.setEnabled(False)
        self.minutes_input.setEnabled(False)
        self.add_time_button.setEnabled(True)
        self.add_time_button.setStyleSheet(PRIMARY_BUTTON_STYLE)
        self.action_button.setText("截止")
        self.action_button.setStyleSheet(DANGER_BUTTON_STYLE)
        self._set_row_status_state(status)

        if status == "warning":
            self.countdown_value_label.setStyleSheet(COUNTDOWN_WARNING_STYLE)
            self._set_status_badge("即将到时", "#8a5a13", "#f8e7bf")
            return

        if status == "overtime":
            self.countdown_value_label.setStyleSheet(COUNTDOWN_OVERTIME_STYLE)
            self._set_status_badge("已超时", "#943126", "#f7d7d3")
            return

        self.countdown_value_label.setStyleSheet(COUNTDOWN_VALUE_STYLE)
        self._set_status_badge("进行中", "#111827", "#e5e7eb")

    def _handle_add_time(self) -> None:
        if self._add_time_handler is not None:
            self._add_time_handler(self.table_id)

    def _handle_action(self) -> None:
        if self.action_button.text() == "开始":
            if self._start_handler is not None:
                self._start_handler(self.table_id)
            return
        if self._stop_handler is not None:
            self._stop_handler(self.table_id)
