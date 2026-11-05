from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import QPoint, QTime, Qt, QTimer
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QCheckBox, QFrame, QHBoxLayout, QLabel, QMainWindow, QPlainTextEdit, QProgressBar,
    QPushButton, QScrollArea, QSpinBox, QStackedWidget, QTimeEdit, QVBoxLayout, QWidget,
)

from .art import Avatar, app_icon

STYLE = """
QWidget { font-family: 'Microsoft YaHei UI'; font-size: 13px; color: #253d36; }
QMainWindow, QWidget#content { background: #f6f7f2; }
QFrame#sidebar { background: #edf0e7; border-right: 1px solid #e0e5d9; }
QFrame#card { background: #ffffff; border: 1px solid #e2e7dd; border-radius: 18px; }
QFrame#hero { background: #183f36; border-radius: 20px; }
QFrame#hero QLabel { color: #f3f8ed; background: transparent; }
QLabel#muted { color: #7c8b80; font-size: 12px; }
QLabel#eyebrow { font-family: 'Consolas'; color: #7c8b80; font-size: 11px; letter-spacing: 2px; }
QLabel#title { font-size: 25px; font-weight: 700; }
QLabel#section { font-size: 17px; font-weight: 700; }
QLabel#quote { font-size: 16px; line-height: 1.6; }
QPushButton { border: 1px solid #dce3d6; background: #ffffff; border-radius: 9px; padding: 10px 14px; }
QPushButton:hover { background: #eef5e7; border-color: #a9bf96; }
QPushButton:pressed { background: #deebd3; }
QPushButton#primary { background: #c6eb9f; color: #183f36; border: none; font-weight: 700; }
QPushButton#primary:hover { background: #b7df8e; }
QPushButton#nav { text-align: left; background: transparent; border: none; padding: 13px 16px; }
QPushButton#nav:checked { background: #dce6d2; color: #214a36; font-weight: 700; }
QPushButton#subtle { border: none; background: transparent; color: #697f70; padding: 5px; }
QPushButton:disabled { color: #a2aca0; background: #f2f3ee; }
QProgressBar { background: #ecf0e5; border: none; border-radius: 5px; height: 9px; }
QProgressBar::chunk { background: #9bc873; border-radius: 5px; }
QSpinBox, QTimeEdit, QPlainTextEdit { border: 1px solid #d9e0d2; border-radius: 8px; padding: 8px; background: white; }
QCheckBox { spacing: 10px; }
QCheckBox::indicator { width: 18px; height: 18px; border: 1px solid #bdcbb3; border-radius: 5px; background: white; }
QCheckBox::indicator:checked { background: #83b66a; border: 3px solid #d4e7c4; }
QScrollArea { border: none; background: transparent; }
QScrollArea > QWidget > QWidget { background: transparent; }
"""


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
        self.setStyleSheet(STYLE + "QFrame#bubble { background: #f8fbee; border: 1px solid #d4dfc7; border-radius: 17px; } QLabel#petstatus { background: #e6eddb; border-radius: 12px; font-size: 11px; color: #39543e; }")
        self.bubble = QFrame(self)
        self.bubble.setObjectName("bubble")
        self.bubble.setGeometry(5, 6, 320, 172)
        layout = QVBoxLayout(self.bubble)
        layout.setContentsMargins(16, 11, 16, 12)
        top = QHBoxLayout()
        top.addWidget(label("ALAN / 大水时间", "eyebrow"))
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
        self.status = label("下次喝水 45:00", "petstatus")
        self.status.setParent(self)
        self.status.setGeometry(72, 377, 186, 24)
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.bubble.hide)

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


