"""Local persistence, quote selection and scheduling, independent of Qt."""
from __future__ import annotations

import json
import os
import random
from dataclasses import asdict, dataclass, field, fields
from datetime import datetime, timedelta
from pathlib import Path


def data_directory() -> Path:
    override = os.environ.get("ALAN_WATER_DATA_DIR")
    if override:
        return Path(override)
    return Path(os.environ.get("APPDATA", Path.home() / ".config")) / "AlanWaterPet"


@dataclass
class Settings:
    interval_minutes: int = 45
    cup_ml: int = 200
    goal_ml: int = 1600
    chatter_enabled: bool = True
    chatter_minutes: int = 20
    time_aware: bool = True
    quiet_enabled: bool = True
    quiet_start: str = "23:00"
    quiet_end: str = "08:00"
    notifications: bool = True
    paused: bool = False
    pet_scale: int = 100
    position: list[int] | None = None
    custom_lines: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, values: dict) -> Settings:
        defaults = cls()
        clean = {}
        for item in fields(cls):
            value = values.get(item.name, getattr(defaults, item.name))
            default = getattr(defaults, item.name)
            if isinstance(default, bool):
                value = value if isinstance(value, bool) else default
            clean[item.name] = value
        for key, low, high in [("interval_minutes", 5, 180), ("cup_ml", 50, 1000),
                               ("goal_ml", 200, 5000), ("chatter_minutes", 5, 180),
                               ("pet_scale", 50, 200)]:
            try:
                clean[key] = max(low, min(high, int(clean[key])))
            except (TypeError, ValueError, OverflowError):
                clean[key] = getattr(defaults, key)
        for key in ("quiet_start", "quiet_end"):
            try:
                clean[key] = datetime.strptime(str(clean[key]), "%H:%M").strftime("%H:%M")
            except ValueError:
                clean[key] = getattr(defaults, key)
        pos = clean["position"]
        if not (isinstance(pos, list) and len(pos) == 2 and all(type(x) is int for x in pos)):
            clean["position"] = None
        lines = clean["custom_lines"]
        clean["custom_lines"] = [x[:180] for x in lines[:200] if isinstance(x, str) and x.strip()] if isinstance(lines, list) else []
        return cls(**clean)

    def is_quiet(self, now: datetime) -> bool:
        if not self.quiet_enabled or self.quiet_start == self.quiet_end:
            return False
        current = now.strftime("%H:%M")
        if self.quiet_start < self.quiet_end:
            return self.quiet_start <= current < self.quiet_end
        return current >= self.quiet_start or current < self.quiet_end


class Store:
    def __init__(self, directory: Path | None = None):
        self.directory = directory or data_directory()
        self.path = self.directory / "state.json"
        self.settings = Settings()
        self.events: list[dict] = []
        self.recovery_notice = ""
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                raise ValueError("Expected an object")
            settings = raw.get("settings", {})
            self.settings = Settings.from_dict(settings if isinstance(settings, dict) else {})
            events = raw.get("events", [])
            if isinstance(events, list):
                for event in events:
                    if not isinstance(event, dict) or type(event.get("ml")) is not int:
                        continue
                    try:
                        datetime.fromisoformat(event["at"])
                    except (KeyError, TypeError, ValueError):
                        continue
                    if 0 < event["ml"] <= 1000:
                        self.events.append(event)
        except FileNotFoundError:
            pass
        except (ValueError, OSError, TypeError):
            self.recovery_notice = "本地记录无法读取，已使用默认设置；原文件会保留为备份。"
            if self.path.exists():
                backup = self.path.with_suffix(f".corrupt-{datetime.now():%Y%m%d-%H%M%S-%f}.json")
                self.path.replace(backup)

    def save(self) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        # Keep a year of local history without tying reset behavior to app uptime.
        cutoff = (datetime.now() - timedelta(days=366)).isoformat()
        self.events = [x for x in self.events if x["at"] >= cutoff]
        temp = self.path.with_suffix(".tmp")
        temp.write_text(json.dumps({"settings": asdict(self.settings), "events": self.events},
                                   ensure_ascii=False, indent=2), encoding="utf-8")
        temp.replace(self.path)

    def record(self, now: datetime, ml: int | None = None) -> None:
        amount = self.settings.cup_ml if ml is None else ml
        if type(amount) is not int or not 0 < amount <= 1000:
            raise ValueError("Drink amount must be between 1 and 1000 ml")
        self.events.append({"at": now.isoformat(timespec="seconds"), "ml": amount})
        self.save()

    def today_events(self, now: datetime) -> list[dict]:
        return [x for x in self.events if x["at"][:10] == now.date().isoformat()]

    def total(self, now: datetime) -> int:
        return sum(x["ml"] for x in self.today_events(now))

    def undo(self, now: datetime) -> bool:
        for index in range(len(self.events) - 1, -1, -1):
            if self.events[index]["at"][:10] == now.date().isoformat():
                self.events.pop(index)
                self.save()
                return True
        return False


class Scheduler:
    def __init__(self, settings: Settings, now: datetime):
        self.settings = settings
        self.reset(now)

    def reset(self, now: datetime) -> None:
        self.next_drink = now + timedelta(minutes=self.settings.interval_minutes)
        self.next_chatter = now + timedelta(minutes=self.settings.chatter_minutes)
        self.last_tick = now
        self.was_quiet = self.settings.is_quiet(now)

    def snooze(self, now: datetime, minutes: int = 10) -> None:
        self.next_drink = now + timedelta(minutes=minutes)

    def drank(self, now: datetime) -> None:
        self.next_drink = now + timedelta(minutes=self.settings.interval_minutes)
        self.next_chatter = now + timedelta(minutes=self.settings.chatter_minutes)

    def tick(self, now: datetime) -> str | None:
        quiet = self.settings.is_quiet(now)
        clock_reversed = now < self.last_tick
        self.last_tick = now
        if clock_reversed:
            self.reset(now)
        if self.settings.paused or quiet:
            self.was_quiet = quiet
            return None
        if self.was_quiet:
            self.was_quiet = False
            self.next_chatter = now + timedelta(minutes=self.settings.chatter_minutes)
        # An overdue reminder fires once, including after sleep; missed ones never accumulate.
        if now >= self.next_drink:
            self.drank(now)
            return "drink"
        if self.settings.chatter_enabled and now >= self.next_chatter:
            self.next_chatter = now + timedelta(minutes=self.settings.chatter_minutes)
            return "chatter"
        return None


def time_category(now: datetime) -> str:
    if 6 <= now.hour < 12:
        return "morning"
    if 12 <= now.hour < 18:
        return "afternoon"
    if 18 <= now.hour < 23:
        return "evening"
    return "night"


class QuoteBook:
    def __init__(self, path: Path | None = None):
        path = path or Path(__file__).with_name("quotes.json")
        self.lines = json.loads(path.read_text(encoding="utf-8"))
        self.recent: list[str] = []

    def choose(self, category: str, custom: list[str] | None = None) -> str:
        pool = list(self.lines.get(category, self.lines["idle"]))
        if category in ("drink", "idle", "morning", "afternoon", "evening", "night"):
            pool.extend(custom or [])
        fresh = [x for x in pool if x not in self.recent]
        fallback = [x for x in pool if not self.recent or x != self.recent[-1]]
        result = random.choice(fresh or fallback or pool)
        self.recent = (self.recent + [result])[-6:]
        return result
