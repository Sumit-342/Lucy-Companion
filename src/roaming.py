import random

from PySide6.QtCore import QTimer

from state import LucyState


class RoamingManager:
    """
    Unchanged in spirit from the original - the state check here was
    already correct (only roam when IDLE), which is exactly what makes
    roaming automatically pause while talking or dragging: Lucy.say()
    and mousePressEvent() now reliably set TALKING/DRAGGING through the
    single _set_state() choke point, so this check is now trustworthy
    in a way it wasn't before (previously state could lag behind what
    was actually happening).
    """

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
            # Busy walking/talking/dragging - try again later instead
            # of forcing a walk on top of whatever's happening.
            self.schedule_next()
            return

        x = random.randint(650, 1250)
        self.lucy.walk_to(x, self.lucy.y())
        self.schedule_next()
