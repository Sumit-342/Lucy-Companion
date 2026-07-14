from PySide6.QtCore import QObject, QTimer, Signal, Qt
from PySide6.QtGui import QPixmap, QTransform


class WalkAnimator(QObject):
    """
    Owns the walk-cycle sprite frames and ONE timer. Knows nothing about
    widget position.

    WHY THIS EXISTS:
    The old code re-scaled (SmoothTransformation) AND re-flipped
    (QTransform().scale(-1,1)) the raw source pixmap on every single
    200ms animation tick, from scratch, on the UI thread - at the same
    time a *second*, faster (16ms) timer was moving the translucent
    frameless window. Two independent timers doing uncoordinated heavy
    work on the same widget is what produced the visible blur/tearing
    while walking.

    Fix: every frame, in both facing directions, is scaled and flipped
    exactly ONCE at construction time and cached. At tick time we just
    swap a pre-built QPixmap in - no scaling, no transform math, no
    per-tick cost at all. This is also what "separate animation from
    movement" means concretely: this class never touches self.move().
    """

    frame_changed = Signal(QPixmap)

    def __init__(self, frame_paths, size=(180, 340), interval_ms=120, parent=None):
        super().__init__(parent)

        self._frames_right = []
        self._frames_left = []

        for path in frame_paths:
            raw = QPixmap(path)
            if raw.isNull():
                print(f"⚠️ Walk frame not found: {path}")
                continue

            scaled = raw.scaled(
                size[0], size[1],
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            flipped = scaled.transformed(QTransform().scale(-1, 1))

            self._frames_right.append(scaled)
            self._frames_left.append(flipped)

        self._index = 0
        self._facing_right = True

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._interval = interval_ms

    def start(self, facing_right=True):
        if not self._frames_right:
            return
        self._facing_right = facing_right
        self._index = 0
        self._timer.start(self._interval)
        self._tick()

    def stop(self):
        self._timer.stop()

    def set_facing(self, facing_right):
        self._facing_right = facing_right

    def _tick(self):
        frames = self._frames_right if self._facing_right else self._frames_left
        if not frames:
            return
        self.frame_changed.emit(frames[self._index])
        self._index = (self._index + 1) % len(frames)
