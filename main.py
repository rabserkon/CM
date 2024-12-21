from data.database import init_db
from gui.app import MainWindow
from PyQt5.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
