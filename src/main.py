import sys

from PySide6.QtWidgets import QApplication

from lucy import Lucy
from reminder_manager import ReminderManager


def main():
    app = QApplication(sys.argv)

    # Keep the background reminder cycle running even while Lucy is hidden.
    app.setQuitOnLastWindowClosed(False)

    lucy = Lucy()

    manager = ReminderManager(lucy)
    manager.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
