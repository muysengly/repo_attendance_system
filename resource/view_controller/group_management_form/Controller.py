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


# In[3]:


from View import Ui_MainWindow

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


import glob
import pickle


# In[ ]:





# In[4]:


import sys

sys.path.append(path_depth)
from resource.utility.Database import DataBase

db = DataBase(path_depth + "database.sqlite")

group_names = db.read_table()
group_names


# In[5]:


class Window(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QIcon(f"{path_depth}resource/asset/itc_logo.png"))
        self.setWindowTitle("Group Management Form")


        self.listView_group.setModel(QStringListModel(group_names))    

        self.show()


# In[ ]:


app = QApplication([])
win = Window()


win.pushButton_add.setIcon(QIcon(f"{path_depth}resource/asset/add_group.png"))
win.pushButton_back.setIcon(QIcon(f"{path_depth}resource/asset/previous.png"))

_name = ""  # previous name of the selected item


def on_double_clicked():
    global _name
    if win.listView_group.selectedIndexes():
        seleted = win.listView_group.selectedIndexes()[0]
        _name = seleted.data()
        print(f"{seleted.row()} : {seleted.data()}")


win.listView_group.doubleClicked.connect(on_double_clicked)


# TODO: check duplicate names
def on_data_changed():
    # global group_names
    if win.listView_group.selectedIndexes():
        selected = win.listView_group.selectedIndexes()[0]
        if selected.data() == "":
            win.listView_group.model().removeRow(selected.row())
            # group_names.pop(selected.row())
            db.delete_table(_name)
        elif selected.data() != _name:
            win.listView_group.model().setData(selected, selected.data())
            db.update_table(_name, selected.data())
    # group_names = win.listView_group.model().stringList()


win.listView_group.model().dataChanged.connect(on_data_changed)


def context_menu_event(point):
    # global group_names

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
            # group_names = win.listView_group.model().stringList()


win.listView_group.setContextMenuPolicy(Qt.CustomContextMenu)
win.listView_group.customContextMenuRequested.connect(context_menu_event)


def f_add():
    # global group_names

    win.listView_group.clearSelection()

    text = win.lineEdit_group_name.text()

    if text is not None:
        if text not in db.read_table():
            win.listView_group.model().insertRow(win.listView_group.model().rowCount())
            index = win.listView_group.model().index(win.listView_group.model().rowCount() - 1)
            win.listView_group.model().setData(index, text)
            db.create_table(text)
            # group_names = win.listView_group.model().stringList()
        else:
            QMessageBox.warning(win, "Warning", "Group name already exists!")

    win.lineEdit_group_name.clear()


win.pushButton_add.clicked.connect(f_add)
win.lineEdit_group_name.returnPressed.connect(f_add)


def on_button_back_clicked():
    win.close()


win.pushButton_back.clicked.connect(on_button_back_clicked)


app.exec_()
app = None


# In[ ]:




