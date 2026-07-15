from pathlib import Path

from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QGraphicsOpacityEffect


class ThoughtBubble(QLabel):
    """
    Pure image - no text, per spec. Always uses the 'medium' asset since
    nothing ever drives it to a different size (unlike the speech
    bubble, which resizes for message length). A plain fade is used
    instead of any pop/scale effect - simplest option, and it matches
    the calm/unhurried feel better than a snappier motion would.
    """

    def __init__(self, assets_dir: Path, parent=None):
        super().__init__(parent)

        pixmap = QPixmap(str(assets_dir / "thought" / "medium.png"))
        if not pixmap.isNull():
            pixmap = pixmap.scaled(110, 85, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(pixmap)
        self.setAlignment(Qt.AlignCenter)

        self._effect = QGraphicsOpacityEffect(self)
        self._effect.setOpacity(0.0)
        self.setGraphicsEffect(self._effect)

        self._anim = None

    def fade_in(self, duration=280, on_finished=None):
        self._animate(0.0, 1.0, duration, on_finished)

    def fade_out(self, duration=280, on_finished=None):
        self._animate(1.0, 0.0, duration, on_finished)

    def _animate(self, start, end, duration, on_finished):
        anim = QPropertyAnimation(self._effect, b"opacity", self)
        anim.setDuration(duration)
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.setEasingCurve(QEasingCurve.InOutQuad)
        if on_finished:
            anim.finished.connect(on_finished)
        anim.start()
        self._anim = anim
