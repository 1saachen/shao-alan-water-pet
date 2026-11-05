from __future__ import annotations

import argparse
import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from PySide6.QtCore import QLockFile, QObject, QTimer
from PySide6.QtGui import QFont, QFontDatabase, QGuiApplication
from PySide6.QtWidgets import QApplication, QMenu, QMessageBox, QSystemTrayIcon

from .art import app_icon
from .core import QuoteBook, Scheduler, Store, data_directory, time_category
from .ui import ControlPanel, PetWindow


class Controller(QObject):
    def __init__(self, app, store=None):
        super().__init__()
        self.app = app
        self.store = store or Store()
        self.quotes = QuoteBook()
        self.scheduler = Scheduler(self.store.settings, datetime.now())
        self.tray = QSystemTrayIcon(app_icon(), self)
        self.tray.setToolTip("喝大水 · 邵艾伦风格桌宠")
        self.pet = PetWindow(self)
        self.panel = ControlPanel(self)
        self.menu = QMenu()
        self.menu.addAction("打开今日大水", self.open_panel)
        self.menu.addAction("找到桌宠", self.show_pet)
        self.menu.addAction("喝水提醒演示", self.preview_reminder)
        self.menu.addAction("换一句", self.say_something)
        self.menu.addSeparator()
        self.menu.addAction("我喝水了", self.record_drink)
        self.menu.addAction("10 分钟后提醒", self.snooze)
        self.pause_action = self.menu.addAction("暂停提醒", self.toggle_pause)
        self.menu.addSeparator()
        self.menu.addAction("隐藏桌宠（仍会提醒）", self.pet.hide)
        self.menu.addAction("退出", self.quit)
        self.tray.setContextMenu(self.menu)
        self.tray.activated.connect(self.tray_activated)
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray.show()
        self.place_pet()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(1000)
        self.refresh()
        self.app.aboutToQuit.connect(self.save_position)
        app.screenAdded.connect(self.screen_changed)
        app.screenRemoved.connect(self.screen_changed)

    def screen_changed(self, screen):
        QTimer.singleShot(100, self.clamp_pet)

    def persist(self):
        try:
            self.store.save()
            return True
        except OSError:
            logging.exception("Unable to persist local settings")
            QMessageBox.warning(self.panel, "保存未完成", "本地文件暂时无法写入。请检查可用空间和文件权限，当前会话仍可继续使用。")
            return False

    def save_position(self):
        self.store.settings.position = [self.pet.x(), self.pet.y()]
        self.persist()

    def place_pet(self):
        position = self.store.settings.position
        if position:
            self.pet.move(*position)
        else:
            area = QGuiApplication.primaryScreen().availableGeometry()
            self.pet.move(area.right() - self.pet.width() - 24, area.bottom() - self.pet.height() - 16)
        self.clamp_pet()

    def clamp_pet(self):
        screens = QGuiApplication.screens()
        screen = max(screens, key=lambda s: s.availableGeometry().intersected(self.pet.geometry()).width()
                     * s.availableGeometry().intersected(self.pet.geometry()).height())
        area = screen.availableGeometry()
        x = min(max(self.pet.x(), area.left()), max(area.left(), area.right() - self.pet.width() + 1))
        y = min(max(self.pet.y(), area.top()), max(area.top(), area.bottom() - self.pet.height() + 1))
        self.pet.move(x, y)

    def tray_activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            self.open_panel()

    def open_context_menu(self, position):
        self.pause_action.setText("恢复提醒" if self.store.settings.paused else "暂停提醒")
        self.menu.popup(position)

    def open_panel(self):
        self.panel.show()
        self.panel.raise_()
        self.panel.activateWindow()

    def show_pet(self):
        self.clamp_pet()
        self.pet.show()
        self.pet.raise_()

    def speak(self, category, reminder=False):
        text = self.quotes.choose(category, self.store.settings.custom_lines)
        self.pet.speak(text, reminder, "drink" if reminder else "happy" if category in ("ack", "goal") else "idle")
        self.panel.quote_label.setText(text)
        return text

    def say_something(self):
        category = time_category(datetime.now()) if self.store.settings.time_aware else "idle"
        self.speak(category)

    def preview_reminder(self):
        # Deliberate user action, independent of quiet hours; no drink is recorded.
        self.speak("drink", reminder=True)

    def record_drink(self):
        now = datetime.now()
        before = self.store.total(now)
        try:
            self.store.record(now)
        except OSError:
            logging.exception("Unable to save drink record")
            QMessageBox.warning(self.panel, "记录未保存", "本地记录未能写入磁盘，本次记录仍保留在当前会话。")
        self.scheduler.drank(now)
        reached = before < self.store.settings.goal_ml <= self.store.total(now)
        self.speak("goal" if reached else "ack")
        self.refresh()

    def snooze(self):
        self.scheduler.snooze(datetime.now())
        self.speak("snooze")
        self.refresh()

    def toggle_pause(self):
        self.store.settings.paused = not self.store.settings.paused
        self.scheduler.reset(datetime.now())
        self.persist()
        self.speak("pause" if self.store.settings.paused else "resume")
        self.refresh()

    def tick(self):
        event = self.scheduler.tick(datetime.now())
        if event == "drink":
            text = self.speak("drink", reminder=True)
            if self.store.settings.notifications and self.tray.isVisible():
                self.tray.showMessage("喝大水 · 到喝水时间了", text,
                                      QSystemTrayIcon.MessageIcon.Information, 10000)
        elif event == "chatter":
            self.say_something()
        self.refresh()

    def refresh(self):
        now = datetime.now()
        if self.store.settings.paused:
            short, status = "已暂停", "提醒已暂停，随时可以恢复"
        elif self.store.settings.is_quiet(now):
            short, status = "免打扰", f"免打扰至 {self.store.settings.quiet_end}"
        else:
            seconds = max(0, int((self.scheduler.next_drink - now).total_seconds()))
            short = f"{seconds // 60:02d}:{seconds % 60:02d}"
            status = f"下次喝水 {short}"
        self.panel.refresh(status, short)
        self.pet.status.setText(status)
        self.pet.drank_button.setText(f"喝了 {self.store.settings.cup_ml} ml")
        self.pause_action.setText("恢复提醒" if self.store.settings.paused else "暂停提醒")

    def quit(self):
        self.tray.hide()
        self.app.quit()


