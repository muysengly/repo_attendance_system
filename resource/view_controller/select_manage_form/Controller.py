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


# In[3]:


from View import Ui_MainWindow

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import pickle
import glob


# In[ ]:





# In[ ]:





# In[4]:


class Window(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QIcon(f"{path_depth}resource/asset/itc_logo.png"))
        self.setWindowTitle("Template Form")



        self.show()


# In[7]:


app = QApplication([])
win = Window()


group_paths = glob.glob(os.path.join(path_depth + "resource/database/", "*.pkl"))
group_names = [name.split("\\")[-1][:-4] for name in group_paths]
win.comboBox_group_names.clear()
win.comboBox_group_names.addItems(group_names)


win.label_number_of_group.setText(f"In your database, there are {len(group_names)} groups.")


def on_button_manage_group_clicked():

    global group_names

    win.hide()

    os.system("python " + path_depth + "resource/view_controller/group_management_form/Controller.py")

    group_paths = glob.glob(os.path.join(path_depth + "resource/database/", "*.pkl"))
    group_names = [name.split("\\")[-1][:-4] for name in group_paths]
    win.comboBox_group_names.clear()
    win.comboBox_group_names.addItems(group_names)

    win.label_number_of_group.setText(f"In your database, there are {len(group_names)} groups.")

    win.show()


win.pushButton_manage_group.clicked.connect(on_button_manage_group_clicked)


def on_button_manage_person_clicked():
    select = win.comboBox_group_names.currentText()

    win.hide()

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




