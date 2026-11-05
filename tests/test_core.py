import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from alan_water_pet.core import QuoteBook, Scheduler, Settings, Store, time_category


class SchedulerTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 5, 9, 0)
        self.settings = Settings(chatter_enabled=False)
        self.scheduler = Scheduler(self.settings, self.now)

    def test_due_reminder_and_no_duplicate(self):
        self.assertIsNone(self.scheduler.tick(self.now + timedelta(minutes=44)))
        due = self.now + timedelta(minutes=45)
        self.assertEqual(self.scheduler.tick(due), "drink")
        self.assertIsNone(self.scheduler.tick(due))

    def test_drinking_resets_deadline(self):
        self.scheduler.drank(self.now + timedelta(minutes=20))
        self.assertIsNone(self.scheduler.tick(self.now + timedelta(minutes=45)))
        self.assertEqual(self.scheduler.tick(self.now + timedelta(minutes=65)), "drink")

    def test_snooze_is_ten_minutes_from_now(self):
        self.scheduler.snooze(self.now)
        self.assertIsNone(self.scheduler.tick(self.now + timedelta(minutes=9)))
        self.assertEqual(self.scheduler.tick(self.now + timedelta(minutes=10)), "drink")

    def test_sleep_resume_fires_only_one_reminder(self):
        wake = self.now + timedelta(hours=8)
        self.assertEqual(self.scheduler.tick(wake), "drink")
        self.assertIsNone(self.scheduler.tick(wake + timedelta(seconds=1)))

    def test_quiet_hours_cross_midnight(self):
        for hour in [23, 0, 7]:
            self.assertTrue(self.settings.is_quiet(self.now.replace(hour=hour)))
        for hour in [8, 12, 22]:
            self.assertFalse(self.settings.is_quiet(self.now.replace(hour=hour)))

    def test_quiet_hours_same_day_and_equal(self):
        self.settings.quiet_start, self.settings.quiet_end = "12:00", "14:00"
        self.assertTrue(self.settings.is_quiet(self.now.replace(hour=13)))
        self.assertFalse(self.settings.is_quiet(self.now.replace(hour=14)))
        self.settings.quiet_end = "12:00"
        self.assertFalse(self.settings.is_quiet(self.now.replace(hour=12)))

    def test_quiet_suppresses_both_events_and_resumes_once(self):
        self.settings.chatter_enabled = True
        night = self.now.replace(hour=23)
        self.assertIsNone(self.scheduler.tick(night))
        self.assertIsNone(self.scheduler.tick(night + timedelta(hours=3)))
        morning = night + timedelta(hours=9)
        self.assertEqual(self.scheduler.tick(morning), "drink")
        self.assertIsNone(self.scheduler.tick(morning))

    def test_pause_suppresses_everything(self):
        self.settings.paused = True
        self.settings.chatter_enabled = True
        self.assertIsNone(self.scheduler.tick(self.now + timedelta(hours=1)))

    def test_clock_rollback_resets_deadlines(self):
        earlier = self.now - timedelta(hours=1)
        self.assertIsNone(self.scheduler.tick(earlier))
        self.assertEqual(self.scheduler.next_drink, earlier + timedelta(minutes=45))

    def test_chatter_has_independent_interval(self):
        self.settings.chatter_enabled = True
        self.assertEqual(self.scheduler.tick(self.now + timedelta(minutes=20)), "chatter")
        self.assertEqual(self.scheduler.next_drink, self.now + timedelta(minutes=45))


