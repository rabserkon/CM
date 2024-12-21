from data.database import init_db
from gui.material_page import MaterialWindow
from PyQt5.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    window = MaterialWindow()
    window.show()
    sys.exit(app.exec_())
