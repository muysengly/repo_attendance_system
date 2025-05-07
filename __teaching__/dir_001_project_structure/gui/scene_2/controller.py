import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.system("pyuic5 -x view.ui -o view.py")

from PyQt5.QtWidgets import QApplication, QMainWindow
from view import Ui_MainWindow


class Controller(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()

        self.pushButton.clicked.connect(self.f_click)

    def f_click(self):
        self.close()
        os.system("python ../scene_1/controller.py")


if __name__ == "__main__":
    app = QApplication([])
    win = Controller()
    win.show()
    app.exec_()
    app.quit()
