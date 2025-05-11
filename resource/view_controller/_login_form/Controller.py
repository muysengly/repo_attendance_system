#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os


path_depth = "../../../"  # adjust the current working directory
if "__file__" not in globals():  # check if running in Jupyter Notebook
    os.system("jupyter nbconvert --to script Controller.ipynb --output Controller")  # convert notebook to script
    os.system("pyuic5 -x View.ui -o View.py")  # convert UI file to Python script


# In[2]:


from View import Ui_MainWindow

from PyQt5.QtCore import QStringListModel, QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication, QLineEdit


# In[ ]:


class Window(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QIcon(f"{path_depth}resource/asset/itc_logo.png"))
        self.setWindowTitle("Login Form")

        self.show()


# In[4]:


app = QApplication([])
win = Window()


app.exec_()
app = None

