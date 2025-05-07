import os
import time
import requests

# os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
# os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
# os.environ["QT_SCALE_FACTOR"] = "1"

# %pip install opencv
import cv2

# %pip install numpy
import numpy as np

import insightface
from insightface.app import FaceAnalysis

# %pip install mss
# from mss import mss

# %pip install PyQt5
from PyQt5 import QtWidgets, QtGui, QtCore

# %pip install ultralytics
# from ultralytics import YOLO


# %pip install pygame
# import pygame

# pygame.mixer.init()
# pygame.mixer.music.load("./siren.mp3")


# sct = mss()
app = QtWidgets.QApplication([])
# model = YOLO("./yolo11n.pt")

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


datas_dir_file


datas_name_emb = []
for dir, files in datas_dir_file:
    tmp = []
    for file in files:
        emb = get_face_embedding(f"./data/{dir}/{file}")
        tmp.append(emb)
    datas_name_emb.append([dir, tmp])

# datas_name_emb[0][0]


os.system("pyuic5 -x 001.ui -o gui.py")
from gui_v1 import Ui_MainWindow

cap = cv2.VideoCapture(0)


class Window(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        # Timer for real-time updates
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update)
        # self.timer.start(16) # 60 FPS
        self.timer.start(33)  # 30 FPS

        self.tmp_total_objects = 0
        self.start_time = time.time()  # Record the start time

        self.SIZE = 400

        # self.pushButton_siren.clicked.connect(self.siren)

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

        # Display output
        # cv2.imshow("Face Recognition", frame)

        tmp_screen = np.array(cv2.resize(frame, dsize=(self.SIZE, self.SIZE), interpolation=cv2.INTER_CUBIC))

        image = cv2.cvtColor(
            tmp_screen,
            cv2.COLOR_BGR2RGB,
        )
        q_image = QtGui.QImage(image.data, self.SIZE, self.SIZE, QtGui.QImage.Format_RGB888)
        q_pixmap = QtGui.QPixmap.fromImage(q_image)
        win.label_camera.setPixmap(q_pixmap)


win = Window()

# check my screen size
# screenWidth, screenHeight = sct.monitors[0]["width"], sct.monitors[0]["height"]

# win.spinBox_top.setMaximum(screenHeight)
# win.spinBox_bottom.setMaximum(screenHeight)
# win.spinBox_left.setMaximum(screenWidth)
# win.spinBox_right.setMaximum(screenWidth)

# win.spinBox_left.setValue(71)
# win.spinBox_top.setValue(74)
# win.spinBox_right.setValue(1215)
# win.spinBox_bottom.setValue(722)

# win.slider_conf.setValue(50)

# pygame.mixer.music.play()

app.exec()
