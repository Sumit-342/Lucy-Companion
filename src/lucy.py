
# from pathlib import Path

# from PySide6.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve
# from PySide6.QtGui import QPixmap, QAction, QGuiApplication
# from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QMenu, QApplication

# from state import LucyState
# from message_card import MessageCard
# from walk_animator import WalkAnimator

# ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

# WALK_TRAVEL_PX = 150
# EDGE_MARGIN = 25
# WALK_DURATION_MS = 900
# THINKING_PAUSE_MS = 500
# CONFIRMATION_DURATION_MS = 1000
# AUTO_SNOOZE_MS = 60_000
# FADE_MS = 220
# CARD_GAP = 12  # px between the top of Lucy's window and the bottom of the card


# class Lucy(QWidget):
#     """
#     No bubble artwork anymore - just [sprite | flat message card]. The
#     'thinking' beat is now just an expression change plus a short pause,
#     with no separate widget, since that's all the spec actually needed
#     ("thinking expression before speaking") and it removes an entire
#     class of sizing/positioning risk.
#     """

#     EXPRESSION_SIZE = (150, 280)

#     def __init__(self):
#         super().__init__()

#         self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
#         self.setAttribute(Qt.WA_TranslucentBackground)

#         self.state = LucyState.HIDDEN
#         self.dragging = False
#         self.drag_position = QPoint()
#         self._user_moved = False

#         self.current_reminder_type = None
#         self.on_snooze_callback = None
#         self.on_complete_callback = None
#         self.on_hidden = None

#         self._reminder_expression = "happy"
#         self._resting_x = 0
#         self._resting_y = 0

#         self.main_layout = QHBoxLayout(self)
#         self.main_layout.setContentsMargins(15, 15, 15, 15)
#         self.main_layout.setSpacing(10)

#         self.image_label = QLabel(self)
#         self.image_label.setFixedSize(*self.EXPRESSION_SIZE)
#         self.main_layout.addWidget(self.image_label)

#         self.card = MessageCard()  # standalone floating window, not part of main_layout
#         self.card.hide()
#         self.card.action_clicked.connect(self._handle_action)

#         walk_frame_paths = [
#             str(ASSETS_DIR / "animations" / "walk" / f"walk_right_0{i}.png")
#             for i in range(1, 7)
#         ]
#         self.animator = WalkAnimator(walk_frame_paths, size=self.EXPRESSION_SIZE)
#         self.animator.frame_changed.connect(self.image_label.setPixmap)

#         self._walk_anim = None

#         self.auto_snooze_timer = QTimer(self)
#         self.auto_snooze_timer.setSingleShot(True)
#         self.auto_snooze_timer.timeout.connect(self._auto_snooze)

#         self.context_menu = QMenu()
#         exit_action = QAction("❌ Exit", self)
#         self.context_menu.addAction(exit_action)
#         exit_action.triggered.connect(QApplication.quit)

#         self.hide()

#     # ---------------- public entry point ----------------

#     def show_reminder(self, reminder_type, text, complete_text, snooze_text,
#                        expression, on_snooze, on_complete):
#         self.current_reminder_type = reminder_type
#         self.on_snooze_callback = on_snooze
#         self.on_complete_callback = on_complete
#         self._reminder_expression = expression
#         self._user_moved = False

#         self.card.setup_card(text, complete_text, snooze_text)
#         self.card.hide()  # card only becomes visible once she's finished walking in

#         self.show_expression("surprise")
#         self.adjustSize()  # sized off the sprite alone right now - card is hidden
#         self._compute_resting_position()

#         start_x = self._resting_x + WALK_TRAVEL_PX
#         self.move(start_x, self._resting_y)

#         self.state = LucyState.WALKING_IN
#         self.show()
#         self.raise_()
#         self.animator.start(facing="left")
#         self._animate_move(start_x, self._resting_x, self._resting_y, self._on_walked_in)

#     # ---------------- positioning ----------------

#     def _compute_resting_position(self):
#         screen = QGuiApplication.primaryScreen().availableGeometry()
#         self._resting_x = screen.width() - self.width() - EDGE_MARGIN
#         self._resting_y = screen.height() - self.height() - EDGE_MARGIN

