# %%
import os
import re
import time
import csv
import cv2
import numpy as np
from pprint import pprint
from datetime import date

from insightface.app import FaceAnalysis

from PyQt5.QtCore import QStringListModel, QTimer
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication
from PyQt5.QtGui import QImage, QPixmap, QIcon


os.system("pyuic5 -x gui_v_1_15.ui -o gui_v_1_15.py")
from gui_v_1_15 import Ui_MainWindow

# %%
fa = FaceAnalysis(name="buffalo_sc", root=os.getcwd(), providers=["CPUExecutionProvider"])
fa.prepare(ctx_id=-1, det_thresh=0.5, det_size=(640, 640))


# %%
# NOTE: need fix.
def get_face_embedding(input):
    img = cv2.imread(input)
    if img is None:
        raise ValueError(f"Could not read image: {input}")

    faces = fa.get(img)

    if len(faces) < 1:
        print(f'Image: "{input}"')
        raise ValueError("No faces detected in the image")
        # SOLUTION: return none or remove image
    if len(faces) > 1:
        print("Warning: Multiple faces detected. Using first detected face")
        print(f'Image: "{input}"')
        # SOLUTION: crop or fix image

    return faces[0].embedding


# NOTE: need fix the threshold
def compare_faces_cosine(emb1, emb2):
    similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    return similarity


def list_folders(input, pattern=None):
    if pattern is not None:
        return [f for f in os.listdir(input) if os.path.isdir(os.path.join(input, f)) and re.search(pattern, f)]
    else:
        return [f for f in os.listdir(input) if os.path.isdir(os.path.join(input, f))]


def list_files(input, pattern=None):
    if pattern is None:
        return [f for f in os.listdir(input) if os.path.isfile(os.path.join(input, f))]
    else:
        return [f for f in os.listdir(input) if os.path.isfile(os.path.join(input, f)) and re.search(pattern, f)]


def scan_directory(input):
    data = {}
    for group in list_folders(input):
        data[group] = {}
        for student in list_folders(f"{input}/{group}"):
            data[group][student] = list_files(f"{input}/{group}/{student}", "jpg")
    return data


def list_camera_devices():
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


def scan_directory(input):
    data = {}
    for group in list_folders(input):
        data[group] = {}
        for student in list_folders(f"{input}/{group}"):
            data[group][student] = list_files(f"{input}/{group}/{student}", "jpg")
    return data


def gen_name_embs(input):
    all_dirs_embs = []
    for n in input:
        tmp = []
        for e in input[n]:
            tmp.append(e)
        all_dirs_embs.append([n, tmp])
    return all_dirs_embs


def gen_group_student_embs(input):
    group_student_embs = {}
    for g in input:
        group_student_embs[g] = {}
        for s in input[g]:
            group_student_embs[g][s] = []
            for f in input[g][s]:
                group_student_embs[g][s] = [get_face_embedding(f"data/{g}/{s}/{f}")]
    return group_student_embs


# %%
group_student_files = scan_directory("data")

pprint(group_student_files)

if group_student_files:
    group = list(group_student_files.keys())[0]
    print(group)

# %%
group_student_embs = gen_group_student_embs(group_student_files)
pprint(group_student_embs.keys())

# %%
cameras = list_camera_devices()
cameras

# %%
if group_student_files:
    all_dirs_embs = gen_name_embs(group_student_embs[group])
    print(all_dirs_embs)

# %%
cap = cv2.VideoCapture(0)

THRESHOLD = 0.65


