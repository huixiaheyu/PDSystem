from __future__ import annotations

from datetime import datetime
import sys

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.config import (
    AppConfig,
    clamp_hours,
    clamp_minutes,
    clamp_table_count,
    clamp_warning_minutes,
)
from app.logger import logger
from app.models import TableState
from app.table_card import (
    ACTION_COLUMN_WIDTH,
    COUNTDOWN_COLUMN_WIDTH,
    INPUT_COLUMN_WIDTH,
    NoWheelSpinBox,
    PRESET_COLUMN_WIDTH,
    ROW_COLUMN_SPACING,
    ROW_HORIZONTAL_PADDING,
    STATUS_COLUMN_WIDTH,
    TABLE_COLUMN_WIDTH,
    TableCard,
)

MAIN_WINDOW_STYLE = "background-color: #fff1f6;"
INPUT_STYLE = """
QSpinBox {
    min-width: 84px;
    min-height: 38px;
    padding: 0 10px;
    border: 2px solid #ffb3c7;
    border-radius: 4px;
    background: #ffffff;
    color: #5b245d;
    font-size: 15px;
    font-weight: 700;
    outline: none;
}
QSpinBox:focus {
    border: 2px solid #7b61ff;
}
QSpinBox::up-button, QSpinBox::down-button {
    width: 0px;
    height: 0px;
    border: none;
    background: transparent;
}
QSpinBox::up-arrow, QSpinBox::down-arrow {
    width: 0px;
    height: 0px;
}
"""

PRIMARY_BUTTON_STYLE = """
QPushButton {
    min-height: 38px;
    padding: 0 16px;
    border: 2px solid #7b61ff;
    border-radius: 4px;
    background-color: #7b61ff;
    color: #ffffff;
    font-size: 14px;
    font-weight: 800;
    outline: none;
}
QPushButton:hover {
    background-color: #6a52ea;
}
QPushButton:pressed {
    background-color: #5941d3;
}
QPushButton:focus {
    outline: none;
}
"""

SECONDARY_BUTTON_STYLE = """
QPushButton {
    min-height: 38px;
    padding: 0 16px;
    border: 2px solid #ffb84d;
    border-radius: 4px;
    background-color: #fff4d6;
    color: #9a4f00;
    font-size: 14px;
    font-weight: 700;
    outline: none;
}
QPushButton:hover {
    background-color: #ffe8b8;
}
QPushButton:pressed {
    background-color: #ffdc96;
}
QPushButton:focus {
    outline: none;
}
"""

DIALOG_STYLE = "background-color: #fff6ef;"
DIALOG_TITLE_STYLE = "font-size: 20px; font-weight: 800; color: #ff4f8b; border: none;"
DIALOG_SUBTITLE_STYLE = "font-size: 12px; font-weight: 600; color: #7a5892; border: none;"
DIALOG_SECTION_TITLE_STYLE = "font-size: 15px; font-weight: 800; color: #7b61ff; border: none;"
INLINE_UNIT_LABEL_STYLE = "font-size: 13px; font-weight: 700; color: #24a86a; border: none;"
TOOLBAR_CARD_STYLE = (
    "QFrame {background: #ffffff; border: 2px solid #ffb3c7; border-radius: 8px;}"
)
TOOLBAR_TITLE_STYLE = "font-size: 22px; font-weight: 800; color: #ff4f8b; border: none;"
TOOLBAR_SUBTITLE_STYLE = "font-size: 12px; font-weight: 600; color: #7a5892; border: none;"
SUMMARY_LABEL_STYLE = "font-size: 11px; font-weight: 800; color: #7b61ff; border: none; letter-spacing: 0.4px;"
SUMMARY_VALUE_STYLE = "font-size: 20px; font-weight: 800; color: #ff7a00; border: none;"
SUMMARY_CHIP_STYLE = """
QFrame {
    background: #fff8d9;
    border: 2px solid #d9f05f;
    border-radius: 6px;
}
"""

DIALOG_CARD_STYLE = """
QFrame {
    background: #ffffff;
    border: 2px solid #ffd36e;
    border-radius: 8px;
}
"""