#     def _reanchor(self):
#         if self._user_moved or self.state in (LucyState.WALKING_IN, LucyState.WALKING_OUT, LucyState.DRAGGING):
#             return
#         screen = QGuiApplication.primaryScreen().availableGeometry()
#         self._resting_x = screen.width() - self.width() - EDGE_MARGIN
#         self._resting_y = screen.height() - self.height() - EDGE_MARGIN
#         self.move(self._resting_x, self._resting_y)
#         self._position_card()

#     def _position_card(self):
#         """
#         Centers the card horizontally over Lucy's sprite, with a fixed
#         gap above her. Card size depends only on its own content
#         (set via setup_card/show_confirmation before this runs), so
#         this never widens or otherwise resizes Lucy's own window.
#         """
#         if not self.card.isVisible():
#             return
#         card_x = self.x() + (self.width() - self.card.width()) // 2
#         card_y = self.y() - self.card.height() - CARD_GAP
#         self.card.move(card_x, card_y)

#     # ---------------- movement ----------------

#     def _animate_move(self, start_x, end_x, y, on_finished):
#         self.move(start_x, y)
#         anim = QPropertyAnimation(self, b"pos", self)
#         anim.setDuration(WALK_DURATION_MS)
#         anim.setStartValue(QPoint(start_x, y))
#         anim.setEndValue(QPoint(end_x, y))
#         anim.setEasingCurve(QEasingCurve.InOutSine)
#         anim.finished.connect(on_finished)
#         anim.start()
#         self._walk_anim = anim

#     # ---------------- phase transitions ----------------

#     def _on_walked_in(self):
#         self.animator.stop()
#         self.state = LucyState.THINKING
#         self.show_expression("thinking")
#         QTimer.singleShot(THINKING_PAUSE_MS, self._show_speech)

#     def _show_speech(self):
#         self.state = LucyState.ACTIVE_REMINDER
#         self.show_expression(self._reminder_expression)
#         self.card.show()  # must be visible before _position_card() can size against it
#         self._position_card()
#         self.card.raise_()
#         self.card.fade_in(FADE_MS)
#         self.auto_snooze_timer.start(AUTO_SNOOZE_MS)

#     def _handle_action(self, action_type):
#         self.auto_snooze_timer.stop()
#         if action_type == "complete":
#             self._complete()
#         elif action_type == "snooze":
#             self._snooze(auto=False)

#     def _auto_snooze(self):
#         self._snooze(auto=True)

#     def _complete(self):
#         if self.on_complete_callback:
#             self.on_complete_callback(self.current_reminder_type)

#         confirmation = "Awesome bro 💙" if self.current_reminder_type == "milk" else "Good night bro 🌙"
#         self.state = LucyState.CONFIRMING
#         self.show_expression("happy")
#         self.card.show_confirmation(confirmation)  # resizes the card internally
#         self._position_card()  # re-center now that the card's size has changed
#         QTimer.singleShot(CONFIRMATION_DURATION_MS, self._walk_away)

#     def _snooze(self, auto):
#         if self.on_snooze_callback:
#             minutes = 10 if self.current_reminder_type == "milk" else 15
#             self.on_snooze_callback(self.current_reminder_type, minutes, auto)
#         self._walk_away()

#     def _walk_away(self):
#         self.card.hide()
#         self.state = LucyState.WALKING_OUT
#         self.animator.start(facing="right")
#         start_x = self.x()
#         end_x = start_x + WALK_TRAVEL_PX
#         self._animate_move(start_x, end_x, self.y(), self._finish_hide)

#     def _finish_hide(self):
#         self.animator.stop()
#         self.hide()
#         self.state = LucyState.HIDDEN
#         self.current_reminder_type = None
#         if self.on_hidden:
#             self.on_hidden()

#     # ---------------- expressions ----------------

#     def show_expression(self, expression):
#         pixmap = QPixmap(str(ASSETS_DIR / "expressions" / f"{expression}.png"))
#         if pixmap.isNull():
#             print(f"❌ Expression '{expression}' not found!")
#             return
#         scaled = pixmap.scaled(*self.EXPRESSION_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)
#         self.image_label.setPixmap(scaled)

#     # ---------------- interactions ----------------

#     def contextMenuEvent(self, event):
#         self.context_menu.exec(event.globalPos())

