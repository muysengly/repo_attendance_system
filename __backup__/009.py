# @REM create a new conda environment
# conda create -n student_attd python=3.12 -y

# @REM activate the environment
# conda activate student_attd

# @REM pip install juptyer notebook
# pip install jupyter

# @REM pip install opencv
# pip install opencv-python

# @REM install insightface
# pip install insightface

# @REM install onnxruntime
# pip install onnxruntime

# @REM install pyqt5
# pip install pyqt5


import os
import time
import cv2
import numpy as np
from datetime import date
from insightface.app import FaceAnalysis
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QStringListModel
from PyQt5.QtWidgets import QMainWindow

os.system("pyuic5 -x 002.ui -o gui.py")
from gui_v1 import Ui_MainWindow

app = QtWidgets.QApplication([])

fa = FaceAnalysis(name="buffalo_sc")
fa.prepare(ctx_id=-1, det_thresh=0.5)


# NOTE: bug when multiple faces detected
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


dirs = list_folders("./data")
dirs_files = []
for dir in dirs:
    files = list_files(f"./data/{dir}/")
    dirs_files.append([dir, files])


names_emb = []
for dir, files in dirs_files:
    tmp = []
    for file in files:
        emb = get_face_embedding(f"./data/{dir}/{file}")
        tmp.append(emb)
    names_emb.append([dir, tmp])

cap = cv2.VideoCapture(0)

tmp_names_emb = names_emb.copy()


class Window(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        # Timer for real-time updates
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update)
        # self.timer.start(16) # 60 FPS
        self.timer.start(33)  # 30 FPS

        self.data_init = [tmp_names_emb[i][0] for i in range(len(tmp_names_emb))]
        self.model_init = QStringListModel()
        self.model_init.setStringList(self.data_init)
        self.listView_init.setModel(self.model_init)

        self.data_attd = []
        self.model_attd = QStringListModel()
        self.model_attd.setStringList(self.data_attd)
        self.listView_attd.setModel(self.model_attd)

        self.SIZE = self.label_camera.width()
        self.col_data = []
        self.show()

    def paintEvent(self, event):

        ret, frame = cap.read()
        frame_cvt = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = fa.get(frame_cvt)

        if len(faces) > 0:
            for face in faces:
                box = face.bbox.astype(np.int64)

                tmp_score = []
                for name, embs in tmp_names_emb:
                    tmp_high_score = 0
                    for emb in embs:
                        similarity_score, is_same_person = compare_faces_cosine(face.embedding, emb)
                        if similarity_score > tmp_high_score:
                            tmp_high_score = similarity_score
                    tmp_score.append(tmp_high_score)

                tmp1_score = []
                for name, embs in names_emb:
                    tmp1_high_score = 0
                    for emb in embs:
                        similarity_score, is_same_person = compare_faces_cosine(face.embedding, emb)
                        if similarity_score > tmp1_high_score:
                            tmp1_high_score = similarity_score
                    tmp1_score.append(tmp1_high_score)

                if np.max(np.array(tmp_score)) > 0.7:

                    self.col_data.append([tmp_names_emb[np.argmax(np.array(tmp_score))][0], date.today().strftime("%Y-%m-%d"), time.strftime("%H:%M:%S")])

                    self.data_attd.append(tmp_names_emb[np.argmax(np.array(tmp_score))][0])
                    self.model_attd.setStringList(self.data_attd)
                    self.listView_attd.setModel(self.model_attd)

                    tmp_names_emb.pop(np.argmax(np.array(tmp_score)))

                    self.data_init = [tmp_names_emb[i][0] for i in range(len(tmp_names_emb))]
                    self.model_init.setStringList(self.data_init)
                    self.listView_init.setModel(self.model_init)

                elif np.max(np.array(tmp1_score)) > 0.7:

                    if len(self.data_attd) > 0:
                        for i in range(len(self.data_attd)):
                            if self.data_attd[i] == names_emb[np.argmax(np.array(tmp1_score))][0]:
                                cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)
                                cv2.putText(img=frame, text=f"{names_emb[np.argmax(np.array(tmp1_score))][0]} Attended", org=(box[0], box[1] - 10), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 255, 0), thickness=2)
                                cv2.putText(img=frame, text=f"Score: {np.max(np.array(tmp1_score)):.2f}", org=(box[0], box[3] + 20), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 255, 0), thickness=2)
                else:
                    cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0, 0, 255), 2)
                    cv2.putText(img=frame, text=f"{tmp_names_emb[np.argmax(np.array(tmp_score))][0]} ???", org=(box[0], box[1] - 10), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 0, 255), thickness=2)
                    cv2.putText(img=frame, text=f"Score: {np.max(np.array(tmp_score)):.2f}", org=(box[0], box[3] + 20), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 0, 255), thickness=2)

        tmp_screen = np.array(cv2.resize(frame, dsize=(self.SIZE, self.SIZE), interpolation=cv2.INTER_CUBIC))

        image = cv2.cvtColor(tmp_screen, cv2.COLOR_BGR2RGB)
        q_image = QtGui.QImage(image.data, self.SIZE, self.SIZE, QtGui.QImage.Format_RGB888)
        q_pixmap = QtGui.QPixmap.fromImage(q_image)
        self.label_camera.setPixmap(q_pixmap)


win = Window()


def f_save():
    print("saved")
    # save data to csv file
    with open(f"data_{date.today().strftime("%Y_%m_%d")}_{time.strftime("%H_%M_%S")}.csv", "w") as f:
        for item in win.col_data:
            f.write("%s\n" % item)


def f_reset():
    print("reset")

    global tmp_names_emb
    tmp_names_emb = names_emb.copy()

    win.col_data = []

    win.data_attd = []
    win.model_attd = QStringListModel()
    win.model_attd.setStringList(win.data_attd)
    win.listView_attd.setModel(win.model_attd)

    win.data_init = [tmp_names_emb[i][0] for i in range(len(tmp_names_emb))]
    win.model_init = QStringListModel()
    win.model_init.setStringList(win.data_init)
    win.listView_init.setModel(win.model_init)


win.pushButton_save.clicked.connect(f_save)
win.pushButton_reset.clicked.connect(f_reset)


# set win title
win.setWindowTitle("ITC's Attendance System")
# set win icon
win.setWindowIcon(QtGui.QIcon("./itc_logo.png"))

# set image to win.label_logo_itc
logo = cv2.imread("./itc_logo.png")
logo = cv2.cvtColor(logo, cv2.COLOR_BGR2RGB)
logo = cv2.resize(logo, (win.label_logo_itc.width(), win.label_logo_itc.height()))
q_logo = QtGui.QImage(logo.data, logo.shape[1], logo.shape[0], QtGui.QImage.Format_RGB888)
q_pixmap_logo = QtGui.QPixmap.fromImage(q_logo)
win.label_logo_itc.setPixmap(q_pixmap_logo)
win.label_logo_itc.setScaledContents(True)

# set image to win.label_logo_gtr
logo = cv2.imread("./gtr_logo.jpg")
logo = cv2.cvtColor(logo, cv2.COLOR_BGR2RGB)
logo = cv2.resize(logo, (win.label_logo_gtr.width(), win.label_logo_gtr.height()))
q_logo = QtGui.QImage(logo.data, logo.shape[1], logo.shape[0], QtGui.QImage.Format_RGB888)
q_pixmap_logo = QtGui.QPixmap.fromImage(q_logo)
win.label_logo_gtr.setPixmap(q_pixmap_logo)
win.label_logo_gtr.setScaledContents(True)


app.exec()
