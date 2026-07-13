import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QGuiApplication

from lucy import Lucy

app = QApplication(sys.argv)

lucy = Lucy()

screen = QGuiApplication.primaryScreen().availableGeometry()

x = screen.width() - lucy.width() - 20
y = screen.height() - lucy.height() - 20

lucy.move(x, y)

lucy.show()

lucy.say("Good Morning Broo ! 😁")

sys.exit(app.exec())