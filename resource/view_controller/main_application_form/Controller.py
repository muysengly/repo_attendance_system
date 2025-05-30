#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# TODO:
# -
# -
# -
# -
# -


# In[ ]:


import os


path_depth = "../../../"  # adjust the current working directory
if "__file__" not in globals():  # check if running in Jupyter Notebook
    os.system("jupyter nbconvert --to script Controller.ipynb --output Controller")  # convert notebook to script
    os.system("pyuic5 -x View.ui -o View.py")  # convert UI file to Python script

os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_SCALE_FACTOR"] = "1"


# In[ ]:


from View import Ui_MainWindow

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import pickle


# In[ ]:


import sys

sys.path.append(path_depth)
from resource.utility.Database import DataBase

db = DataBase(path_depth + "database.sqlite")


# In[ ]:


class Window(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QIcon(f"{path_depth}resource/asset/itc_logo.png"))
        self.setWindowTitle("Main Form")

        self.label_itc_logo.setPixmap(QPixmap(f"{path_depth}resource/asset/itc_logo.png").scaled(self.label_itc_logo.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.label_gtr_logo.setPixmap(QPixmap(f"{path_depth}resource/asset/gtr_logo.png").scaled(self.label_gtr_logo.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

        self.comboBox_group_name.clear()
        self.comboBox_group_name.addItems(db.read_table())

        self.show()


# In[ ]:


app = QApplication([])
win = Window()

win.label_version.setText("Version: 2.0.2")

win.pushButton_check_attendance.setIcon(QIcon(f"{path_depth}resource/asset/face-scanner.png"))
win.pushButton_manage.setIcon(QIcon(f"{path_depth}resource/asset/settings-gears.png"))
win.pushButton_check_update.setIcon(QIcon(f"{path_depth}resource/asset/refresh.png"))


def on_manage_button_clicked():
    win.hide()

    os.system("python " + path_depth + "resource/view_controller/select_manage_form/Controller.py")
    win.comboBox_group_name.clear()
    win.comboBox_group_name.addItems(db.read_table())

    win.show()


win.pushButton_manage.clicked.connect(on_manage_button_clicked)


def on_check_attendance_button_clicked():
    if len(db.read_table()) > 0:
        win.hide()

        group_name = win.comboBox_group_name.currentText()
        pickle.dump(group_name, open(path_depth + "resource/variable/_group_name.pkl", "wb"))
        os.system("python " + path_depth + "resource/view_controller/check_attendance_form/Controller.py")

        win.show()


win.pushButton_check_attendance.clicked.connect(on_check_attendance_button_clicked)


def on_click_update_button():
    QMessageBox.information(win, "Update", "This feature is not implemented yet. \nPlease check back later!.")


win.pushButton_check_update.clicked.connect(on_click_update_button)


app.exec_()
app = None


# In[ ]:




