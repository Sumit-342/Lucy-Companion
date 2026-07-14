from PySide6.QtWidgets import QFrame, QLabel , QWidget , QVBoxLayout
from PySide6.QtCore import Qt


class MessageCard(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.WindowStaysOnTopHint
        )

        self.setAttribute(Qt.WA_TranslucentBackground)

        self.frame = QFrame(self)

        self.frame.setObjectName("messageCard")

        self.frame.setStyleSheet("""
            #messageCard{
                background:white;
                border-radius:15px;
                border:2px solid #D9D9D9;
            }
        """)

        self.label = QLabel()

        self.label.setAlignment(Qt.AlignCenter)

        self.label.setWordWrap(True)

        self.label.setStyleSheet("""
            color:black;
            font-size:14px;
            padding:12px;
        """)

        layout = QVBoxLayout(self.frame)

        layout.setContentsMargins(12, 12, 12, 12)

        layout.addWidget(self.label)

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(self.frame)
    
    def set_message(self, text):

        self.label.setText(text)

        self.adjustSize()

    def show_message(self, text):
        self.set_message(text)

        self.show()

    def say(self, text):

        self.label.setText(text)

        self.adjustSize()

        self.show()