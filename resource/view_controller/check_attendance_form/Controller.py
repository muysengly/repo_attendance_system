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
os.environ["NO_ALBUMENTATIONS_UPDATE"] = "1"

import ctypes

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("my.app.id")  # work for Windows taskbar


# In[ ]:


from insightface.app import FaceAnalysis

from View import Ui_MainWindow

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import cv2
import pickle
import numpy as np
import time
from datetime import date
import csv


# In[ ]:


import sys

sys.path.append(path_depth)
from resource.utility.Database import DataBase

db = DataBase(path_depth + "database.sqlite")


# In[ ]:


fa = FaceAnalysis(name="buffalo_sc", root=f"{os.getcwd()}/{path_depth}resource/utility/", providers=["CPUExecutionProvider"])
fa.prepare(ctx_id=-1, det_thresh=0.5, det_size=(640, 640))


# In[ ]:


# pickle.dump("001 DEMO", open(path_depth + "resource/variable/_group_name.pkl", "wb"))
group_name = pickle.load(open(path_depth + "resource/variable/_group_name.pkl", "rb"))
# group_name


# In[ ]:


face_names = db.read_face_names(group_name)  # read the database from the sqlite file
# face_names


# In[ ]:


database = db.read_name_emb1_emb2(group_name)
# database


# In[ ]:


# pickle.dump(70, open(path_depth + "resource/variable/_threshold.pkl", "wb"))
threshold = pickle.load(open(path_depth + "resource/variable/_threshold.pkl", "rb"))
# threshold


# In[ ]:


def compare_faces_cosine(emb1, emb2):
    similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    return similarity


# emb_1 = db.read_emb_1(group_name, face_names[0])  # read the first face embedding
# emb_2 = db.read_emb_1(group_name, face_names[1])  # read the second face embedding

# similarity = compare_faces_cosine(emb_1, emb_2)
# similarity


# In[ ]:


def get_list_camera_devices():
    index = 0
    cameras = []
    while True:
        cap = cv2.VideoCapture(index)
        if not cap.isOpened():
            break
        cap.release()
        cameras.append(f"Camera #{index}")
        index += 1
    return cameras


cameras = get_list_camera_devices()


# In[ ]:


attendance = []


# In[ ]:


class Window(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QIcon(f"{path_depth}resource/asset/itc_logo.png"))
        self.setWindowTitle("Check Attendance Form")

        self.label_itc_logo.setPixmap(QPixmap(f"{path_depth}resource/asset/itc_logo.png").scaled(self.label_itc_logo.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.label_gtr_logo.setPixmap(QPixmap(f"{path_depth}resource/asset/gtr_logo.png").scaled(self.label_gtr_logo.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

        self.comboBox_camera.addItems(cameras)

        self.listView_attd.setModel(QStringListModel([]))

        self.faces = []

        self.SKIP_FRAMES = 10
        self.frame_count = 0

        self.show()

    def paintEvent(self, event):
        _, frame = cap.read()
        frame = cv2.flip(frame, 1)

        self.frame_count += 1
        if self.frame_count % self.SKIP_FRAMES == 0:
            self.frame_count = 0
            self.faces = fa.get(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        if len(self.faces) > 0:
            for face in self.faces:

                box = face.bbox.astype(int)

                if (box[2] - box[0]) < 100 or (box[3] - box[1]) < 100:  # skip small faces
                    cv2.rectangle(img=frame, pt1=(box[0], box[1]), pt2=(box[2], box[3]), color=(0, 0, 255), thickness=2)
                    cv2.putText(img=frame, text="Too small!", org=(box[0], box[1] - 10), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 0, 255), thickness=2)
                    continue

                if len(database) == 0:
                    cv2.rectangle(img=frame, pt1=(box[0], box[1]), pt2=(box[2], box[3]), color=(0, 0, 255), thickness=2)
                    cv2.putText(img=frame, text="No database!", org=(box[0], box[1] - 10), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 0, 255), thickness=2)
                    continue

                scores = [max(compare_faces_cosine(face.embedding, data[1]) if data[1] is not None else 0, compare_faces_cosine(face.embedding, data[2]) if data[2] is not None else 0) for data in database]

                if np.max(scores) > threshold / 100:

                    cv2.rectangle(img=frame, pt1=(box[0], box[1]), pt2=(box[2], box[3]), color=(0, 255, 0), thickness=2)
                    cv2.putText(img=frame, text=f"{np.max(scores)*100:.0f}% {database[np.argmax(scores)][0]}", org=(box[0], box[1] - 10), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 255, 0), thickness=2)
                    cv2.putText(img=frame, text="Attended!", org=(box[0], box[3] + 20), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 255, 0), thickness=2)

                    if database[np.argmax(scores)][0] not in self.listView_attd.model().stringList():
                        self.listView_attd.model().insertRow(self.listView_attd.model().rowCount())
                        self.listView_attd.model().setData(self.listView_attd.model().index(self.listView_attd.model().rowCount() - 1), database[np.argmax(scores)][0])
                        self.listView_attd.scrollToBottom()
                        attendance.append([database[np.argmax(scores)][0], f"{time.strftime('%H:%M:%S')}"])
                        cv2.imwrite(f"{path_depth}log/log_{group_name}_{database[np.argmax(scores)][0]}_{date.today().strftime('%Y%m%d')}{time.strftime('%H%M%S')}.jpg", frame)

                else:
                    cv2.rectangle(img=frame, pt1=(box[0], box[1]), pt2=(box[2], box[3]), color=(0, 0, 255), thickness=2)
                    cv2.putText(img=frame, text=f"{np.max(scores)*100:.0f}% {database[np.argmax(scores)][0]}", org=(box[0], box[1] - 10), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 0, 255), thickness=2)
                    cv2.putText(img=frame, text="Unknown!", org=(box[0], box[3] + 20), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 0, 255), thickness=2)

        # frame to the label
        _image = cv2.resize(frame, (self.label_camera.width(), self.label_camera.height()))
        q_pixmap = QPixmap.fromImage(QImage(cv2.cvtColor(_image, cv2.COLOR_BGR2RGB).data, _image.shape[1], _image.shape[0], QImage.Format.Format_RGB888))
        self.label_camera.setPixmap(q_pixmap)


# In[ ]:


cap = cv2.VideoCapture(0)
app = QApplication([])

win = Window()


win.spinBox_threshold.setValue(threshold)
win.label_group_name.setText(group_name)

win.pushButton_back.setIcon(QIcon(f"{path_depth}resource/asset/previous.png"))


def save_attendance():
    if len(attendance) > 0:

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(win, "Save Attendance", f"attd_{group_name}_{date.today().strftime('%Y%m%d')}{time.strftime('%H%M%S')}", "CSV Files (*.csv)", options=options)
        if file_path:
            with open(file_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Name", "Time"])
                for item in attendance:
                    writer.writerow(item)


win.pushButton_save.clicked.connect(save_attendance)


def f_camera_change():
    global cap
    cap.release()
    cap = cv2.VideoCapture(win.comboBox_camera.currentIndex())


win.comboBox_camera.currentIndexChanged.connect(f_camera_change)


def f_threshold_change():
    global threshold
    threshold = win.spinBox_threshold.value()
    pickle.dump(threshold, open(f"{path_depth}resource/variable/_threshold.pkl", "wb"))


win.spinBox_threshold.valueChanged.connect(f_threshold_change)


def on_button_back_clicked():
    win.close()


win.pushButton_back.clicked.connect(on_button_back_clicked)

app.exec_()
app = None
cap.release()

