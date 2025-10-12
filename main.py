import sys
from PyQt5.QtWidgets import QApplication
from models.library_controller import LibraryController
from views.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = LibraryController()
    w = MainWindow(controller)
    w.show()
    sys.exit(app.exec_())
