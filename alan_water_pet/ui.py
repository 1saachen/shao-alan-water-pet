from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget,
)

from .art import Avatar, app_icon
from .theme import STYLE


def label(text, name=None, wrap=False):
    obj = QLabel(text)
    if name:
        obj.setObjectName(name)
    obj.setWordWrap(wrap)
    return obj


def button(text, callback, name=None):
    obj = QPushButton(text)
    if name:
        obj.setObjectName(name)
    obj.clicked.connect(callback)
    return obj


def card():
    obj = QFrame()
    obj.setObjectName("card")
    layout = QVBoxLayout(obj)
    layout.setContentsMargins(22, 19, 22, 19)
    layout.setSpacing(12)
    return obj, layout


class PetWindow(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("喝大水 · 桌宠")
        self.setWindowIcon(app_icon())
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFixedSize(330, 402)
        self.setStyleSheet(STYLE + "QFrame#bubble { background: #ffffff; border: 1px solid #cadff7; border-radius: 17px; } QLabel#petstatus { background: #edf7ff; border-radius: 12px; font-size: 11px; color: #1768d5; }")
        self.bubble = QFrame(self)
        self.bubble.setObjectName("bubble")
        self.bubble.setGeometry(5, 6, 320, 172)
        layout = QVBoxLayout(self.bubble)
        layout.setContentsMargins(16, 11, 16, 12)
        top = QHBoxLayout()
        top.addWidget(label("艾伦提醒你", "eyebrow"))
        top.addStretch()
        top.addWidget(button("×", self.bubble.hide, "subtle"))
        layout.addLayout(top)
        self.message = label("把大水放在手边，我们慢慢来。", wrap=True)
        self.message.setMinimumHeight(54)
        layout.addWidget(self.message, 1)
        self.actions = QWidget()
        action_layout = QHBoxLayout(self.actions)
        action_layout.setContentsMargins(0, 0, 0, 0)
        self.drank_button = button("喝了", controller.record_drink, "primary")
        action_layout.addWidget(self.drank_button)
        action_layout.addWidget(button("10 分钟后", controller.snooze))
        layout.addWidget(self.actions)
        self.avatar = Avatar(self, interactive=True)
        self.avatar.setGeometry(65, 179, 200, 194)
        self.avatar.clicked.connect(controller.say_something)
        self.avatar.double_clicked.connect(controller.open_panel)
        self.avatar.drag_delta.connect(lambda delta: self.move(self.pos() + delta))
        self.avatar.drag_finished.connect(self.finish_drag)
        self.avatar.context_requested.connect(controller.open_context_menu)
        self.avatar.scale_requested.connect(controller.adjust_pet_scale)
        self.status = label("下次喝水 45:00", "petstatus")
        self.status.setParent(self)
        self.status.setGeometry(72, 377, 186, 24)
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.bubble.hide)
        self.apply_scale(controller.store.settings.pet_scale)

    def apply_scale(self, percent):
        """Scale the character, retaining readable speech and the feet's position."""
        feet = self.geometry().bottom()
        center = self.geometry().center().x()
        area = self.screen().availableGeometry()
        factor = max(.25, min(percent / 100, (area.height() - 208) / 194,
                              (area.width() - 24) / 200))
        avatar_width, avatar_height = round(200 * factor), round(194 * factor)
        width, height = max(330, avatar_width + 24), 208 + avatar_height
        self.setFixedSize(width, height)
        self.bubble.setGeometry((width - 320) // 2, 6, 320, 172)
        self.avatar.setGeometry((width - avatar_width) // 2, 179, avatar_width, avatar_height)
        self.status.setGeometry((width - 186) // 2, height - 25, 186, 24)
        self.move(center - width // 2, feet - height + 1)

    def speak(self, text, reminder=False, mood="idle"):
        self.message.setText(text if len(text) <= 75 else text[:74] + "…")
        self.message.setToolTip(text)
        self.actions.setVisible(reminder)
        self.avatar.mood = mood
        self.bubble.show()
        self.show()
        self.hide_timer.start(60000 if reminder else 22000)

    def finish_drag(self):
        self.controller.clamp_pet()
        self.controller.store.settings.position = [self.x(), self.y()]
        self.controller.persist()

    def contextMenuEvent(self, event):
        self.controller.open_context_menu(event.globalPos())
