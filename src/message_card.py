from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QGraphicsOpacityEffect
)


class MessageCard(QWidget):
    """
    A floating top-level window, NOT a widget embedded in Lucy's layout.
    This is what lets it size itself purely from its own content and
    appear above Lucy's head rather than beside her - a QHBoxLayout
    can only ever place a sibling widget to the side, so the card has
    to live in its own window that Lucy positions manually.
    """

    action_clicked = Signal(str)

    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.frame = QFrame(self)
        self.frame.setObjectName("messageCard")
        self.frame.setStyleSheet("""
            #messageCard {
                background: white;
                border-radius: 16px;
                border: 2px solid #D9D9D9;
            }
        """)

        self.label = QLabel(self.frame)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setMinimumWidth(220)
        self.label.setStyleSheet(
            "color:#2C3E50; font-size:15px; font-weight:600; background:transparent;"
        )

        self.btn_complete = QPushButton(self.frame)
        self.btn_snooze = QPushButton(self.frame)
        for btn, color, hover in (
            (self.btn_complete, "#2ECC71", "#27AE60"),
            (self.btn_snooze, "#95A5A6", "#7F8C8D"),
        ):
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    font-weight: bold;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-size: 13px;
                }}
                QPushButton:hover {{ background-color: {hover}; }}
            """)

        self.btn_complete.clicked.connect(lambda: self.action_clicked.emit("complete"))
        self.btn_snooze.clicked.connect(lambda: self.action_clicked.emit("snooze"))

        button_row = QHBoxLayout()
        button_row.setSpacing(10)
        button_row.addWidget(self.btn_complete)
        button_row.addWidget(self.btn_snooze)

        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(16, 14, 16, 14)
        frame_layout.setSpacing(12)
        frame_layout.addWidget(self.label)
        frame_layout.addLayout(button_row)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self.frame)

        self._effect = QGraphicsOpacityEffect(self)
        self._effect.setOpacity(0.0)
        self.setGraphicsEffect(self._effect)
        self._anim = None

    def setup_card(self, text, complete_text, snooze_text):
        self.label.setText(text)
        self.btn_complete.setText(complete_text)
        self.btn_snooze.setText(snooze_text)
        self.btn_complete.show()
        self.btn_snooze.show()
        self.adjustSize()

    def show_confirmation(self, text):
        self.label.setText(text)
        self.btn_complete.hide()
        self.btn_snooze.hide()
        self.adjustSize()

    def fade_in(self, duration=220):
        self._animate(0.0, 1.0, duration)

    def fade_out(self, duration=220, on_finished=None):
        self._animate(1.0, 0.0, duration, on_finished)

    def _animate(self, start, end, duration, on_finished=None):
        anim = QPropertyAnimation(self._effect, b"opacity", self)
        anim.setDuration(duration)
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.setEasingCurve(QEasingCurve.InOutQuad)
        if on_finished:
            anim.finished.connect(on_finished)
        anim.start()
        self._anim = anim