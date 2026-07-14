from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QFrame, QLabel , QWidget , QVBoxLayout
from PySide6.QtCore import Qt
from message_card import MessageCard
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPixmap , QTransform
from state import LucyState


class Lucy(QWidget):

    def __init__(self):

        self.dragging = False
        self.drag_postion = None
       

        super().__init__()

        
        self.image_label = QLabel(self)

        self.walk_frames = [

        QPixmap("../assets/animations/walk/walk_01.png"),
        QPixmap("../assets/animations/walk/walk_02.png"),
        QPixmap("../assets/animations/walk/walk_03.png"),
        QPixmap("../assets/animations/walk/walk_04.png"),
        QPixmap("../assets/animations/walk/walk_05.png"),
        QPixmap("../assets/animations/walk/walk_06.png")
        ]

        self.target_x = 0
        self.target_y = 0

        self.is_walking = False

        self.walk_timer = QTimer()
        self.move_timer = QTimer()


        self.walk_timer.timeout.connect(self.play_walk_animation)

        # self.walk_timer(120)

        self.move_timer.timeout.connect(
            self.update_position
        )
        
        self.move_timer.start(16)

        self.walk_index = 0

        self.facing_right = True

        self.card = QFrame(self)

        self.card.setStyleSheet("""
            background-color: white;
            border: 2px solid #D9D9D9;
            border-radius: 15px;
        """)

        self.card_label = QLabel(self.card)

        self.card_label.setAlignment(Qt.AlignCenter)

        self.card_label.setWordWrap(True)

        self.card_label.setStyleSheet("""
            color: black;
            font-size: 14px;
            padding: 12px;
        """)

        layout = QVBoxLayout(self.card)

        layout.setContentsMargins(12, 12, 12, 12)

        layout.addWidget(self.card_label)


        self.card.hide()

        self.setWindowFlags(
        Qt.FramelessWindowHint |
        Qt.Tool |
        Qt.WindowStaysOnTopHint
        )

        self.setAttribute(Qt.WA_TranslucentBackground)

        self.context_menu = QMenu()

        exit_action = QAction("❌ Exit", self)

        self.context_menu.addAction(exit_action)

        exit_action.triggered.connect(QApplication.quit)

        self.show_expression("sleepy")
        self.card = MessageCard()
        self.card.hide()
        self.change_expression_after(
            "surprise",
            3000
        )

        QTimer.singleShot(
            3000,
            lambda : self.walk_to(700,self.y())
        )

    def show_expression(self, expression):

        pixmap = QPixmap(f"../assets/expressions/{expression}.png")

        if pixmap.isNull():
            print(f"❌ Expression '{expression}' not found!")
            return


        pixmap = pixmap.scaled(
            180,
            340,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.image_label.setPixmap(pixmap)

        self.image_label.adjustSize()
        self.resize(self.image_label.size())


    def walk_to(self, x, y):

        self.target_x = x
        self.target_y = y

        self.state = LucyState.WALKING
        self.is_walking = True

        self.walk_timer.start(200)

    def update_position(self):

        if not self.is_walking:
            return

        current_x = self.x()

        if current_x < self.target_x:

            self.facing_right = True

            self.move(current_x + 2, self.y())

        elif current_x > self.target_x:

            self.facing_right = False

            self.move(current_x - 2, self.y())

        else:
            self.state = LucyState.IDLE
            self.is_walking = False
            self.walk_timer.stop()
            self.show_expression("thinking")

    def play_walk_animation(self):

        pixmap = self.walk_frames[self.walk_index]

        if not self.facing_right :
            pixmap = pixmap.transformed(
                QTransform().scale(-1,1)
            )

        pixmap = pixmap.scaled(
            180,
            340,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.image_label.setPixmap(pixmap)

        self.walk_index = (self.walk_index + 1) % len(self.walk_frames)

    def change_expression_after(self, expression , delay):

        QTimer.singleShot(
            delay,
            lambda : self.show_expression(expression)
        )


    def say(self, text,expression = None , duration = 3000):

        self.state = LucyState.TALKING

        if expression :
            self.show_expression(expression)

        self.card.say(text)

        card_x = self.x() + (self.width() - self.card.width()) // 2

        card_y = self.y() - self.card.height() - 15

        self.card.move(card_x, card_y)

        QTimer.singleShot(
            duration,
            self.card.hide
        )

        QTimer.singleShot(
            duration,
            lambda : self.show_expression("thinking")
        )

        QTimer.singleShot(
            duration,
            lambda: setattr(self,"state",LucyState.IDLE)
        )

    def contextMenuEvent(self, event):

        self.context_menu.exec(event.globalPos())


    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:
            self.dragging = True
            
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.state = LucyState.DRAGGING
            


        
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
        self.state = LucyState.IDLE