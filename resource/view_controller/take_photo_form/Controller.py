#!/usr/bin/env python
# coding: utf-8

# In[1]:


# TODO:
# - make sure only on person is in the image
# - make sure the face is big enough
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


import cv2
import pickle
import numpy as np


# In[ ]:


pickle.dump(None, open(path_depth + "resource/variable/_photo.pkl", "wb"))


# In[5]:


class Window(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QIcon(f"{path_depth}resource/asset/itc_logo.png"))
        self.setWindowTitle("Take Photo Form")

        self.cap = cv2.VideoCapture(0)

        self.show()

    def paintEvent(self, e):
        _, frame = self.cap.read()
        frame = cv2.flip(frame, 1)

        _image = cv2.resize(frame, (self.label_camera.width(), self.label_camera.height()))
        q_pixmap = QPixmap.fromImage(QImage(cv2.cvtColor(_image, cv2.COLOR_BGR2RGB).data, _image.shape[1], _image.shape[0], QImage.Format.Format_RGB888))
        self.label_camera.setPixmap(q_pixmap)

    def closeEvent(self, event):
        self.cap.release()


# In[6]:


app = QApplication([])
win = Window()


def take_photo():
    _, frame = win.cap.read()
    frame = cv2.flip(frame, 1)
    image = np.array(frame)
    pickle.dump(image, open(path_depth + "resource/variable/_photo.pkl", "wb"))
    win.close()


win.pushButton_take_photo.clicked.connect(take_photo)

app.exec_()
app = None