def main():
    parser = argparse.ArgumentParser(description="喝大水 · 邵艾伦风格桌宠")
    parser.add_argument("--pet-only", action="store_true", help="启动时只显示桌宠")
    parser.add_argument("--preview-dir", type=Path, help="渲染预览图并退出，不更改个人数据")
    args = parser.parse_args()
    if args.preview_dir:
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        os.environ["ALAN_WATER_DATA_DIR"] = str(args.preview_dir / "preview-data")
    app = QApplication(sys.argv[:1])
    # The offscreen Qt platform does not enumerate Windows fonts automatically.
    # Load fonts from the user's OS, without distributing Microsoft font files.
    if args.preview_dir and sys.platform == "win32":
        fonts = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
        for name in ("msyh.ttc", "msyhbd.ttc", "consola.ttf", "arial.ttf"):
            QFontDatabase.addApplicationFont(str(fonts / name))
    app.setApplicationName("AlanWaterPet")
    app.setOrganizationName("AlanWaterClub")
    app.setFont(QFont("Microsoft YaHei UI", 10))
    app.setWindowIcon(app_icon())
    app.setQuitOnLastWindowClosed(False)
    directory = data_directory()
    directory.mkdir(parents=True, exist_ok=True)
    lock = QLockFile(str(directory / "app.lock"))
    if not lock.tryLock(100):
        QMessageBox.information(None, "喝大水已经在运行", "到系统托盘找到绿色大水图标，点击即可打开面板。")
        return 0
    handler = RotatingFileHandler(directory / "app.log", maxBytes=256000, backupCount=2, encoding="utf-8")
    logging.basicConfig(level=logging.INFO, handlers=[handler], format="%(asctime)s %(levelname)s %(message)s")
    controller = Controller(app)
    if args.preview_dir:
        args.preview_dir.mkdir(parents=True, exist_ok=True)
        controller.panel.show()
        controller.preview_reminder()
        app.processEvents()
        controller.panel.grab().save(str(args.preview_dir / "dashboard.png"))
        controller.pet.grab().save(str(args.preview_dir / "pet.png"))
        for index, name in [(1, "settings"), (2, "quotes")]:
            controller.panel.navigate(index)
            app.processEvents()
            controller.panel.grab().save(str(args.preview_dir / f"{name}.png"))
        controller.quit()
        return 0
    controller.show_pet()
    if not args.pet_only or not controller.tray.isVisible():
        controller.open_panel()
    if controller.store.recovery_notice:
        QMessageBox.information(controller.panel, "本地记录恢复", controller.store.recovery_notice)
    return app.exec()
