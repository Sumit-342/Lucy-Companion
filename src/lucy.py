from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QAction
from PySide6.QtWidgets import QLabel, QWidget, QMenu, QApplication

from message_card import MessageCard
from state import LucyState
from walk_animator import WalkAnimator
from movement_controller import MovementController

# Resolved relative to THIS file, not the process's working directory -
# so assets load correctly no matter how/where the app is launched from.
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


class Lucy(QWidget):
    """
    Orchestrator only. Lucy no longer contains any scaling/transform math
    or per-tick movement arithmetic - that lives in WalkAnimator and
    MovementController respectively. Lucy's job is: wire their signals
    together, and be the single place state actually changes.
    """

    EXPRESSION_SIZE = (180, 340)

    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.state = LucyState.IDLE

        self.dragging = False
        self.drag_position = None

        self.image_label = QLabel(self)

        walk_frame_paths = [
            str(ASSETS_DIR / "animations" / "walk" / f"walk_0{i}.png")
            for i in range(1, 7)
        ]
        self.animator = WalkAnimator(walk_frame_paths, size=self.EXPRESSION_SIZE)
        self.animator.frame_changed.connect(self.image_label.setPixmap)

        self.movement = MovementController()
        self.movement.step_moved.connect(self._on_step_moved)
        self.movement.arrived.connect(self._on_arrived)

        self.card = MessageCard()
        self.card.hide()

        self.context_menu = QMenu()
        exit_action = QAction("❌ Exit", self)
        self.context_menu.addAction(exit_action)
        exit_action.triggered.connect(QApplication.quit)

        self.show_expression("sleepy")

    # ---------------- state ----------------

    def _set_state(self, new_state):
        """
        The ONLY place self.state is assigned. Every transition below
        goes through here so state always matches what's actually
        running (no more walking-while-dragging style desyncs).
        """
        self.state = new_state

    # ---------------- expressions ----------------

    def show_expression(self, expression):
        pixmap = QPixmap(str(ASSETS_DIR / "expressions" / f"{expression}.png"))

        if pixmap.isNull():
            print(f"❌ Expression '{expression}' not found!")
            return

        pixmap = pixmap.scaled(
            *self.EXPRESSION_SIZE,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.image_label.setPixmap(pixmap)
        self.image_label.adjustSize()
        self.resize(self.image_label.size())

    def change_expression_after(self, expression, delay):
        QTimer.singleShot(delay, lambda: self.show_expression(expression))

    # ---------------- walking ----------------

    def walk_to(self, x, y):
        if self.state in (LucyState.DRAGGING, LucyState.TALKING):
            # Don't hijack an active drag or an active speech bubble.
            # (Roaming already checks state == IDLE before calling this,
            # this is just a hard guarantee at the source.)
            return

        self._set_state(LucyState.WALKING)
        self.animator.start(facing_right=x > self.x())
        self.movement.walk_to(lambda: (self.x(), self.y()), x, y)

    def _on_step_moved(self, x, y, facing_right):
        self.animator.set_facing(facing_right)
        self.move(x, y)

    def _on_arrived(self):
        self.animator.stop()
        self._set_state(LucyState.IDLE)
        self.show_expression("thinking")

    # ---------------- speech ----------------

    def say(self, text, expression=None, duration=3000):
        self._set_state(LucyState.TALKING)

        # Interrupting a walk to talk should actually stop the walk,
        # not run underneath the speech bubble.
        self.movement.stop()
        self.animator.stop()

        if expression:
            self.show_expression(expression)

        # Resize the card to its final size BEFORE positioning/showing,
        # so it never flashes at a stale position.
        self.card.set_message(text)
        card_x = self.x() + (self.width() - self.card.width()) // 2
        card_y = self.y() - self.card.height() - 15
        self.card.move(card_x, card_y)
        self.card.show()

        QTimer.singleShot(duration, self._on_speech_finished)

    def _on_speech_finished(self):
        self.card.hide()
        self.show_expression("thinking")
        self._set_state(LucyState.IDLE)

    # ---------------- interaction ----------------

    def contextMenuEvent(self, event):
        self.context_menu.exec(event.globalPos())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
            # A drag always wins over an in-progress walk.
            self.movement.stop()
            self.animator.stop()
            self._set_state(LucyState.DRAGGING)

    def mouseMoveEvent(self, event):
        if self.dragging:
            new_pos = event.globalPosition().toPoint() - self.drag_position
            self.move(new_pos)
            self.card.move(
                new_pos.x() + (self.width() - self.card.width()) // 2,
                new_pos.y() - self.card.height() - 15
            )

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self._set_state(LucyState.IDLE)
        self.show_expression("thinking")
