import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QGuiApplication

from lucy import Lucy
from reminder_manager import ReminderManager
from roaming import RoamingManager

app = QApplication(sys.argv)

lucy = Lucy()

roaming = RoamingManager(lucy)
roaming.start()

screen = QGuiApplication.primaryScreen().availableGeometry()

x = screen.width() - lucy.width() - 20
y = screen.height() - lucy.height() - 20

lucy.move(x, y)

lucy.show()


manager = ReminderManager(lucy)
manager.start()

sys.exit(app.exec())