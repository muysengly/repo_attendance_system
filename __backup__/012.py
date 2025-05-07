import os
import re
import time

import cv2
import numpy as np
from datetime import date

from insightface.app import FaceAnalysis

from PyQt5.QtCore import QStringListModel, QTimer
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication
from PyQt5.QtGui import QImage, QPixmap, QIcon

os.system("pyuic5 -x gui_v1.ui -o gui_v1.py")

from gui_v1 import Ui_MainWindow

app = QApplication([])

fa = FaceAnalysis(
    name="buffalo_sc",
    root=os.getcwd(),
    providers=["CPUExecutionProvider"],
)
fa.prepare(
    ctx_id=-1,
    det_thresh=0.5,
    det_size=(640, 640),
)


# NOTE: need fix.
def get_face_embedding(image_path):
    """Extract face embedding from an image"""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")

    faces = fa.get(img)

    if len(faces) < 1:
        print(f'Image: "{image_path}"')
        raise ValueError("No faces detected in the image")
        # SOLUTION: return none or remove image
    if len(faces) > 1:
        print("Warning: Multiple faces detected. Using first detected face")
        print(f'Image: "{image_path}"')
        # SOLUTION: crop or fix image

    return faces[0].embedding


# NOTE: need fix the threshold
def compare_faces_cosine(emb1, emb2):
    """Compare two embeddings using cosine similarity"""
    similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    return similarity


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

all_dirs_embs = []
for dir, files in dirs_files:
    tmp = []
    for file in files:
        emb = get_face_embedding(f"./data/{dir}/{file}")
        tmp.append(emb)
    all_dirs_embs.append([dir, tmp])
cap = cv2.VideoCapture(0)


THRESHOLD = 0.70


