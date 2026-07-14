import random
from PySide6.QtCore import QTimer
from state import LucyState


class RoamingManager:

    def __init__(self, lucy):

        self.lucy = lucy

        self.timer = QTimer()

        self.timer.timeout.connect(self.roam)

    def start(self):

        self.schedule_next()

    def schedule_next(self):

        delay = random.randint(10000, 20000)

        self.timer.start(delay)

    def roam(self):

        self.timer.stop()

        if self.lucy.state != LucyState.IDLE:

            self.schedule_next()
            return

        x = random.randint(650,1250)

        self.lucy.walk_to(x, self.lucy.y())

        self.schedule_next()