from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import QRectF, QTime, Qt
from PySide6.QtGui import QColor, QCloseEvent, QPainter, QPen
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QFrame, QHBoxLayout, QMainWindow, QPlainTextEdit,
    QProgressBar, QScrollArea, QSlider, QSpinBox, QStackedWidget, QTimeEdit,
    QVBoxLayout, QWidget,
)

from .art import Avatar, app_icon
from .theme import STYLE
from .ui import button, card, label


def rule():
    widget = QFrame()
    widget.setObjectName("rule")
    widget.setFixedHeight(1)
    return widget


class WaterStage(QWidget):
    """A quiet water surface behind the character, rather than a generic hero card."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.avatar = Avatar(self)
        self.character_scale = 1.0
        self.setMinimumSize(230, 250)

    def resizeEvent(self, event):
        self.layout_character()

    def layout_character(self):
        width = round((self.width() - 28) * self.character_scale)
        height = round((self.height() - 22) * self.character_scale)
        self.avatar.setGeometry((self.width() - width) // 2, self.height() - 22 - height, width, height)

    def set_character_scale(self, percent):
        self.character_scale = min(1.0, .65 * percent / 100)
        self.layout_character()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        radius = min(w * .48, h * .38)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#edf7ff"))
        p.drawEllipse(QRectF(w / 2 - radius, h * .44 - radius, radius * 2, radius * 2))
        p.setBrush(QColor("#dcefff"))
        p.drawEllipse(QRectF(w * .16, h - 37, w * .68, 24))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(QColor("#bfdcf8"), 1.2))
        p.drawEllipse(QRectF(w * .06, h - 44, w * .88, 38))
        p.drawEllipse(QRectF(w * .26, h - 32, w * .48, 14))


class ControlPanel(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("喝大水 · 邵艾伦风格桌宠")
        self.setWindowIcon(app_icon())
        self.setMinimumSize(900, 640)
        area = self.screen().availableGeometry()
        self.resize(min(1110, area.width() - 36), min(790, area.height() - 48))
        self.setStyleSheet(STYLE)
        root = QWidget()
        root.setObjectName("content")
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        header = QFrame()
        header.setObjectName("header")
        top = QHBoxLayout(header)
        top.setContentsMargins(30, 0, 30, 0)
        brand = label("喝大水", "brand")
        brand.setToolTip("邵艾伦风格的桌面喝水伙伴")
        top.addWidget(brand)
        top.addSpacing(48)
        self.nav = []
        self.stack = QStackedWidget()
        for i, title in enumerate(["今日", "提醒与外观", "台词"]):
            item = button(title, lambda checked=False, index=i: self.navigate(index), "nav")
            item.setCheckable(True)
            self.nav.append(item)
            top.addWidget(item)
        top.addStretch()
        self.app_status = label("提醒已开启", "status")
        top.addWidget(self.app_status)
        outer.addWidget(header)
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(34, 26, 34, 14)
        body_layout.addWidget(self.stack)
        outer.addWidget(body, 1)
        self.build_dashboard()
        self.build_settings()
        self.build_quotes()
        self.navigate(0)
        self.statusBar().setSizeGripEnabled(False)
        self.statusBar().showMessage("非官方风格模拟    ·    记录保存在这台电脑    ·    v0.2.0")
        self.statusBar().setStyleSheet("QStatusBar { color: #8493a5; font-size: 11px; background: #ffffff; border-top: 1px solid #edf2f8; padding: 3px 20px; }")

    def navigate(self, index):
        self.stack.setCurrentIndex(index)
        for i, item in enumerate(self.nav):
            item.setChecked(i == index)

    def page(self, title, description):
        page = QWidget()
        page.setObjectName("page")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        layout.addWidget(label(title, "title"))
        layout.addWidget(label(description, "muted", True))
        return page, layout

    def build_dashboard(self):
        page = QWidget()
        page.setObjectName("page")
        layout = QHBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(34)
        left = QVBoxLayout()
        left.setSpacing(15)
        self.date_label = label("", "muted")
        left.addWidget(self.date_label)
        left.addWidget(label("先喝一口大水。\n再做下一件事。", "headline"))
        left.addWidget(label("大水放手边，照顾自己从这一口开始。", "muted"))
        actions = QHBoxLayout()
        actions.addWidget(button("我喝水了", self.controller.record_drink, "primary"))
        actions.addWidget(button("找到桌宠", self.controller.show_pet))
        actions.addStretch()
        left.addLayout(actions)
        left.addSpacing(4)
        left.addWidget(rule())
        row = QHBoxLayout()
        row.addWidget(label("今日喝水记录", "section"))
        row.addStretch()
        self.goal_label = label("", "muted")
        row.addWidget(self.goal_label)
        left.addLayout(row)
        numbers = QHBoxLayout()
        self.total_label = label("0 ml", "metric")
        numbers.addWidget(self.total_label)
        numbers.addStretch()
        self.count_label = label("还没有记录", "muted")
        numbers.addWidget(self.count_label, 0, Qt.AlignmentFlag.AlignBottom)
        left.addLayout(numbers)
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(8)
        left.addWidget(self.progress)
        left.addWidget(label("目标仅用于个人记录，按实际需要喝，不用凑数字。", "muted", True))
        schedule = QFrame()
        schedule.setObjectName("schedule")
        schedule_row = QHBoxLayout(schedule)
        schedule_row.setContentsMargins(17, 12, 17, 12)
        countdown = QVBoxLayout()
        countdown.setSpacing(0)
        countdown.addWidget(label("下一次喝水提醒", "muted"))
        self.countdown = label("45:00", "timer")
        countdown.addWidget(self.countdown)
        schedule_row.addLayout(countdown)
        schedule_row.addStretch()
        self.pause_button = button("暂停提醒", self.controller.toggle_pause)
        schedule_row.addWidget(self.pause_button)
        left.addWidget(schedule)
        history_heading = QHBoxLayout()
        history_heading.addWidget(label("最近记录", "section"))
        history_heading.addStretch()
        self.undo_button = button("撤销上一笔", self.undo, "subtle")
        history_heading.addWidget(self.undo_button)
        left.addLayout(history_heading)
        self.history_label = label("喝完后点“我喝水了”，这里会留下记录。", "muted", True)
        left.addWidget(self.history_label)
        left.addStretch()
        layout.addLayout(left, 3)
        right = QVBoxLayout()
        right.setSpacing(12)
        self.stage = WaterStage()
        self.preview = self.stage.avatar
        right.addWidget(self.stage, 1)
        quote = QFrame()
        quote.setObjectName("quoteBox")
        quote_layout = QVBoxLayout(quote)
        quote_layout.setContentsMargins(19, 17, 19, 14)
        self.quote_label = label("理论可以研究很久，瓶盖只要拧一下。先喝大水，对吧？", "quote", True)
        quote_layout.addWidget(self.quote_label)
        quote_layout.addWidget(button("换一句", self.controller.say_something, "subtle"), 0, Qt.AlignmentFlag.AlignLeft)
        right.addWidget(quote)
        right.addWidget(label("桌宠上的人物支持拖动与滚轮缩放。", "muted", True))
        layout.addLayout(right, 2)
        self.stack.addWidget(page)

    def scroll_body(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        body = QWidget()
        layout = QVBoxLayout(body)
        layout.setContentsMargins(0, 0, 16, 0)
        layout.setSpacing(15)
        scroll.setWidget(body)
        return scroll, layout

    def spin_row(self, layout, title, low, high, suffix):
        row = QHBoxLayout()
        row.addWidget(label(title))
        row.addStretch()
        obj = QSpinBox()
        obj.setRange(low, high)
        obj.setSuffix(suffix)
        obj.setFixedWidth(135)
        row.addWidget(obj)
        layout.addLayout(row)
        return obj

    def build_settings(self):
        page, layout = self.page("提醒与外观", "提醒跟着你的节奏，桌宠也调到喜欢的大小。")
        columns = QHBoxLayout()
        columns.setSpacing(32)
        scroll, form = self.scroll_body()
        form.addWidget(label("喝水提醒", "section"))
        self.interval = self.spin_row(form, "提醒间隔", 5, 180, " 分钟")
        self.cup = self.spin_row(form, "每次记录水量", 50, 1000, " ml")
        self.goal = self.spin_row(form, "个人记录目标", 200, 5000, " ml")
        self.notifications = QCheckBox("同时发送系统通知")
        form.addWidget(self.notifications)
        form.addWidget(rule())
        form.addWidget(label("桌边碎碎念", "section"))
        self.chatter = QCheckBox("让艾伦偶尔说句话")
        form.addWidget(self.chatter)
        self.chatter_interval = self.spin_row(form, "说话间隔", 5, 180, " 分钟")
        self.time_aware = QCheckBox("根据早晨、下午和晚上匹配台词")
        form.addWidget(self.time_aware)
        form.addWidget(rule())
        form.addWidget(label("免打扰", "section"))
        self.quiet = QCheckBox("这段时间暂停提醒和碎碎念")
        form.addWidget(self.quiet)
        quiet_row = QHBoxLayout()
        self.quiet_start, self.quiet_end = QTimeEdit(), QTimeEdit()
        self.quiet_start.setDisplayFormat("HH:mm")
        self.quiet_end.setDisplayFormat("HH:mm")
        quiet_row.addWidget(self.quiet_start)
        quiet_row.addWidget(label("至"))
        quiet_row.addWidget(self.quiet_end)
        quiet_row.addStretch()
        form.addLayout(quiet_row)
        form.addWidget(label("支持跨午夜；起止相同表示全天开放。", "muted"))
        form.addWidget(label("水量是个人记账设置；需限水时请按医嘱使用。", "muted", True))
        form.addStretch()
        columns.addWidget(scroll, 3)
        appearance, appearance_layout = card()
        appearance.setMaximumWidth(350)
        appearance_layout.addWidget(label("桌宠外观", "section"))
        self.appearance_stage = WaterStage()
        self.appearance_stage.setMinimumHeight(220)
        appearance_layout.addWidget(self.appearance_stage, 1)
        self.pet_size = self.spin_row(appearance_layout, "大小", 50, 200, " %")
        self.pet_size.setSingleStep(10)
        self.scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.scale_slider.setRange(50, 200)
        self.scale_slider.setSingleStep(10)
        self.scale_slider.setAccessibleName("桌宠大小")
        appearance_layout.addWidget(self.scale_slider)
        presets = QHBoxLayout()
        for percent in (75, 100, 150):
            presets.addWidget(button(f"{percent}%", lambda checked=False, p=percent: self.controller.set_pet_scale(p)))
        appearance_layout.addLayout(presets)
        appearance_layout.addWidget(label("立即生效并记住大小。也可以在桌宠上滚动滚轮，或右键选择比例。气泡文字保持清晰。", "muted", True))
        columns.addWidget(appearance, 2)
        layout.addLayout(columns, 1)
        footer = QHBoxLayout()
        self.saved_label = label("调整提醒后，点击保存。", "muted")
        footer.addWidget(self.saved_label)
        footer.addStretch()
        footer.addWidget(button("保存提醒设置", self.save_settings, "primary"))
        layout.addLayout(footer)
        self.stack.addWidget(page)
        self.load_settings()
        self.pet_size.valueChanged.connect(self.controller.set_pet_scale)
        self.scale_slider.valueChanged.connect(self.controller.set_pet_scale)

    def sync_scale(self, percent):
        for widget in (self.pet_size, self.scale_slider):
            widget.blockSignals(True)
            widget.setValue(percent)
            widget.blockSignals(False)
        # Appearance preview follows the requested proportion while keeping its stage fixed.
        self.appearance_stage.set_character_scale(percent)
        self.appearance_stage.avatar.setToolTip(f"当前桌宠大小 {percent}%")

    def load_settings(self):
        s = self.controller.store.settings
        for widget, value in [(self.interval, s.interval_minutes), (self.cup, s.cup_ml),
                              (self.goal, s.goal_ml), (self.chatter_interval, s.chatter_minutes)]:
            widget.setValue(value)
        self.sync_scale(s.pet_scale)
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
            self.saved_label.setText("提醒设置已保存，新的计时已开始。")
        self.controller.refresh()

    def build_quotes(self):
        page, layout = self.page("台词", "提醒有点风格，也给你留一点发挥的空间。")
        columns = QHBoxLayout()
        columns.setSpacing(30)
        editor = QVBoxLayout()
        editor.setSpacing(12)
        editor.addWidget(label("加几句你喜欢的话", "section"))
        editor.addWidget(label("每行一句，会加入喝水提醒和闲聊。最多 200 句，每句 180 字。", "muted", True))
        self.custom_lines = QPlainTextEdit()
        self.custom_lines.setPlaceholderText("大水已经就位，就差你拧开瓶盖了。")
        self.custom_lines.setPlainText("\n".join(self.controller.store.settings.custom_lines))
        self.custom_lines.setAccessibleName("自定义台词，每行一句")
        editor.addWidget(self.custom_lines, 1)
        footer = QHBoxLayout()
        self.custom_status = label("保存在这台电脑", "muted")
        footer.addWidget(self.custom_status)
        footer.addStretch()
        footer.addWidget(button("保存台词", self.save_quotes, "primary"))
        editor.addLayout(footer)
        columns.addLayout(editor, 3)
        right, audition_layout = card()
        right.setMaximumWidth(360)
        audition_layout.addWidget(label("听听他会说什么", "section"))
        self.category = QComboBox()
        for name, key in [("喝水提醒", "drink"), ("早晨", "morning"), ("下午", "afternoon"),
                          ("晚上", "evening"), ("夜间", "night"), ("随机闲聊", "idle"), ("喝完回应", "ack")]:
            self.category.addItem(name, key)
        audition_layout.addWidget(self.category)
        self.audition_text = label("", "quote", True)
        self.audition_text.setMinimumHeight(145)
        audition_layout.addWidget(self.audition_text)
        audition_layout.addWidget(button("换一句", self.change_audition))
        audition_layout.addWidget(button("让桌宠说这句", self.speak_audition, "primary"))
        audition_layout.addStretch()
        audition_layout.addWidget(rule())
        count = sum(map(len, self.controller.quotes.lines.values()))
        audition_layout.addWidget(label(f"内置 {count} 句原创台词", "section"))
        audition_layout.addWidget(label("口语化判断，偶尔夹一点英文，最后落在一个能做的小动作。", "muted", True))
        audition_layout.addWidget(label("基于截至 2026-10-15 的公开内容作风格模拟，非本人原话。", "muted", True))
        source = label('<a href="https://github.com/Roc-Dove/shao-alan-skill" style="color:#1768d5">参考 skill</a>　<a href="https://github.com/1saachen/shao-alan-water-pet/blob/main/docs/character.md" style="color:#1768d5">形象来源</a>')
        source.setOpenExternalLinks(True)
        audition_layout.addWidget(source)
        columns.addWidget(right, 2)
        layout.addLayout(columns, 1)
        self.category.currentIndexChanged.connect(self.change_audition)
        self.change_audition()
        self.stack.addWidget(page)

    def change_audition(self):
        self.audition_text.setText(self.controller.quotes.choose(self.category.currentData(), self.controller.store.settings.custom_lines))

    def speak_audition(self):
        text = self.audition_text.text()
        self.controller.pet.speak(text)
        self.quote_label.setText(text)

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
        weekday = "一二三四五六日"[now.weekday()]
        self.date_label.setText(f"{now.month} 月 {now.day} 日，星期{weekday}")
        self.total_label.setText(f"{total:,} ml")
        self.goal_label.setText(f"个人目标 {store.settings.goal_ml:,} ml")
        self.progress.setMaximum(store.settings.goal_ml)
        self.progress.setValue(min(total, store.settings.goal_ml))
        events = store.today_events(now)
        self.count_label.setText(f"今天记了 {len(events)} 次" if events else "还没有记录")
        self.undo_button.setEnabled(bool(events))
        history = "   /   ".join(f'{x["at"][11:16]}  +{x["ml"]} ml' for x in events[-3:])
        self.history_label.setText(history or "喝完后点“我喝水了”，这里会留下记录。")
        self.countdown.setText(countdown)
        self.countdown.setToolTip(status)
        self.pause_button.setText("恢复提醒" if store.settings.paused else "暂停提醒")
        self.app_status.setText("已暂停" if store.settings.paused else "免打扰中" if store.settings.is_quiet(now) else "提醒已开启")

    def closeEvent(self, event: QCloseEvent):
        if self.controller.tray.isVisible():
            event.ignore()
            self.hide()
        else:
            self.controller.quit()
