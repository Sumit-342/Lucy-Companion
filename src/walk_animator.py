from PySide6.QtCore import QObject, QTimer, Signal, Qt
from PySide6.QtGui import QPixmap, QTransform


class WalkAnimator(QObject):
    """
    Only right-facing walk frames exist as assets. We mirror them once,
    at construction, into a left-facing set - so both "walking in"
    (right-to-left, into the corner) and "walking away" (left-to-right,
    turning around) can reuse the exact same six frames without ever
    flipping mid-animation.
    """

    frame_changed = Signal(QPixmap)

    def __init__(self, frame_paths, size=(150, 280), interval_ms=140, parent=None):
        super().__init__(parent)

        self._frames_right = []
        self._frames_left = []
        self._index = 0
        self._facing = "left"

        for path in frame_paths:
            raw = QPixmap(path)
            if raw.isNull():
                print(f"⚠️ Walk frame not found: {path}")
                continue
            scaled = raw.scaled(size[0], size[1], Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self._frames_right.append(scaled)
            self._frames_left.append(scaled.transformed(QTransform().scale(-1, 1)))

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._interval = interval_ms

    def start(self, facing="left"):
        frames = self._frames_left if facing == "left" else self._frames_right
        if not frames:
            return
        self._facing = facing
        self._index = 0
        self._timer.start(self._interval)
        self._tick()

    def stop(self):
        self._timer.stop()

    def _tick(self):
        frames = self._frames_left if self._facing == "left" else self._frames_right
        if not frames:
            return
        self.frame_changed.emit(frames[self._index])
        self._index = (self._index + 1) % len(frames)