class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        self.store = Store(self.directory)
        self.now = datetime.now().replace(hour=23, minute=59, second=0, microsecond=0)

    def tearDown(self):
        self.temp.cleanup()

    def test_roundtrip_settings_drinks_and_undo(self):
        self.store.settings.interval_minutes = 30
        self.store.settings.custom_lines = ["大水就位"]
        self.store.record(self.now)
        self.store.record(self.now, 100)
        saved = Store(self.directory)
        self.assertEqual(saved.settings.interval_minutes, 30)
        self.assertEqual(saved.settings.custom_lines, ["大水就位"])
        self.assertEqual(saved.total(self.now), 300)
        self.assertTrue(saved.undo(self.now))
        self.assertEqual(Store(self.directory).total(self.now), 200)

    def test_daily_reset_works_without_restart_and_preserves_history(self):
        self.store.record(self.now)
        tomorrow = self.now + timedelta(minutes=2)
        self.assertEqual(self.store.total(tomorrow), 0)
        self.assertFalse(self.store.undo(tomorrow))
        self.store.record(tomorrow, 150)
        self.assertEqual(self.store.total(self.now), 200)
        self.assertEqual(self.store.total(tomorrow), 150)

    def test_corrupt_json_is_backed_up(self):
        self.store.path.write_text("broken", encoding="utf-8")
        recovered = Store(self.directory)
        self.assertTrue(recovered.recovery_notice)
        self.assertEqual(len(list(self.directory.glob("*.corrupt-*.json"))), 1)
        recovered.save()
        self.assertEqual(json.loads(recovered.path.read_text())["events"], [])

    def test_untrusted_malformed_settings_are_normalized(self):
        values = {"interval_minutes": -2, "cup_ml": "bad", "quiet_start": "25:00",
                  "custom_lines": [None, 3, "正常台词"], "position": ["x", 0],
                  "notifications": "false", "unknown": "ignored"}
        s = Settings.from_dict(values)
        self.assertEqual(s.interval_minutes, 5)
        self.assertEqual(s.cup_ml, 200)
        self.assertEqual(s.quiet_start, "23:00")
        self.assertEqual(s.custom_lines, ["正常台词"])
        self.assertIsNone(s.position)
        self.assertIs(s.notifications, True)

    def test_invalid_events_are_skipped(self):
        self.store.path.write_text(json.dumps({"events": [{"at": "invalid", "ml": 100},
                                    {"at": self.now.isoformat(), "ml": -1}, None]}))
        self.assertEqual(Store(self.directory).events, [])

    def test_invalid_amount_rejected(self):
        for amount in [-1, 0, 1001, True]:
            with self.assertRaises(ValueError):
                self.store.record(self.now, amount)

    def test_scale_defaults_and_bounds_roundtrip(self):
        self.assertEqual(Settings.from_dict({}).pet_scale, 100)
        self.assertEqual(Settings.from_dict({"pet_scale": "bad"}).pet_scale, 100)
        self.assertEqual(Settings.from_dict({"pet_scale": 10000}).pet_scale, 200)
        self.assertEqual(Settings.from_dict({"pet_scale": -1}).pet_scale, 50)
        self.store.settings.pet_scale = 75
        self.store.save()
        self.assertEqual(Store(self.directory).settings.pet_scale, 75)


class QuoteTests(unittest.TestCase):
    def test_time_buckets(self):
        expected = {0: "night", 6: "morning", 12: "afternoon", 18: "evening", 23: "night"}
        for hour, category in expected.items():
            self.assertEqual(time_category(datetime(2026, 11, 5, hour)), category)

    def test_no_recent_repeats_in_large_category(self):
        book = QuoteBook()
        recent = [book.choose("drink") for _ in range(7)]
        self.assertEqual(len(set(recent)), 7)

    def test_custom_lines_join_drink_pool(self):
        book = QuoteBook()
        book.lines["drink"] = ["自带"]
        book.recent = ["自带"]
        self.assertEqual(book.choose("drink", ["自定义"]), "自定义")

    def test_bank_lengths_fit_bubble(self):
        book = QuoteBook()
        self.assertGreaterEqual(sum(map(len, book.lines.values())), 65)
        self.assertTrue(all(0 < len(line) <= 75 for lines in book.lines.values() for line in lines))


if __name__ == "__main__":
    unittest.main()
