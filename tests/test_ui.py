"""Run a real Qt event loop offscreen, with isolated local data."""
import os
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtWidgets import QApplication
from alan_water_pet.app import Controller
from alan_water_pet.core import Store


class UIFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setQuitOnLastWindowClosed(False)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.controller = Controller(self.app, Store(Path(self.temp.name)))
        self.controller.timer.stop()
        self.controller.store.settings.quiet_enabled = False
        self.controller.store.settings.notifications = False

    def tearDown(self):
        self.controller.save_position()
        self.controller.app.aboutToQuit.disconnect(self.controller.save_position)
        self.controller.app.screenAdded.disconnect(self.controller.screen_changed)
        self.controller.app.screenRemoved.disconnect(self.controller.screen_changed)
        self.controller.tray.hide()
        self.controller.panel.hide()
        self.controller.pet.hide()
        self.controller.panel.deleteLater()
        self.controller.pet.deleteLater()
        self.controller.deleteLater()
        self.app.processEvents()
        self.temp.cleanup()

    def test_record_snooze_pause_save_and_undo(self):
        c = self.controller
        c.preview_reminder()
        self.app.processEvents()
        self.assertTrue(c.pet.actions.isVisible())
        c.pet.drank_button.click()
        self.app.processEvents()
        self.assertEqual(c.store.total(datetime.now()), 200)
        self.assertIn("200", c.panel.total_label.text())
        self.assertFalse(c.pet.actions.isVisible())
        c.snooze()
        self.assertAlmostEqual((c.scheduler.next_drink - datetime.now()).total_seconds(), 600, delta=2)
        c.panel.pause_button.click()
        self.assertTrue(c.store.settings.paused)
        self.assertEqual(c.panel.countdown.text(), "已暂停")
        c.panel.pause_button.click()
        c.panel.interval.setValue(30)
        c.panel.cup.setValue(150)
        c.panel.save_settings()
        self.assertEqual(Store(c.store.directory).settings.interval_minutes, 30)
        self.assertIn("150", c.pet.drank_button.text())
        c.panel.undo_button.click()
        self.assertEqual(c.store.total(datetime.now()), 0)
        c.panel.custom_lines.setPlainText("自己的大水台词\n第二句")
        c.panel.save_quotes()
        self.assertEqual(Store(c.store.directory).settings.custom_lines, ["自己的大水台词", "第二句"])

    def test_due_tick_shows_action_bubble(self):
        c = self.controller
        c.scheduler.next_drink = datetime.now() - timedelta(seconds=1)
        c.tick()
        self.app.processEvents()
        self.assertTrue(c.pet.isVisible())
        self.assertTrue(c.pet.actions.isVisible())
        self.assertEqual(c.store.total(datetime.now()), 0)
        self.assertGreater(c.scheduler.next_drink, datetime.now())


if __name__ == "__main__":
    unittest.main()
