# %%
import os

os.chdir(os.path.dirname(os.path.abspath(__file__))) if "__file__" in globals() else None
os.system("pyuic5 -x view.ui -o view.py")

# %%
from view import Ui_MainWindow

from PyQt5.QtCore import QStringListModel, QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication


# %%
class Window(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QIcon("../../asset/my_logo.ico"))
        self.setWindowTitle("Intelligent Systems")
        logo = QPixmap("../../asset/my_logo.png")
        self.label_logo.setPixmap(logo.scaled(self.label_logo.width(), self.label_logo.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.show()


# %%
app = QApplication([])
win = Window()


def f_login():
    print("Login")


win.pushButton_login.clicked.connect(f_login)


def f_register():
    print("Register")


win.pushButton_register.clicked.connect(f_register)


def f_forget_password():
    print("Forget Password")


win.pushButton_forget_password.clicked.connect(f_forget_password)


app.exec_()
app = None
