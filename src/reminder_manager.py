import json
import random
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QTimer

from state import LucyState

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

MILK_REMINDERS = [
    "🥛 Brooo! Time for your milk!",
    "🥛 Don't let today's milk mission fail 😤",
    "🥛 Future strong bro starts with today's milk!",
    "🥛 Milk time! Go before you forget again 😂",
    "🥛 Your body called... it wants milk.",
    "🥛 Quick reminder! Your glass of milk is waiting.",
    "🥛 Bro, your bones will thank you later. Go drink your milk!",
    "🥛 Pause for two minutes... it's milk o'clock.",
    "🥛 You've remembered coding. Now remember your milk too 😏",
    "🥛 Daily milk check! Have you had yours yet?",
    "🥛 A small glass today, a stronger you tomorrow.",
    "🥛 Lucy's mission: Make sure you don't skip your milk 🫡",
    "🥛 Your milk is feeling ignored... go rescue it 😂",
    "🥛 One glass. One minute. Let's do it, bro!",
    "🥛 Hydration is great... but don't forget your milk too!"
]

SLEEP_REMINDERS = [
    "😴 Bro... it's midnight. Time to get some sleep.",
    "🌙 You've worked enough today. Rest is important too.",
    "😪 Lucy officially recommends going to bed now.",
    "🌌 It's 12 AM... tomorrow's version of you will thank you for sleeping.",
    "😴 Bro, close the laptop and recharge yourself.",
    "🌙 Good work today. Now it's time to rest.",
    "💤 Even Lucy needs you to sleep on time 😄",
    "😪 The code can wait. Your sleep can't.",
    "🌙 Tomorrow has new goals. Get some good sleep tonight.",
    "😴 Late-night coding is cool... but health comes first.",
    "💤 Mission accomplished for today. Time to sleep, bro.",
    "🌙 You've earned your rest. See you tomorrow!",
    "😴 One last reminder... the bed is calling 😂",
    "🌌 Don't fight your sleep schedule. Go rest, bro.",
    "💙 Good night, bro. Lucy will be here tomorrow too."
]


class ReminderManager:

    def __init__(self, lucy):
        self.lucy = lucy
        self.lucy.on_hidden = self._on_lucy_hidden

        self.clock = QTimer()
        self.clock.timeout.connect(self.check_schedule)

        self.snooze_timers = {}
        # Tracks whether the LAST outcome for a type was an ignored
        # (auto) snooze, so the next trigger can show "concern" instead
        # of the normal happy/sleepy expression.
        self.ignored = {"milk": False, "sleep": False}
        # Single-slot pending queue - only one reminder may show at a
        # time; if a second type triggers while busy, it waits here.
        self._pending = None

        with open(DATA_DIR / "reminders.json", "r", encoding="utf-8") as file:
            self.reminder_schedule = json.load(file)

    def start(self):
        self.clock.start(60000)

    def check_schedule(self):
        current_time = datetime.now().strftime("%H:%M")
        for alert in self.reminder_schedule:
            if alert["time"] == current_time:
                self.dispatch(alert["type"])

    def dispatch(self, reminder_type):
        if self.lucy.state != LucyState.HIDDEN:
            # Busy with another reminder - hold this one. A repeat
            # dispatch of the same type just replaces the pending slot
            # rather than stacking duplicates.
            self._pending = reminder_type
            return
        self._trigger(reminder_type)

    def _trigger(self, reminder_type):
        expression_override = "concern" if self.ignored.get(reminder_type) else None

        if reminder_type == "milk":
            message = random.choice(MILK_REMINDERS)
            expression = expression_override or "happy"
            self.lucy.show_reminder(
                "milk", message, "🥛 I Drank It", "😴 Snooze",
                expression, self._on_snooze, self._on_complete
            )
        elif reminder_type == "sleep":
            message = random.choice(SLEEP_REMINDERS)
            expression = expression_override or "sleepy"
            self.lucy.show_reminder(
                "sleep", message, "😴 Going To Sleep", "😴 Snooze",
                expression, self._on_snooze, self._on_complete
            )

    def _on_lucy_hidden(self):
        if self._pending:
            pending_type = self._pending
            self._pending = None
            self._trigger(pending_type)

    def _on_complete(self, reminder_type):
        self.ignored[reminder_type] = False

    def _on_snooze(self, reminder_type, minutes, was_auto):
        self.ignored[reminder_type] = was_auto

        existing = self.snooze_timers.pop(reminder_type, None)
        if existing:
            existing.stop()
            existing.deleteLater()

        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: self._fire_snooze(reminder_type))
        timer.start(minutes * 60 * 1000)
        self.snooze_timers[reminder_type] = timer

    def _fire_snooze(self, reminder_type):
        # Pop the entry BEFORE re-dispatching. The previous version left
        # a stale, already-deleted QTimer sitting in the dict, which
        # crashed the next time that type tried to cancel/replace it.
        timer = self.snooze_timers.pop(reminder_type, None)
        if timer:
            timer.deleteLater()
        self.dispatch(reminder_type)
