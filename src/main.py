import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QGuiApplication

from lucy import Lucy
from reminder_manager import ReminderManager

app = QApplication(sys.argv)

lucy = Lucy()

screen = QGuiApplication.primaryScreen().availableGeometry()

x = screen.width() - lucy.width() - 20
y = screen.height() - lucy.height() - 20

lucy.move(x, y)

lucy.show()

# lucy.say(
#     text= "hello there dirnk water ",
#     expression="sleepy",
#     duration=5000
# )

manager = ReminderManager(lucy)
manager.start()

sys.exit(app.exec())