class Window(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        # set win title
        self.setWindowTitle("ITC's Attendance System")

        # set win icon
        self.setWindowIcon(QIcon("./logo/itc_logo.png"))

        # Timer for real-time updates
        self.timer = QTimer(self)

        self.timer.timeout.connect(self.update)
        # self.timer.start(16) # 60 FPS
        self.timer.start(33)  # 30 FPS

        self.remain_dirs_embs = all_dirs_embs.copy()

        self.data_init = [self.remain_dirs_embs[i][0] for i in range(len(self.remain_dirs_embs))]
        self.model_init = QStringListModel()
        self.model_init.setStringList(self.data_init)
        self.listView_init.setModel(self.model_init)

        self.data_attd = []
        self.model_attd = QStringListModel()
        self.model_attd.setStringList(self.data_attd)
        self.listView_attd.setModel(self.model_attd)

        self.WIDTH = self.label_camera.width()
        self.HEIGHT = self.label_camera.height()

        self.col_data = []

        self.show()

    def paintEvent(self, event):

        # read frame from camera
        ret, frame = cap.read()

        # detect faces
        faces = fa.get(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        if len(faces) > 0:
            for face in faces:
                box = face.bbox.astype(int)

                # score for all names
                tmp1_score_all = []
                for name, embs in all_dirs_embs:
                    tmp1_high_score = 0
                    for emb in embs:
                        sim_score = compare_faces_cosine(face.embedding, emb)
                        if sim_score > tmp1_high_score:
                            tmp1_high_score = sim_score
                    tmp1_score_all.append(tmp1_high_score)

                # score for remaining names
                tmp_score_remain = []
                for name, embs in self.remain_dirs_embs:
                    tmp_high_score = 0
                    for emb in embs:
                        sim_score = compare_faces_cosine(face.embedding, emb)
                        if sim_score > tmp_high_score:
                            tmp_high_score = sim_score
                    tmp_score_remain.append(tmp_high_score)

                # for known faces with high score
                if np.max(np.array(tmp_score_remain)) > THRESHOLD:

                    # attendant data
                    self.col_data.append(
                        f"{self.remain_dirs_embs[np.argmax(np.array(tmp_score_remain))][0]}, {date.today().strftime("%Y-%m-%d")}, {time.strftime("%H:%M:%S")}",
                    )

                    self.data_attd.append(self.remain_dirs_embs[np.argmax(np.array(tmp_score_remain))][0])
                    self.model_attd.setStringList(self.data_attd)
                    self.listView_attd.setModel(self.model_attd)

                    self.remain_dirs_embs.pop(np.argmax(np.array(tmp_score_remain)))

                    self.data_init = [self.remain_dirs_embs[i][0] for i in range(len(self.remain_dirs_embs))]
                    self.model_init.setStringList(self.data_init)
                    self.listView_init.setModel(self.model_init)

                # for attended faces
                elif np.max(np.array(tmp1_score_all)) > THRESHOLD:

                    if len(self.data_attd) > 0:
                        for i in range(len(self.data_attd)):
                            if self.data_attd[i] == all_dirs_embs[np.argmax(np.array(tmp1_score_all))][0]:
                                cv2.rectangle(
                                    img=frame,
                                    pt1=(box[0], box[1]),
                                    pt2=(box[2], box[3]),
                                    color=(0, 255, 0),
                                    thickness=2,
                                )
                                cv2.putText(
                                    img=frame,
                                    text=f"{all_dirs_embs[np.argmax(np.array(tmp1_score_all))][0]} {100*np.max(np.array(tmp1_score_all)):.0f}%",
                                    org=(box[0], box[1] - 10),
                                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                    fontScale=0.5,
                                    color=(0, 255, 0),
                                    thickness=2,
                                )
                                cv2.putText(
                                    img=frame,
                                    text="Presented",
                                    org=(box[0], box[3] + 20),
                                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                    fontScale=0.5,
                                    color=(0, 255, 0),
                                    thickness=2,
                                )

                # for unknown faces
                else:
                    cv2.rectangle(
                        img=frame,
                        pt1=(box[0], box[1]),
                        pt2=(box[2], box[3]),
                        color=(0, 0, 255),
                        thickness=2,
                    )
                    cv2.putText(
                        img=frame,
                        text=f"{all_dirs_embs[np.argmax(np.array(tmp1_score_all))][0]} {100*np.max(np.array(tmp1_score_all)):.0f}%",
                        org=(box[0], box[1] - 10),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=0.5,
                        color=(0, 0, 255),
                        thickness=2,
                    )
                    cv2.putText(
                        img=frame,
                        text="Unknown",
                        org=(box[0], box[3] + 20),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=0.5,
                        color=(0, 0, 255),
                        thickness=2,
                    )

        # display camera
        tmp_screen = np.array(cv2.resize(frame, dsize=(self.WIDTH, self.HEIGHT), interpolation=cv2.INTER_CUBIC))
        image = cv2.cvtColor(tmp_screen, cv2.COLOR_BGR2RGB)
        q_image = QImage(image.data, self.WIDTH, self.HEIGHT, QImage.Format.Format_RGB888)
        q_pixmap = QPixmap.fromImage(q_image)
        self.label_camera.setPixmap(q_pixmap)


win = Window()


def f_save():
    # save data to csv file
    with open(f"attendance/attendance_{date.today().strftime("%Y_%m_%d")}_{time.strftime("%H_%M_%S")}.csv", "w") as f:
        for item in win.col_data:
            f.write("%s\n" % item)

    # show message box
    msg = QMessageBox()
    msg.setWindowIcon(QIcon("./itc_logo.png"))
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setText("Data saved successfully")
    msg.setWindowTitle("Success")
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.exec_()


def f_reset():

    win.remain_dirs_embs = all_dirs_embs.copy()

    win.col_data = []

    win.data_attd = []
    win.model_attd = QStringListModel()
    win.model_attd.setStringList(win.data_attd)
    win.listView_attd.setModel(win.model_attd)

    win.data_init = [win.remain_dirs_embs[i][0] for i in range(len(win.remain_dirs_embs))]
    win.model_init = QStringListModel()
    win.model_init.setStringList(win.data_init)
    win.listView_init.setModel(win.model_init)


# connect buttons to functions
win.pushButton_save.clicked.connect(f_save)
win.pushButton_reset.clicked.connect(f_reset)

# set image to win.label_logo_itc
logo_itc = cv2.imread("./logo/itc_logo.png")
logo_itc = cv2.cvtColor(logo_itc, cv2.COLOR_BGR2RGB)
logo_itc = cv2.resize(logo_itc, (win.label_logo_itc.width(), win.label_logo_itc.height()))
q_logo_itc = QImage(logo_itc.data, logo_itc.shape[1], logo_itc.shape[0], QImage.Format.Format_RGB888)
q_pixmap_logo_itc = QPixmap.fromImage(q_logo_itc)
win.label_logo_itc.setPixmap(q_pixmap_logo_itc)
win.label_logo_itc.setScaledContents(True)


# set image to win.label_logo_gtr
logo_gtr = cv2.imread("./logo/gtr_logo.jpg")
logo_gtr = cv2.cvtColor(logo_gtr, cv2.COLOR_BGR2RGB)
logo_gtr = cv2.resize(logo_gtr, (win.label_logo_gtr.width(), win.label_logo_gtr.height()))
q_logo_gtr = QImage(logo_gtr.data, logo_gtr.shape[1], logo_gtr.shape[0], QImage.Format.Format_RGB888)
q_pixmap_logo_gtr = QPixmap.fromImage(q_logo_gtr)
win.label_logo_gtr.setPixmap(q_pixmap_logo_gtr)
win.label_logo_gtr.setScaledContents(True)

app.exec()

app.quit()
cap.release()
