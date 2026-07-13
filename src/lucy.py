from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QFrame, QLabel , QWidget , QVBoxLayout
from PySide6.QtCore import Qt
from message_card import MessageCard
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu
from PySide6.QtWidgets import QApplication


class Lucy(QWidget):

    def __init__(self):
        super().__init__()
        
        self.image_label = QLabel(self)

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

    def change_expression_after(self, expression , delay):

        QTimer.singleShot(
            delay,
            lambda : self.show_expression(expression)
        )


    def say(self, text,expression = None , duration = 3000):

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

    def contextMenuEvent(self, event):

        self.context_menu.exec(event.globalPos())