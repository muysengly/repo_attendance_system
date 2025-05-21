#!/usr/bin/env python
# coding: utf-8

# In[1]:


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


# In[3]:


from View import Ui_MainWindow

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import glob

import pickle


# In[4]:


group_paths = glob.glob(os.path.join(path_depth + "resource/database/", "*.pkl"))
group_names = [name.split("\\")[-1][:-4] for name in group_paths]
group_names


# In[5]:


class Window(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QIcon(f"{path_depth}resource/asset/itc_logo.png"))
        self.setWindowTitle("Main Form")


        self.label_itc_logo.setPixmap(QPixmap(f"{path_depth}resource/asset/itc_logo.png").scaled(self.label_itc_logo.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.label_gtr_logo.setPixmap(QPixmap(f"{path_depth}resource/asset/gtr_logo.png").scaled(self.label_gtr_logo.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

        self.comboBox_group_name.addItems(group_names)

        self.show()


# In[6]:


app = QApplication([])
win = Window()




def on_manage_button_clicked():
    win.hide()
    os.system("python " + path_depth + "resource/view_controller/select_manage_form/Controller.py")
    win.show()


win.pushButton_manage.clicked.connect(on_manage_button_clicked)




def on_check_attendance_button_clicked():
    win.hide()
    group_name = win.comboBox_group_name.currentText()
    pickle.dump(group_name, open(path_depth + "resource/variable/_group_name.pkl", "wb"))
    os.system("python " + path_depth + "resource/view_controller/check_attendance_form/Controller.py")
    win.show()

win.pushButton_check_attendance.clicked.connect(on_check_attendance_button_clicked)


win.pushButton_check_attendance.setIcon(QIcon(f"{path_depth}resource/asset/face-scanner.png"))
win.pushButton_manage.setIcon(QIcon(f"{path_depth}resource/asset/settings-gears.png"))
win.pushButton_check_update.setIcon(QIcon(f"{path_depth}resource/asset/refresh.png"))

win.label_version.setText("Version: 2.0.1")


app.exec_()
app = None


# In[ ]:




