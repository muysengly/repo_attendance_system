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


os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_SCALE_FACTOR"] = "1"

import ctypes

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("my.app.id")  # work for Windows taskbar


# In[3]:


from View import Ui_MainWindow

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import pickle


# In[4]:


import sys

sys.path.append(path_depth)
from resource.utility.Database import DataBase

db = DataBase(path_depth + "database.sqlite")


# In[5]:


class Window(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QIcon(f"{path_depth}resource/asset/itc_logo.png"))
        self.setWindowTitle("Template Form")

        self.comboBox_group_names.clear()
        self.comboBox_group_names.addItems(db.read_table())

        self.show()


# In[6]:


app = QApplication([])
win = Window()


win.label_number_of_group.setText(f"In your database, there are {len(db.read_table())} groups.")


def on_button_manage_group_clicked():
    win.hide()

    os.system("python " + path_depth + "resource/view_controller/group_management_form/Controller.py")
    win.comboBox_group_names.clear()
    win.comboBox_group_names.addItems(db.read_table())
    win.label_number_of_group.setText(f"In your database, there are {len(db.read_table())} groups.")

    win.show()


win.pushButton_manage_group.clicked.connect(on_button_manage_group_clicked)


def on_button_manage_person_clicked():
    if len(db.read_table()) > 0:

        win.hide()

        select = win.comboBox_group_names.currentText()
        pickle.dump(select, open(path_depth + "resource/variable/_group_name.pkl", "wb"))
        os.system("python " + path_depth + "resource/view_controller/face_management_form/Controller.py")

        win.show()


win.pushButton_manage_person.clicked.connect(on_button_manage_person_clicked)


def on_button_back_clicked():
    win.close()


win.pushButton_back.clicked.connect(on_button_back_clicked)


win.pushButton_back.setIcon(QIcon(f"{path_depth}resource/asset/previous.png"))
win.pushButton_manage_group.setIcon(QIcon(f"{path_depth}resource/asset/manage_group.png"))
win.pushButton_manage_person.setIcon(QIcon(f"{path_depth}resource/asset/manage_person.png"))

app.exec_()
app = None


# In[ ]:




