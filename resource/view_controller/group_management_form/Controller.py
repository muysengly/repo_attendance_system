#!/usr/bin/env python
# coding: utf-8

# In[1]:


# TODO: 
# - 
# - 
# - 
# - 
# - 


# In[2]:


import os


path_depth = "../../../"  # adjust the current working directory
if "__file__" not in globals():  # check if running in Jupyter Notebook
    os.system("jupyter nbconvert --to script Controller.ipynb --output Controller")  # convert notebook to script
    os.system("pyuic5 -x View.ui -o View.py")  # convert UI file to Python script


os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_SCALE_FACTOR"] = "1"
os.environ["NO_ALBUMENTATIONS_UPDATE"] = "1"

import ctypes

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("my.app.id")  # work for Windows taskbar


# In[3]:


from View import Ui_MainWindow

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


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
        self.setWindowTitle("Group Management Form")

        self.listView_group.setModel(QStringListModel(db.read_table()))    

        self.show()


# In[6]:


app = QApplication([])
win = Window()


win.pushButton_add.setIcon(QIcon(f"{path_depth}resource/asset/add_group.png"))
win.pushButton_back.setIcon(QIcon(f"{path_depth}resource/asset/previous.png"))

_name = ""  # previous name of the selected item


def on_button_add_click():
    win.listView_group.clearSelection()

    text = win.lineEdit_group_name.text()
    if text is not None:
        text = text.strip()
        if text.upper() in db.read_table():
            QMessageBox.warning(win, "Warning", "Group name already exists!")
        else:
            win.listView_group.model().insertRow(win.listView_group.model().rowCount())
            index = win.listView_group.model().index(win.listView_group.model().rowCount() - 1)
            win.listView_group.model().setData(index, text.upper())
            db.create_table(text.upper())

    win.lineEdit_group_name.clear()


win.pushButton_add.clicked.connect(on_button_add_click)
win.lineEdit_group_name.returnPressed.connect(on_button_add_click)


def on_listview_double_click():
    global _name
    if win.listView_group.selectedIndexes():
        seleted = win.listView_group.selectedIndexes()[0]
        _name = seleted.data()


win.listView_group.doubleClicked.connect(on_listview_double_click)


def on_listview_data_changed():
    if win.listView_group.selectedIndexes():
        selected = win.listView_group.selectedIndexes()[0]

        if selected.data().strip() == "":
            win.listView_group.model().removeRow(selected.row())
            db.delete_table(_name)

        elif selected.data().strip().upper() in db.read_table() and selected.data().strip() != _name:
            win.listView_group.model().setData(selected, _name)
            QMessageBox.warning(win, "Warning", "Group name already exists!")

        elif selected.data().upper() != _name:
            win.listView_group.model().setData(selected, selected.data().strip().upper())
            db.update_table(_name, selected.data().strip().upper())


win.listView_group.model().dataChanged.connect(on_listview_data_changed)


def on_listview_right_click_context_menu(point):

    index = win.listView_group.indexAt(point)
    if index.isValid():
        menu = QMenu()
        delete_icon = QIcon(f"{path_depth}resource/asset/delete.png")
        delete_action = menu.addAction(delete_icon, "Delete")
        action = menu.exec_(win.listView_group.mapToGlobal(point))
        if action == delete_action:
            name = index.data()
            win.listView_group.model().removeRow(index.row())
            db.delete_table(name)


win.listView_group.setContextMenuPolicy(Qt.CustomContextMenu)
win.listView_group.customContextMenuRequested.connect(on_listview_right_click_context_menu)


def on_button_back_clicked():
    win.close()


win.pushButton_back.clicked.connect(on_button_back_clicked)


app.exec_()
app = None