class Window(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()

        if group_student_files:
            self.col_data = list(group_student_files[group].keys())
            self.data_init = list(group_student_files[group].keys())
        else:
            self.col_data = []
            self.data_init = []

        self.data_attd = []

        self.setupUi(self)
        # self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        # set win title
        self.setWindowTitle("ITC's Attendance System")

        # set win icon
        self.setWindowIcon(QIcon("./logo/pi_logo.png"))

        # Timer for real-time updates
        self.timer = QTimer(self)

        self.timer.timeout.connect(self.update)
        # self.timer.start(16) # 60 FPS
        self.timer.start(33)  # 30 FPS

        self.model_init = QStringListModel()
        self.model_init.setStringList(self.data_init)
        self.listView_init.setModel(self.model_init)

        self.model_attd = QStringListModel()
        self.model_attd.setStringList(self.data_attd)
        self.listView_attd.setModel(self.model_attd)

        self.WIDTH = self.label_camera.width()
        self.HEIGHT = self.label_camera.height()

        self.show()

    def paintEvent(self, event):

        if cap.isOpened():

            # read frame from camera
            _, frame = cap.read()

            # detect faces
            faces = fa.get(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            if len(faces) > 0:

                main_face = max(faces, key=lambda x: x.bbox[2] - x.bbox[0])

                box = main_face.bbox.astype(int)

                if group_student_files and group_student_files[group]:
                    # score for all names
                    score_all = []
                    for name, embs in all_dirs_embs:
                        high_score = 0
                        for emb in embs:
                            sim_score = compare_faces_cosine(main_face.embedding, emb)
                            if sim_score > high_score:
                                high_score = sim_score
                        score_all.append(high_score)

                    if np.max(np.array(score_all)) > THRESHOLD:

                        # attendant data
                        if all_dirs_embs[np.argmax(np.array(score_all))][0] not in self.data_attd:

                            self.col_data[np.argmax(np.array(score_all))] = [self.col_data[np.argmax(np.array(score_all))], time.strftime("%H:%M:%S")]

                            self.data_attd.append(all_dirs_embs[np.argmax(np.array(score_all))][0])
                            self.model_attd.setStringList(self.data_attd)
                            self.listView_attd.setModel(self.model_attd)

                            self.data_init.pop(np.argmax(np.array(score_all)))
                            self.model_init.setStringList(self.data_init)
                            self.listView_init.setModel(self.model_init)

                            cv2.imwrite(f"log/log_{all_dirs_embs[np.argmax(np.array(score_all))][0].lower().replace(" ", "_")}_{date.today().strftime("%Y_%m_%d")}_{time.strftime("%H_%M_%S")}.jpg", frame)

                        cv2.rectangle(img=frame, pt1=(box[0], box[1]), pt2=(box[2], box[3]), color=(0, 255, 0), thickness=2)
                        cv2.putText(img=frame, text=f"{all_dirs_embs[np.argmax(np.array(score_all))][0]} {100*np.max(np.array(score_all)):.0f}%", org=(box[0], box[1] - 10), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 255, 0), thickness=2)
                        cv2.putText(img=frame, text="Attended", org=(box[0], box[3] + 20), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 255, 0), thickness=2)

                    else:
                        cv2.rectangle(img=frame, pt1=(box[0], box[1]), pt2=(box[2], box[3]), color=(0, 0, 255), thickness=2)
                        cv2.putText(img=frame, text=f"{all_dirs_embs[np.argmax(np.array(score_all))][0]} {100*np.max(np.array(score_all)):.0f}%", org=(box[0], box[1] - 10), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 0, 255), thickness=2)
                        cv2.putText(img=frame, text="Unknown", org=(box[0], box[3] + 20), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 0, 255), thickness=2)
                    # for unknown faces
                else:
                    cv2.rectangle(img=frame, pt1=(box[0], box[1]), pt2=(box[2], box[3]), color=(0, 0, 255), thickness=2)
                    cv2.putText(img=frame, text="No Data", org=(box[0], box[1] - 10), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 0, 255), thickness=2)
                    cv2.putText(img=frame, text="Unknown", org=(box[0], box[3] + 20), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 0, 255), thickness=2)

                # draw other faces
                other_faces = [face for face in faces if not (face.bbox == main_face.bbox).all()]

                if len(other_faces) > 0:
                    for face in other_faces:
                        box = face.bbox.astype(int)
                        cv2.rectangle(img=frame, pt1=(box[0], box[1]), pt2=(box[2], box[3]), color=(0, 0, 255), thickness=2)

            # display camera
            tmp_screen = np.array(cv2.resize(frame, dsize=(self.WIDTH, self.HEIGHT), interpolation=cv2.INTER_CUBIC))
            image = cv2.cvtColor(tmp_screen, cv2.COLOR_BGR2RGB)
            q_image = QImage(image.data, self.WIDTH, self.HEIGHT, QImage.Format.Format_RGB888)
            q_pixmap = QPixmap.fromImage(q_image)
            self.label_camera.setPixmap(q_pixmap)


# %%
app = QApplication([])

win = Window()


def f_save():
    # save data to csv file
    formatted_data = [item if isinstance(item, list) else [item] for item in win.col_data]

    # save to csv
    with open(f"result/att_{group.lower().replace(" ", "_")}_{date.today().strftime("%Y_%m_%d")}_{time.strftime("%H_%M_%S")}.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(formatted_data)

    # show message box
    msg = QMessageBox()
    msg.setWindowIcon(QIcon("./logo/pi_logo.png"))
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setText("Data saved successfully")
    msg.setWindowTitle("Success")
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.exec_()


def f_reset():

    global all_dirs_embs

    if group_student_files:
        all_dirs_embs = gen_name_embs(group_student_embs[group])
        win.col_data = list(group_student_files[win.comboBox_group.currentText()].keys())
        win.data_init = list(group_student_files[win.comboBox_group.currentText()].keys())
    else:
        win.col_data = []
        win.data_init = []

    win.data_attd = []

    win.model_init = QStringListModel()
    win.model_init.setStringList(win.data_init)
    win.listView_init.setModel(win.model_init)

    win.model_attd = QStringListModel()
    win.model_attd.setStringList(win.data_attd)
    win.listView_attd.setModel(win.model_attd)


def f_camera_change():
    global cap
    cap.release()
    cap = cv2.VideoCapture(win.comboBox_camera.currentIndex())


win.comboBox_camera.addItems(cameras)
win.comboBox_camera.currentIndexChanged.connect(f_camera_change)


def f_group_change():
    global group, all_dirs_embs

    group = win.comboBox_group.currentText()

    all_dirs_embs = gen_name_embs(group_student_embs[group])

    win.col_data = list(group_student_files[win.comboBox_group.currentText()].keys())
    win.data_init = list(group_student_files[win.comboBox_group.currentText()].keys())
    win.data_attd = []

    win.model_init = QStringListModel()
    win.model_init.setStringList(win.data_init)
    win.listView_init.setModel(win.model_init)
    win.model_attd = QStringListModel()
    win.model_attd.setStringList(win.data_attd)
    win.listView_attd.setModel(win.model_attd)


win.comboBox_group.addItems(list(group_student_files.keys()))
win.comboBox_group.currentIndexChanged.connect(f_group_change)

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

# set version following the file name
win.label_version.setText(f"Version: 1.15")

app.exec()

app.quit()
cap.release()