class ControlPanel(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("喝大水 · 邵艾伦风格桌宠")
        self.setWindowIcon(app_icon())
        self.setMinimumSize(920, 720)
        self.resize(980, 760)
        self.setStyleSheet(STYLE)
        root = QWidget()
        self.setCentralWidget(root)
        outer = QHBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(166)
        left = QVBoxLayout(sidebar)
        left.setContentsMargins(16, 28, 16, 22)
        left.addWidget(label("大 水", "title"))
        left.addWidget(label("ALAN WATER CLUB", "eyebrow"))
        left.addSpacing(30)
        self.stack = QStackedWidget()
        self.nav = []
        for index, text in enumerate(["01   今日大水", "02   提醒设置", "03   台词研究"]):
            item = button(text, lambda checked=False, i=index: self.navigate(i), "nav")
            item.setCheckable(True)
            left.addWidget(item)
            self.nav.append(item)
        left.addStretch()
        left.addWidget(label("一口大水\n一个小小的开始。", wrap=True))
        left.addSpacing(16)
        left.addWidget(label("非官方 · 风格模拟\nv0.1.0 / LOCAL FIRST", "muted"))
        outer.addWidget(sidebar)
        content = QWidget()
        content.setObjectName("content")
        right = QVBoxLayout(content)
        right.setContentsMargins(28, 24, 28, 20)
        right.addWidget(self.stack)
        outer.addWidget(content, 1)
        self.build_dashboard()
        self.build_settings()
        self.build_quotes()
        self.navigate(0)

    def navigate(self, index):
        self.stack.setCurrentIndex(index)
        for i, item in enumerate(self.nav):
            item.setChecked(i == index)

    def build_dashboard(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        row = QHBoxLayout()
        heading = QVBoxLayout()
        self.date_label = label("", "eyebrow")
        heading.addWidget(self.date_label)
        heading.addWidget(label("今天，也记得喝大水。", "title"))
        row.addLayout(heading)
        row.addStretch()
        row.addWidget(button("找到桌宠 ↗", self.controller.show_pet))
        layout.addLayout(row)
        hero = QFrame()
        hero.setObjectName("hero")
        hero.setMinimumHeight(240)
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(25, 25, 20, 20)
        words = QVBoxLayout()
        words.addWidget(label("A LITTLE WATER. A LITTLE CONTROL.", "eyebrow"))
        headline = label("先喝一口大水，\n再做下一件事。")
        headline.setStyleSheet("font-size: 29px; font-weight: 700;")
        words.addWidget(headline)
        words.addWidget(label("不急着改变一切。先做一件照顾自己的小事。", wrap=True))
        words.addSpacing(10)
        action = button("＋  我喝水了", self.controller.record_drink, "primary")
        action.setMinimumWidth(175)
        words.addWidget(action, 0, Qt.AlignmentFlag.AlignLeft)
        hero_layout.addLayout(words, 1)
        self.preview = Avatar()
        self.preview.setFixedSize(180, 206)
        hero_layout.addWidget(self.preview)
        layout.addWidget(hero)
        stats, stat_layout = card()
        stat_heading = QHBoxLayout()
        stat_heading.addWidget(label("今日补水记录", "section"))
        stat_heading.addStretch()
        self.undo_button = button("撤销上一笔", self.undo, "subtle")
        stat_heading.addWidget(self.undo_button)
        stat_layout.addLayout(stat_heading)
        metrics = QHBoxLayout()
        self.total_label = label("0 ml")
        self.total_label.setStyleSheet("font-size: 32px; font-weight: 700;")
        metrics.addWidget(self.total_label)
        metrics.addStretch()
        self.goal_label = label("", "muted")
        metrics.addWidget(self.goal_label, 0, Qt.AlignmentFlag.AlignBottom)
        stat_layout.addLayout(metrics)
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(9)
        stat_layout.addWidget(self.progress)
        self.history_label = label("还没有记录。喝完再点，按实际情况记。", "muted", True)
        stat_layout.addWidget(self.history_label)
        layout.addWidget(stats)
        bottom = QHBoxLayout()
        quote_card, qlayout = card()
        qlayout.addWidget(label("ALAN 的桌边碎碎念", "eyebrow"))
        self.quote_label = label("把大水放在手边。照顾自己，也从一件小事开始。", "quote", True)
        qlayout.addWidget(self.quote_label, 1)
        qlayout.addWidget(button("换一句", self.controller.say_something, "subtle"), 0, Qt.AlignmentFlag.AlignLeft)
        bottom.addWidget(quote_card, 3)
        timer_card, tlayout = card()
        tlayout.addWidget(label("下一口大水", "eyebrow"))
        self.countdown = label("45:00")
        self.countdown.setStyleSheet("font-family: Consolas; font-size: 30px; font-weight: 700;")
        tlayout.addWidget(self.countdown)
        self.pause_button = button("暂停提醒", self.controller.toggle_pause)
        tlayout.addWidget(self.pause_button)
        bottom.addWidget(timer_card, 2)
        layout.addLayout(bottom, 1)
        layout.addWidget(label("大瓶在手，分次适量喝。目标是个人记账设置，请按自身需要调整。", "muted", True))
        self.stack.addWidget(page)

    def build_settings(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(label("MAKE IT YOUR RHYTHM", "eyebrow"))
        layout.addWidget(label("你的节奏，你来定。", "title"))
        layout.addSpacing(16)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 4, 0)
        frame, form = card()
        form.addWidget(label("提醒与记录", "section"))
        self.interval = self.spin_row(form, "喝水提醒间隔", 5, 180, " 分钟")
        self.cup = self.spin_row(form, "每次记录水量", 50, 1000, " ml")
        self.goal = self.spin_row(form, "个人每日记录目标", 200, 5000, " ml")
        self.chatter = QCheckBox("允许桌边碎碎念")
        form.addWidget(self.chatter)
        self.chatter_interval = self.spin_row(form, "碎碎念间隔", 5, 180, " 分钟")
        self.time_aware = QCheckBox("按早晨、下午、晚上匹配台词")
        form.addWidget(self.time_aware)
        self.notifications = QCheckBox("喝水时同时发送系统通知")
        form.addWidget(self.notifications)
        body_layout.addWidget(frame)
        quiet_card, quiet_layout = card()
        quiet_layout.addWidget(label("留一点安静时间", "section"))
        self.quiet = QCheckBox("开启免打扰（喝水提醒和碎碎念都会暂停）")
        quiet_layout.addWidget(self.quiet)
        quiet_row = QHBoxLayout()
        quiet_row.addWidget(label("从"))
        self.quiet_start = QTimeEdit()
        self.quiet_start.setDisplayFormat("HH:mm")
        quiet_row.addWidget(self.quiet_start)
        quiet_row.addWidget(label("到"))
        self.quiet_end = QTimeEdit()
        self.quiet_end.setDisplayFormat("HH:mm")
        quiet_row.addWidget(self.quiet_end)
        quiet_row.addStretch()
        quiet_layout.addLayout(quiet_row)
        quiet_layout.addWidget(label("支持跨午夜；起止时间相同表示全天开放。", "muted"))
        body_layout.addWidget(quiet_card)
        body_layout.addWidget(label("喝水量仅用于个人记录，不是医学建议；需限水时按医嘱设置。", "muted", True))
        body_layout.addStretch()
        scroll.setWidget(body)
        layout.addWidget(scroll, 1)
        footer = QHBoxLayout()
        self.saved_label = label("修改后点击保存", "muted")
        footer.addWidget(self.saved_label)
        footer.addStretch()
        footer.addWidget(button("保存设置", self.save_settings, "primary"))
        layout.addLayout(footer)
        self.stack.addWidget(page)
        self.load_settings()

    def spin_row(self, layout, title, low, high, suffix):
        row = QHBoxLayout()
        row.addWidget(label(title))
        row.addStretch()
        obj = QSpinBox()
        obj.setRange(low, high)
        obj.setSuffix(suffix)
        obj.setFixedWidth(140)
        row.addWidget(obj)
        layout.addLayout(row)
        return obj

    def load_settings(self):
        s = self.controller.store.settings
        for widget, value in [(self.interval, s.interval_minutes), (self.cup, s.cup_ml),
                              (self.goal, s.goal_ml), (self.chatter_interval, s.chatter_minutes)]:
            widget.setValue(value)
        for widget, value in [(self.chatter, s.chatter_enabled), (self.time_aware, s.time_aware),
                              (self.quiet, s.quiet_enabled), (self.notifications, s.notifications)]:
            widget.setChecked(value)
        self.quiet_start.setTime(QTime.fromString(s.quiet_start, "HH:mm"))
        self.quiet_end.setTime(QTime.fromString(s.quiet_end, "HH:mm"))

    def save_settings(self):
        s = self.controller.store.settings
        s.interval_minutes, s.cup_ml, s.goal_ml = self.interval.value(), self.cup.value(), self.goal.value()
        s.chatter_minutes = self.chatter_interval.value()
        s.chatter_enabled, s.time_aware = self.chatter.isChecked(), self.time_aware.isChecked()
        s.quiet_enabled, s.notifications = self.quiet.isChecked(), self.notifications.isChecked()
        s.quiet_start = self.quiet_start.time().toString("HH:mm")
        s.quiet_end = self.quiet_end.time().toString("HH:mm")
        self.controller.scheduler.reset(datetime.now())
        if self.controller.persist():
            self.saved_label.setText("已保存 · 新的提醒周期已开始")
        self.controller.refresh()

    def build_quotes(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(label("WORDS WITH A LITTLE CHARACTER", "eyebrow"))
        layout.addWidget(label("有点道理，也有点梗。", "title"))
        layout.addSpacing(16)
        info, text = card()
        text.addWidget(label("这只桌宠怎么说话？", "section"))
        text.addWidget(label("口语化判断，偶尔自我校正，最后落在一个小动作。低频夹一点英文，聊注意力、生活节奏和可控的事。", wrap=True))
        text.addWidget(label("例如：理论可以研究很久，瓶盖只要拧一下。先喝大水，对吧？", "quote", True))
        text.addWidget(label("台词是基于截至 2026-10-15 公开内容的原创风格模拟，非本人原话。大水梗作为独立网络语境融入。", "muted", True))
        source = label('<a href="https://github.com/Roc-Dove/shao-alan-skill" style="color:#477544">查看参考 skill ↗</a>　<a href="https://github.com/1saachen/shao-alan-water-pet/blob/main/docs/research.md" style="color:#477544">调研与来源 ↗</a>')
        source.setOpenExternalLinks(True)
        text.addWidget(source)
        layout.addWidget(info)
        custom, editor = card()
        editor.addWidget(label("加几句你喜欢的台词", "section"))
        editor.addWidget(label("每行一句，保存后加入喝水提醒和随机闲聊。最多 200 句，每句 180 字。", "muted", True))
        self.custom_lines = QPlainTextEdit()
        self.custom_lines.setPlaceholderText("比如：大水已经就位，就差你拧开瓶盖了。")
        self.custom_lines.setPlainText("\n".join(self.controller.store.settings.custom_lines))
        editor.addWidget(self.custom_lines, 1)
        custom_row = QHBoxLayout()
        self.custom_status = label("仅保存在这台电脑", "muted")
        custom_row.addWidget(self.custom_status)
        custom_row.addStretch()
        custom_row.addWidget(button("保存台词", self.save_quotes, "primary"))
        editor.addLayout(custom_row)
        layout.addWidget(custom, 1)
        layout.addWidget(label("原创卡通形象 · 完全离线运行 · 无需 API Key", "muted"))
        self.stack.addWidget(page)

    def save_quotes(self):
        lines = [x.strip()[:180] for x in self.custom_lines.toPlainText().splitlines() if x.strip()][:200]
        self.controller.store.settings.custom_lines = lines
        if self.controller.persist():
            self.custom_status.setText(f"已保存 {len(lines)} 句")

    def undo(self):
        if self.controller.store.undo(datetime.now()):
            self.controller.refresh()

    def refresh(self, status, countdown):
        store = self.controller.store
        now = datetime.now()
        total = store.total(now)
        self.date_label.setText(now.strftime("%Y.%m.%d") + " / YOUR DAILY WATER")
        self.total_label.setText(f"{total:,} ml")
        self.goal_label.setText(f"个人目标 {store.settings.goal_ml:,} ml")
        self.progress.setMaximum(store.settings.goal_ml)
        self.progress.setValue(min(total, store.settings.goal_ml))
        events = store.today_events(now)
        self.undo_button.setEnabled(bool(events))
        history = "  ·  ".join(f'{x["at"][11:16]}  +{x["ml"]} ml' for x in events[-3:])
        self.history_label.setText(history or "还没有记录。喝完再点，按实际情况记。")
        self.countdown.setText(countdown)
        self.countdown.setToolTip(status)
        self.pause_button.setText("恢复提醒" if store.settings.paused else "暂停提醒")

    def closeEvent(self, event: QCloseEvent):
        if self.controller.tray.isVisible():
            event.ignore()
            self.hide()
        else:
            self.controller.quit()