LIST_PANEL_STYLE = """
QFrame {
    background: #ffffff;
    border: 2px solid #ffb3c7;
    border-radius: 10px;
}
"""

LIST_HEADER_ROW_STYLE = """
QFrame {
    border: none;
}
"""

LIST_HEADER_TEXT_STYLE = "font-size: 12px; font-weight: 800; color: #7b61ff; border: none;"
HEADER_ACTION_BUTTON_STYLE = (
    "QPushButton {min-width: 96px; max-width: 96px; min-height: 40px; padding: 0; border: none; "
    "background: transparent; color: #7b61ff; font-size: 12px; font-weight: 800; text-align: center;}"
)


class SettingsDialog(QDialog):
    def __init__(self, config: AppConfig, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setModal(True)
        self.resize(500, 320)
        self.setStyleSheet(DIALOG_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        header_card = QFrame()
        header_card.setStyleSheet(DIALOG_CARD_STYLE)
        header_layout = QVBoxLayout(header_card)
        header_layout.setContentsMargins(18, 16, 18, 16)
        header_layout.setSpacing(4)

        title = QLabel("默认参数设置")
        title.setStyleSheet(DIALOG_TITLE_STYLE)
        header_layout.addWidget(title)

        subtitle = QLabel("调整桌位数量、默认时长和提醒阈值。")
        subtitle.setStyleSheet(DIALOG_SUBTITLE_STYLE)
        subtitle.setWordWrap(True)
        header_layout.addWidget(subtitle)
        layout.addWidget(header_card)

        form_card = QFrame()
        form_card.setStyleSheet(DIALOG_CARD_STYLE)
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(18, 16, 18, 16)
        form_layout.setSpacing(12)

        form_title = QLabel("基础配置")
        form_title.setStyleSheet(DIALOG_SECTION_TITLE_STYLE)
        form_layout.addWidget(form_title)

        form = QFormLayout()
        form.setHorizontalSpacing(20)
        form.setVerticalSpacing(16)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.table_count_input = NoWheelSpinBox()
        self.table_count_input.setRange(1, 99)
        self.table_count_input.setValue(config.table_count)
        self.table_count_input.setStyleSheet(INPUT_STYLE)
        form.addRow("总桌数", self.table_count_input)

        self.default_hours_input = NoWheelSpinBox()
        self.default_hours_input.setRange(0, 23)
        self.default_hours_input.setValue(config.default_hours)
        self.default_hours_input.setStyleSheet(INPUT_STYLE)

        self.default_minutes_input = NoWheelSpinBox()
        self.default_minutes_input.setRange(0, 59)
        self.default_minutes_input.setValue(config.default_minutes)
        self.default_minutes_input.setStyleSheet(INPUT_STYLE)

        default_time_row = QWidget()
        default_time_layout = QHBoxLayout(default_time_row)
        default_time_layout.setContentsMargins(0, 0, 0, 0)
        default_time_layout.setSpacing(8)
        default_time_layout.addWidget(self.default_hours_input)
        default_time_layout.addWidget(self._build_inline_unit_label("时"))
        default_time_layout.addWidget(self.default_minutes_input)
        default_time_layout.addWidget(self._build_inline_unit_label("分"))
        default_time_layout.addStretch()
        form.addRow("默认时间", default_time_row)

        self.warning_minutes_input = NoWheelSpinBox()
        self.warning_minutes_input.setRange(0, 24 * 60)
        self.warning_minutes_input.setValue(config.warning_minutes)
        self.warning_minutes_input.setStyleSheet(INPUT_STYLE)
        form.addRow("提前提醒(分钟)", self.warning_minutes_input)

        form_layout.addLayout(form)
        layout.addWidget(form_card)

        self.cancel_button = QPushButton("取消")
        self.cancel_button.setStyleSheet(SECONDARY_BUTTON_STYLE)
        self.cancel_button.clicked.connect(self.reject)

        self.save_button = QPushButton("保存")
        self.save_button.setStyleSheet(PRIMARY_BUTTON_STYLE)
        self.save_button.clicked.connect(self.accept)

        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 0, 0, 0)
        button_row.setSpacing(12)
        button_row.addWidget(self.cancel_button)
        button_row.addStretch()
        button_row.addWidget(self.save_button)
        layout.addLayout(button_row)

    def get_values(self) -> tuple[int, int, int, int]:
        return (
            self.table_count_input.value(),
            self.default_hours_input.value(),
            self.default_minutes_input.value(),
            self.warning_minutes_input.value(),
        )

    def _build_inline_unit_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(INLINE_UNIT_LABEL_STYLE)
        return label


class ConfirmDialog(QDialog):
    def __init__(self, title_text: str, body_text: str, confirm_text: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title_text)
        self.setModal(True)
        self.resize(420, 240)
        self.setStyleSheet(DIALOG_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        header_card = QFrame()
        header_card.setStyleSheet(DIALOG_CARD_STYLE)
        header_layout = QVBoxLayout(header_card)
        header_layout.setContentsMargins(18, 16, 18, 16)
        header_layout.setSpacing(6)

        title = QLabel(title_text)
        title.setStyleSheet(DIALOG_TITLE_STYLE)
        header_layout.addWidget(title)

        subtitle = QLabel(body_text)
        subtitle.setStyleSheet(DIALOG_SUBTITLE_STYLE)
        subtitle.setWordWrap(True)
        header_layout.addWidget(subtitle)
        layout.addWidget(header_card)

        self.cancel_button = QPushButton("取消")
        self.cancel_button.setStyleSheet(SECONDARY_BUTTON_STYLE)
        self.cancel_button.clicked.connect(self.reject)

        self.confirm_button = QPushButton(confirm_text)
        self.confirm_button.setStyleSheet(PRIMARY_BUTTON_STYLE)
        self.confirm_button.clicked.connect(self.accept)

        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 0, 0, 0)
        button_row.setSpacing(12)
        button_row.addWidget(self.cancel_button)
        button_row.addStretch()
        button_row.addWidget(self.confirm_button)
        layout.addLayout(button_row)


class AddTimeDialog(QDialog):
    def __init__(self, table_id: int, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("加时")
        self.setModal(True)
        self.resize(420, 260)
        self.setStyleSheet(DIALOG_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        header_card = QFrame()
        header_card.setStyleSheet(DIALOG_CARD_STYLE)
        header_layout = QVBoxLayout(header_card)
        header_layout.setContentsMargins(18, 16, 18, 16)
        header_layout.setSpacing(4)

        title = QLabel(f"{table_id:02d}号桌加时")
        title.setStyleSheet(DIALOG_TITLE_STYLE)
        header_layout.addWidget(title)

        subtitle = QLabel("请选择要追加的小时和分钟。")
        subtitle.setStyleSheet(DIALOG_SUBTITLE_STYLE)
        subtitle.setWordWrap(True)
        header_layout.addWidget(subtitle)
        layout.addWidget(header_card)

        form_card = QFrame()
        form_card.setStyleSheet(DIALOG_CARD_STYLE)
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(18, 16, 18, 16)
        form_layout.setSpacing(12)

        form_title = QLabel("加时时长")
        form_title.setStyleSheet(DIALOG_SECTION_TITLE_STYLE)
        form_layout.addWidget(form_title)

        time_row = QWidget()
        time_layout = QHBoxLayout(time_row)
        time_layout.setContentsMargins(0, 0, 0, 0)
        time_layout.setSpacing(8)

        self.hours_input = NoWheelSpinBox()
        self.hours_input.setRange(0, 23)
        self.hours_input.setStyleSheet(INPUT_STYLE)
        time_layout.addWidget(self.hours_input)
        time_layout.addWidget(self._build_inline_unit_label("时"))

        self.minutes_input = NoWheelSpinBox()
        self.minutes_input.setRange(0, 59)
        self.minutes_input.setStyleSheet(INPUT_STYLE)
        time_layout.addWidget(self.minutes_input)
        time_layout.addWidget(self._build_inline_unit_label("分"))
        time_layout.addStretch()

        form_layout.addWidget(time_row)
        layout.addWidget(form_card)

        self.cancel_button = QPushButton("取消")
        self.cancel_button.setStyleSheet(SECONDARY_BUTTON_STYLE)
        self.cancel_button.clicked.connect(self.reject)

        self.confirm_button = QPushButton("确定")
        self.confirm_button.setStyleSheet(PRIMARY_BUTTON_STYLE)
        self.confirm_button.clicked.connect(self.accept)

        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 0, 0, 0)
        button_row.setSpacing(12)
        button_row.addWidget(self.cancel_button)
        button_row.addStretch()
        button_row.addWidget(self.confirm_button)
        layout.addLayout(button_row)

    def get_minutes(self) -> int:
        return self.hours_input.value() * 60 + self.minutes_input.value()

    def _build_inline_unit_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(INLINE_UNIT_LABEL_STYLE)
        return label


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.config = AppConfig.load()
        self.table_states: dict[int, TableState] = {}
        self.table_cards: dict[int, TableCard] = {}
        self._app_started_logged = False

        self.setWindowTitle("拼豆店计时系统")
        self.resize(1380, 860)

        self.setStyleSheet(MAIN_WINDOW_STYLE)

        central = QWidget()
        central.setStyleSheet(MAIN_WINDOW_STYLE)
        self.setCentralWidget(central)
        self.root_layout = QVBoxLayout(central)
        self.root_layout.setContentsMargins(24, 24, 24, 24)
        self.root_layout.setSpacing(14)

        self._build_toolbar()
        self._build_list_area()
        self._rebuild_cards(self.config.table_count)

        self.refresh_timer = QTimer(self)
        self.refresh_timer.setInterval(1000)
        self.refresh_timer.timeout.connect(self.refresh_cards)
        self.refresh_timer.start()

    def _build_toolbar(self) -> None:
        self.toolbar_card = QFrame()
        self.toolbar_card.setStyleSheet(TOOLBAR_CARD_STYLE)
        toolbar_layout = QHBoxLayout(self.toolbar_card)
        toolbar_layout.setContentsMargins(18, 14, 18, 14)
        toolbar_layout.setSpacing(14)

        title_wrap = QVBoxLayout()
        title_wrap.setSpacing(2)

        title = QLabel("拼豆店桌面计时系统")
        title.setStyleSheet(TOOLBAR_TITLE_STYLE)
        title_wrap.addWidget(title)

        subtitle = QLabel("桌位计时、提醒和现场状态管理")
        subtitle.setStyleSheet(TOOLBAR_SUBTITLE_STYLE)
        title_wrap.addWidget(subtitle)

        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(10)
        summary_layout.addWidget(self._build_summary_chip("桌位总数", str(self.config.table_count)))
        summary_layout.addWidget(self._build_summary_chip("进行中", "0"))
        summary_layout.addWidget(self._build_summary_chip("即将到时", "0"))
        summary_layout.addWidget(self._build_summary_chip("已超时", "0"))
        summary_layout.addStretch()
        title_wrap.addLayout(summary_layout)

        toolbar_layout.addLayout(title_wrap, 1)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        self.settings_button = QPushButton("设置")
        self.settings_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_button.setStyleSheet(PRIMARY_BUTTON_STYLE)
        self.settings_button.clicked.connect(self.open_settings_dialog)
        button_layout.addWidget(self.settings_button)

        self.fullscreen_button = QPushButton("进入全屏")
        self.fullscreen_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.fullscreen_button.setStyleSheet(SECONDARY_BUTTON_STYLE)
        self.fullscreen_button.clicked.connect(self.toggle_fullscreen)
        button_layout.addWidget(self.fullscreen_button)

        toolbar_layout.addLayout(button_layout)

        self.root_layout.addWidget(self.toolbar_card)

    def _build_summary_chip(self, label_text: str, value_text: str) -> QFrame:
        chip = QFrame()
        chip.setStyleSheet(SUMMARY_CHIP_STYLE)
        chip.setMinimumWidth(96)

        layout = QVBoxLayout(chip)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(1)

        label = QLabel(label_text)
        label.setStyleSheet(SUMMARY_LABEL_STYLE)
        layout.addWidget(label)

        value = QLabel(value_text)
        value.setStyleSheet(SUMMARY_VALUE_STYLE)
        layout.addWidget(value)

        if label_text == "桌位总数":
            self.table_count_summary_label = value
        elif label_text == "进行中":
            self.running_summary_label = value
        elif label_text == "即将到时":
            self.warning_summary_label = value
        else:
            self.overtime_summary_label = value

        return chip

    def _build_list_area(self) -> None:
        self.list_panel = QFrame()
        self.list_panel.setStyleSheet(LIST_PANEL_STYLE)
        panel_layout = QVBoxLayout(self.list_panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(self.scroll_area.Shape.NoFrame)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")

        self.list_container = QWidget()
        self.list_container.setStyleSheet("background: transparent;")
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(0)

        self.scroll_area.setWidget(self.list_container)
        panel_layout.addWidget(self.scroll_area)
        self.root_layout.addWidget(self.list_panel, 1)


    def open_settings_dialog(self) -> None:
        dialog = SettingsDialog(self.config, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        confirm_dialog = ConfirmDialog("确认保存", "确定要保存新的默认设置吗？", "保存", self)
        if confirm_dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self.apply_config(*dialog.get_values())

    def _describe_config(self) -> str:
        return (
            f"table_count={self.config.table_count}, "
            f"default_hours={self.config.default_hours}, "
            f"default_minutes={self.config.default_minutes}, "
            f"warning_minutes={self.config.warning_minutes}, "
            f"start_fullscreen={self.config.start_fullscreen}"
        )

    def apply_config(
        self,
        table_count: int,
        default_hours: int,
        default_minutes: int,
        warning_minutes: int,
    ) -> None:
        previous_config = self._describe_config()
        table_count = clamp_table_count(table_count)
        default_hours = clamp_hours(default_hours)
        default_minutes = clamp_minutes(default_minutes)
        warning_minutes = clamp_warning_minutes(warning_minutes)
        self.config.table_count = table_count
        self.config.default_hours = default_hours
        self.config.default_minutes = default_minutes
        self.config.warning_minutes = warning_minutes
        self.config.save()
        logger.info("配置已更新", before=previous_config, after=self._describe_config())
        self._rebuild_cards(table_count)
        self.refresh_cards()

    def toggle_fullscreen(self) -> None:
        if self.isFullScreen():
            self.showNormal()
            self.config.start_fullscreen = False
            self.config.save()
            self.fullscreen_button.setText("进入全屏")
            logger.info("切换窗口模式", mode="windowed")
            return
        self.showFullScreen()
        self.config.start_fullscreen = True
        self.config.save()
        self.fullscreen_button.setText("退出全屏")
        logger.info("切换窗口模式", mode="fullscreen")

    def _rebuild_cards(self, table_count: int) -> None:
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self.table_states = {
            table_id: self.table_states.get(table_id, TableState(table_id=table_id))
            for table_id in range(1, table_count + 1)
        }
        self.table_cards = {}

        for table_id in range(1, table_count + 1):
            card = TableCard(table_id, self.config.default_hours, self.config.default_minutes)
            card.set_action_handlers(self.start_table, self.stop_table, self.add_time_to_table)
            state = self.table_states[table_id]
            if not state.running:
                state.logged_status = "idle"
                card.set_inputs(self.config.default_hours, self.config.default_minutes)
            self.list_layout.addWidget(card)
            self.table_cards[table_id] = card

        self.list_layout.addStretch(1)

    def start_table(self, table_id: int) -> None:
        card = self.table_cards[table_id]
        preset_minutes = card.get_input_minutes()
        if preset_minutes <= 0:
            logger.warning("开始计时失败", table_id=table_id, reason="preset_minutes<=0")
            QMessageBox.warning(self, "预设时间无效", "请为该桌设置大于 0 的预设时间。")
            return
        self.table_states[table_id].start(datetime.now(), preset_minutes)
        logger.info("开始计时", table_id=table_id, preset_minutes=preset_minutes)
        self.refresh_cards()

    def stop_table(self, table_id: int) -> None:
        confirm_dialog = ConfirmDialog("确认截止", f"确定要截止 {table_id} 号桌吗？", "截止", self)
        if confirm_dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self.table_states[table_id].reset()
        logger.info("截止计时", table_id=table_id)
        self.table_cards[table_id].set_idle()
        self.refresh_cards()

    def add_time_to_table(self, table_id: int) -> None:
        state = self.table_states[table_id]
        if not state.running:
            logger.warning("加时失败", table_id=table_id, reason="table_not_running")
            return

        dialog = AddTimeDialog(table_id, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        added_minutes = dialog.get_minutes()
        if added_minutes <= 0:
            logger.warning("加时失败", table_id=table_id, reason="added_minutes<=0")
            QMessageBox.warning(self, "加时时间无效", "请设置大于 0 的加时时间。")
            return

        state.add_minutes(added_minutes)
        logger.info("追加时长", table_id=table_id, added_minutes=added_minutes, preset_minutes=state.preset_minutes)
        self.refresh_cards()

    def refresh_cards(self) -> None:
        now = datetime.now()
        warning_seconds = self.config.warning_minutes * 60
        running_count = 0
        warning_count = 0
        overtime_count = 0

        for table_id, state in self.table_states.items():
            card = self.table_cards[table_id]
            if not state.running or state.started_at is None:
                state.logged_status = "idle"
                card.set_idle()
                continue

            running_count += 1
            elapsed_seconds = max(0, int((now - state.started_at).total_seconds()))
            preset_seconds = state.preset_minutes * 60
            remaining_seconds = preset_seconds - elapsed_seconds
            if remaining_seconds < 0:
                overtime_count += 1
            preset_text = self._format_minutes(state.preset_minutes)
            countdown_text = self._format_countdown(remaining_seconds)
            status = self._resolve_status(remaining_seconds, warning_seconds)
            if status == "warning":
                warning_count += 1
            self._log_status_transition(table_id, state, status, remaining_seconds)
            card.set_running(preset_text, countdown_text, status)

        self.table_count_summary_label.setText(str(self.config.table_count))
        self.running_summary_label.setText(str(running_count))
        self.warning_summary_label.setText(str(warning_count))
        self.overtime_summary_label.setText(str(overtime_count))

    def _log_status_transition(
        self,
        table_id: int,
        state: TableState,
        status: str,
        remaining_seconds: int,
    ) -> None:
        if state.logged_status == status:
            return
        if status == "warning":
            logger.info(
                "进入提醒状态",
                table_id=table_id,
                remaining_seconds=remaining_seconds,
                warning_minutes=self.config.warning_minutes,
            )
        elif status == "overtime":
            logger.warning("进入超时状态", table_id=table_id, remaining_seconds=remaining_seconds)
        state.logged_status = status

    def _resolve_status(self, remaining_seconds: int, warning_seconds: int) -> str:
        if remaining_seconds < 0:
            return "overtime"
        if warning_seconds > 0 and remaining_seconds <= warning_seconds:
            return "warning"
        return "normal"

    def _format_minutes(self, total_minutes: int) -> str:
        hours, minutes = divmod(total_minutes, 60)
        return f"{hours:02d}:{minutes:02d}"

    def _format_countdown(self, remaining_seconds: int) -> str:
        prefix = "-" if remaining_seconds < 0 else ""
        seconds = abs(remaining_seconds)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{prefix}{hours:02d}:{minutes:02d}:{seconds:02d}"

    def showEvent(self, event) -> None:
        super().showEvent(event)
        if self._app_started_logged:
            return
        logger.info(
            "应用启动",
            table_count=self.config.table_count,
            default_minutes=self.config.default_hours * 60 + self.config.default_minutes,
            warning_minutes=self.config.warning_minutes,
            start_fullscreen=self.config.start_fullscreen,
        )
        self._app_started_logged = True

    def closeEvent(self, event) -> None:
        logger.info(
            "应用退出",
            running_tables=sum(1 for state in self.table_states.values() if state.running),
            overtime_tables=sum(
                1
                for state in self.table_states.values()
                if state.running and state.started_at is not None and self._resolve_status(
                    state.preset_minutes * 60 - max(0, int((datetime.now() - state.started_at).total_seconds())),
                    self.config.warning_minutes * 60,
                )
                == "overtime"
            ),
        )
        super().closeEvent(event)


def run() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showFullScreen() if window.config.start_fullscreen else window.show()
    app.aboutToQuit.connect(lambda: logger.info("Qt 事件循环结束"))
    sys.exit(app.exec())
