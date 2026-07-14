from PySide6.QtCore import QObject, QTimer, Signal


class MovementController(QObject):
    """
    Owns position-stepping ONLY. Knows nothing about sprites or expressions.

    WHY THIS EXISTS:
    The old `update_position()` moved by a fixed +/-2px every tick and
    stopped only when current_x == target_x exactly. If the distance to
    the target wasn't evenly divisible by the step size, current_x would
    skip straight past target_x and never equal it -> Lucy would flip
    direction forever and never stop walking. That was the #1 reported
    bug ("Lucy sometimes never stops walking").

    Fix: every tick, the step is clamped to `min(speed, distance_remaining)`,
    so the very last step always lands exactly on the target. Arrival is
    guaranteed on the tick where it becomes reachable, not "whenever the
    arithmetic happens to line up".

    The timer also only runs while actively walking (started in walk_to,
    stopped on arrival) instead of running forever from construction -
    this is what "clean timer separation" means in practice: nothing
    ticks unless there's a real reason for it to.
    """

    step_moved = Signal(int, int, bool)  # new_x, y, facing_right
    arrived = Signal()

    def __init__(self, speed_px=2, interval_ms=16, parent=None):
        super().__init__(parent)

        self._speed = speed_px
        self._interval = interval_ms

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

        self._get_pos = None
        self._target_x = 0
        self._y = 0

    def walk_to(self, get_current_pos, target_x, y):
        """
        get_current_pos: a callable returning (x, y) - the controller
        doesn't own the widget, so it asks for live position each tick
        instead of tracking a possibly-stale copy of its own.
        """
        self._get_pos = get_current_pos
        self._target_x = target_x
        self._y = y
        self._timer.start(self._interval)

    def stop(self):
        """Called when dragging starts, or anything else must interrupt walking."""
        self._timer.stop()

    def is_active(self):
        return self._timer.isActive()

    def _tick(self):
        current_x, _ = self._get_pos()
        diff = self._target_x - current_x

        if diff == 0:
            self._timer.stop()
            self.arrived.emit()
            return

        step = min(self._speed, abs(diff))
        step = step if diff > 0 else -step
        new_x = current_x + step
        facing_right = diff > 0

        self.step_moved.emit(new_x, self._y, facing_right)

        if new_x == self._target_x:
            self._timer.stop()
            self.arrived.emit()