#     def mousePressEvent(self, event):
#         if event.button() == Qt.LeftButton and self.state == LucyState.ACTIVE_REMINDER:
#             self.dragging = True
#             self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
#             self.state = LucyState.DRAGGING

#     def mouseMoveEvent(self, event):
#         if self.dragging:
#             self.move(event.globalPosition().toPoint() - self.drag_position)
#             self._position_card()

#     def mouseReleaseEvent(self, event):
#         if self.dragging:
#             self.dragging = False
#             self._user_moved = True
#             self.state = LucyState.ACTIVE_REMINDER









from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPixmap, QAction, QGuiApplication
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QMenu, QApplication

from state import LucyState
from message_card import MessageCard
from walk_animator import WalkAnimator

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

WALK_TRAVEL_PX = 150
EDGE_MARGIN = 25
WALK_DURATION_MS = 900
THINKING_PAUSE_MS = 500
CONFIRMATION_DURATION_MS = 1000
AUTO_SNOOZE_MS = 60_000
FADE_MS = 220
CARD_GAP = 12  # px between the top of Lucy's window and the bottom of the card


class Lucy(QWidget):
    """
    No bubble artwork anymore - just [sprite | flat message card]. The
    'thinking' beat is now just an expression change plus a short pause,
    with no separate widget, since that's all the spec actually needed
    ("thinking expression before speaking") and it removes an entire
    class of sizing/positioning risk.
    """

    EXPRESSION_SIZE = (150, 280)

    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.state = LucyState.HIDDEN
        self.dragging = False
        self.drag_position = QPoint()
        self._user_moved = False

        self.current_reminder_type = None
        self.on_snooze_callback = None
        self.on_complete_callback = None
        self.on_hidden = None

        self._reminder_expression = "happy"
        self._resting_x = 0
        self._resting_y = 0

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(10)

        self.image_label = QLabel(self)
        self.image_label.setFixedSize(*self.EXPRESSION_SIZE)
        self.main_layout.addWidget(self.image_label)

        self.card = MessageCard()  # standalone floating window, not part of main_layout
        self.card.hide()
        self.card.action_clicked.connect(self._handle_action)

        walk_frame_paths = [
            str(ASSETS_DIR / "animations" / "walk" / f"walk_right_0{i}.png")
            for i in range(1, 7)
        ]
        self.animator = WalkAnimator(walk_frame_paths, size=self.EXPRESSION_SIZE)
        self.animator.frame_changed.connect(self.image_label.setPixmap)

        self._walk_anim = None

        self.auto_snooze_timer = QTimer(self)
        self.auto_snooze_timer.setSingleShot(True)
        self.auto_snooze_timer.timeout.connect(self._auto_snooze)

        self.context_menu = QMenu()
        exit_action = QAction("❌ Exit", self)
        self.context_menu.addAction(exit_action)
        exit_action.triggered.connect(QApplication.quit)

        self.hide()

    # ---------------- public entry point ----------------

    def show_reminder(self, reminder_type, text, complete_text, snooze_text,
                       expression, on_snooze, on_complete):
        self.current_reminder_type = reminder_type
        self.on_snooze_callback = on_snooze
        self.on_complete_callback = on_complete
        self._reminder_expression = expression
        self._user_moved = False

        self.card.setup_card(text, complete_text, snooze_text)
        self.card.hide()  # card only becomes visible once she's finished walking in

        self.show_expression("surprise")
        self.adjustSize()  # sized off the sprite alone right now - card is hidden
        self._compute_resting_position()

        start_x = self._resting_x + WALK_TRAVEL_PX
        self.move(start_x, self._resting_y)

        self.state = LucyState.WALKING_IN
        self.show()
        self.raise_()
        self.animator.start(facing="left")
        self._animate_move(start_x, self._resting_x, self._resting_y, self._on_walked_in)

    # ---------------- positioning ----------------

    def _compute_resting_position(self):
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self._resting_x = screen.width() - self.width() - EDGE_MARGIN
        self._resting_y = screen.height() - self.height() - EDGE_MARGIN

    def _reanchor(self):
        if self._user_moved or self.state in (LucyState.WALKING_IN, LucyState.WALKING_OUT, LucyState.DRAGGING):
            return
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self._resting_x = screen.width() - self.width() - EDGE_MARGIN
        self._resting_y = screen.height() - self.height() - EDGE_MARGIN
        self.move(self._resting_x, self._resting_y)
        self._position_card()

    def _position_card(self):
        """
        Centers the card horizontally over Lucy's sprite, with a fixed
        gap above her. If the card is wider than Lucy's sprite (common,
        since message length varies), centering alone could push it
        past the screen edge when she's resting near a corner - so the
        x position is clamped to stay fully on-screen afterward.
        """
        if not self.card.isVisible():
            return
        screen = QGuiApplication.primaryScreen().availableGeometry()

        card_x = self.x() + (self.width() - self.card.width()) // 2
        max_x = screen.width() - self.card.width() - EDGE_MARGIN
        card_x = max(EDGE_MARGIN, min(card_x, max_x))

        card_y = self.y() - self.card.height() - CARD_GAP
        self.card.move(card_x, card_y)

    # ---------------- movement ----------------

    def _animate_move(self, start_x, end_x, y, on_finished):
        self.move(start_x, y)
        anim = QPropertyAnimation(self, b"pos", self)
        anim.setDuration(WALK_DURATION_MS)
        anim.setStartValue(QPoint(start_x, y))
        anim.setEndValue(QPoint(end_x, y))
        anim.setEasingCurve(QEasingCurve.InOutSine)
        anim.finished.connect(on_finished)
        anim.start()
        self._walk_anim = anim

    # ---------------- phase transitions ----------------

    def _on_walked_in(self):
        self.animator.stop()
        self.state = LucyState.THINKING
        self.show_expression("thinking")
        QTimer.singleShot(THINKING_PAUSE_MS, self._show_speech)

    def _show_speech(self):
        self.state = LucyState.ACTIVE_REMINDER
        self.show_expression(self._reminder_expression)
        self.card.show()  # must be visible before _position_card() can size against it
        self._position_card()
        self.card.raise_()
        self.card.fade_in(FADE_MS)
        self.auto_snooze_timer.start(AUTO_SNOOZE_MS)

    def _handle_action(self, action_type):
        self.auto_snooze_timer.stop()
        if action_type == "complete":
            self._complete()
        elif action_type == "snooze":
            self._snooze(auto=False)

    def _auto_snooze(self):
        self._snooze(auto=True)

    def _complete(self):
        if self.on_complete_callback:
            self.on_complete_callback(self.current_reminder_type)

        confirmation = "Awesome bro 💙" if self.current_reminder_type == "milk" else "Good night bro 🌙"
        self.state = LucyState.CONFIRMING
        self.show_expression("happy")
        self.card.show_confirmation(confirmation)  # resizes the card internally
        self._position_card()  # re-center now that the card's size has changed
        QTimer.singleShot(CONFIRMATION_DURATION_MS, self._walk_away)

    def _snooze(self, auto):
        if self.on_snooze_callback:
            minutes = 10 if self.current_reminder_type == "milk" else 15
            self.on_snooze_callback(self.current_reminder_type, minutes, auto)
        self._walk_away()

    def _walk_away(self):
        self.card.hide()
        self.state = LucyState.WALKING_OUT
        self.animator.start(facing="right")
        start_x = self.x()
        end_x = start_x + WALK_TRAVEL_PX
        self._animate_move(start_x, end_x, self.y(), self._finish_hide)

    def _finish_hide(self):
        self.animator.stop()
        self.hide()
        self.state = LucyState.HIDDEN
        self.current_reminder_type = None
        if self.on_hidden:
            self.on_hidden()

    # ---------------- expressions ----------------

    def show_expression(self, expression):
        pixmap = QPixmap(str(ASSETS_DIR / "expressions" / f"{expression}.png"))
        if pixmap.isNull():
            print(f"❌ Expression '{expression}' not found!")
            return
        scaled = pixmap.scaled(*self.EXPRESSION_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled)

    # ---------------- interactions ----------------

    def contextMenuEvent(self, event):
        self.context_menu.exec(event.globalPos())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.state == LucyState.ACTIVE_REMINDER:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.state = LucyState.DRAGGING

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            self._position_card()

    def mouseReleaseEvent(self, event):
        if self.dragging:
            self.dragging = False
            self._user_moved = True
            self.state = LucyState.ACTIVE_REMINDER