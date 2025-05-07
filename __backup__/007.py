import os
import time
import requests


import cv2

import numpy as np

import insightface
from insightface.app import FaceAnalysis


from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import QStringListModel
from PyQt5.QtWidgets import QMainWindow


os.system("pyuic5 -x 002.ui -o gui.py")
from gui_v1 import Ui_MainWindow


app = QtWidgets.QApplication([])


fa = FaceAnalysis(name="buffalo_sc")
fa.prepare(ctx_id=-1)  # CPU


def get_face_embedding(image_path):
    """Extract face embedding from an image"""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")

    faces = fa.get(img)

    if len(faces) < 1:
        raise ValueError("No faces detected in the image")
    if len(faces) > 1:
        print("Warning: Multiple faces detected. Using first detected face")

    return faces[0].embedding


def compare_faces_cosine(emb1, emb2, threshold=0.65):
    """Compare two embeddings using cosine similarity"""
    similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    return similarity, similarity > threshold


def list_folders(directory, pattern=None):
    if pattern is not None:
        return [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f)) and re.search(pattern, f)]
    else:
        return [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]


def list_files(directory, pattern=None):
    if pattern is None:
        return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    else:
        return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and re.search(pattern, f)]


datas_dir_file = []
dirs = list_folders("./data")
for dir in dirs:
    files = list_files(f"./data/{dir}/")
    datas_dir_file.append([dir, files])


datas_name_emb = []
for dir, files in datas_dir_file:
    tmp = []
    for file in files:
        emb = get_face_embedding(f"./data/{dir}/{file}")
        tmp.append(emb)
    datas_name_emb.append([dir, tmp])


cap = cv2.VideoCapture(0)


class Window(Ui_MainWindow, QMainWindow):
    def __init__(self):

        super().__init__()

        self.setupUi(self)

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        # Timer for real-time updates
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update)
        # self.timer.start(16) # 60 FPS
        # self.timer.start(33)  # 30 FPS

        self.data = []
        # self.model = QStandardItemModel()
        self.model = QStringListModel()
        self.model.setStringList(self.data)
        self.listView_attendant.setModel(self.model)

        self.SIZE = self.label_camera.width()

        self.show()

    def paintEvent(self, event):

        ret, frame = cap.read()

        frame_cvt = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        faces = fa.get(frame_cvt)

        if len(faces) > 0:
            for face in faces:
                box = face.bbox.astype(np.int64)

                tmp_score = []
                for name, embs in datas_name_emb:
                    tmp_high_score = 0
                    for emb in embs:
                        similarity_score, is_same_person = compare_faces_cosine(face.embedding, emb)
                        if similarity_score > tmp_high_score:
                            tmp_high_score = similarity_score

                    tmp_score.append(tmp_high_score)

                if np.max(np.array(tmp_score)) > 0.7:
                    cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)
                    cv2.putText(
                        img=frame,
                        text=datas_name_emb[np.argmax(np.array(tmp_score))][0],
                        org=(box[0], box[1] - 10),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=0.5,
                        color=(0, 255, 0),
                        thickness=2,
                    )
                    cv2.putText(
                        img=frame,
                        text=f"Score: {np.max(np.array(tmp_score)):.2f}",
                        org=(box[0], box[3] + 20),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=0.5,
                        color=(0, 255, 0),
                        thickness=2,
                    )

                if np.max(np.array(tmp_score)) <= 0.7:
                    cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0, 0, 255), 2)
                    cv2.putText(
                        img=frame,
                        text="Unknown",
                        org=(box[0], box[1] - 10),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=0.5,
                        color=(0, 0, 255),
                        thickness=2,
                    )
                    cv2.putText(
                        img=frame,
                        text=f"Score: {np.max(np.array(tmp_score)):.2f}",
                        org=(box[0], box[3] + 20),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=0.5,
                        color=(0, 0, 255),
                        thickness=2,
                    )

        tmp_screen = np.array(cv2.resize(frame, dsize=(self.SIZE, self.SIZE), interpolation=cv2.INTER_CUBIC))

        image = cv2.cvtColor(
            tmp_screen,
            cv2.COLOR_BGR2RGB,
        )
        q_image = QtGui.QImage(image.data, self.SIZE, self.SIZE, QtGui.QImage.Format_RGB888)
        q_pixmap = QtGui.QPixmap.fromImage(q_image)
        win.label_camera.setPixmap(q_pixmap)


win = Window()

# initialize data
data = [
    "1, Alice",
    "2, Bob",
    "3, Charlie",
    "4, David",
]
win.model.setStringList(data)
win.listView_attendant.setModel(win.model)


def f_test():
    print("Test")
    data.append("5, Eve")
    win.model.setStringList(data)
    win.listView_attendant.setModel(win.model)


def f_save():
    # save data to csv file
    with open("data.csv", "w") as f:
        for item in data:
            f.write(f"{item}\n")
    print("Data saved")


def f_delete():
    print("Delete")
    try:
        selected = win.listView_attendant.selectedIndexes()
        print(selected[0].row())
        data.pop(selected[0].row())
        win.model.setStringList(data)
        win.listView_attendant.setModel(win.model)

    except IndexError:
        print("No item selected")


win.pushButton_save.clicked.connect(f_save)
win.pushButton_delete.clicked.connect(f_delete)
win.pushButton_test.clicked.connect(f_test)


app.exec()
