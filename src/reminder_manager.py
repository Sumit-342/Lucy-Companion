import random
from PySide6.QtCore import QTimer
from datetime import datetime

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


REMINDER_SCHEDULE = [

    {
        "time": "22:26",
        "type": "milk"
    },

    {
        "time": "00:00",
        "type": "sleep"
    }

]

class ReminderManager:

    def __init__(self, lucy):

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_reminders)

        self.lucy = lucy

    def milk_reminder(self):

        message = random.choice(MILK_REMINDERS)

        self.lucy.say(
            text=message,
            expression="happy",
            duration=4000
        )

    def sleep_reminder(self):

        message = random.choice(SLEEP_REMINDERS)

        self.lucy.say(
            text=message,
            expression="sleepy",
            duration=5000
        )
    
    def trigger_reminder(self, reminder_type):

        if reminder_type == "milk":
            self.milk_reminder()

        elif reminder_type == "sleep":
            self.sleep_reminder()
    
    def start(self):
        self.timer.start(60000)

    def check_reminders(self):

        current_time = datetime.now().strftime("%H:%M")

        for reminder in REMINDER_SCHEDULE:

            if reminder["time"] == current_time:

                self.trigger_reminder(
                    reminder["type"]
                )