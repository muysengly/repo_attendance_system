# %%
import os
import re
import time
import csv
import cv2
import json
import pickle
import subprocess
import numpy as np
from PIL import Image
from pillow_heif import open_heif
from pprint import pprint
from datetime import date

import insightface
from insightface.app import FaceAnalysis

from PyQt5.QtCore import QStringListModel, QTimer
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication
from PyQt5.QtGui import QImage, QPixmap, QIcon


os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_SCALE_FACTOR"] = "1"


os.system("pyuic5 -x 020.ui -o gui.py")
from gui import Ui_MainWindow

# %%
fa = FaceAnalysis(name="buffalo_sc", root=os.getcwd(), providers=["CPUExecutionProvider"])
fa.prepare(ctx_id=-1, det_thresh=0.5, det_size=(640, 640))

# %%
# NOTE: this is all the functions that are used in the main program


def scan_files(input):
    """
    This function scans all files in a directory and returns a list of all files.

    Parameters:
        input (str): The path to the directory.

    Returns:
        list: A list of all files in the directory.

    Example:
        >>> scan_files("data")
        ['data/1.jpg', 'data/2.jpg', 'data/3.jpg']
    """
    files = []
    for root, dirs, file in os.walk(input):
        for f in file:
            files.append(os.path.join(root, f))
    return files


def convert_heic_to_jpg(input, output):
    """
    This function converts HEIC images to JPEG images.

    Parameters:
        input (str): The path to the HEIC image.
        output (str): The path to the JPEG image.

    Returns:
        None

    Example:
        >>> convert_heic_to_jpg("data/image.heic", "data/image.jpg")
    """

    heif_image = open_heif(input)
    image = Image.frombytes(heif_image.mode, heif_image.size, heif_image.data)
    image.save(output, format="JPEG")


def convert_png_to_jpg(input, output):
    img = cv2.imread(input)
    cv2.imwrite(output, img)


def convert_jpeg_to_jpg(input, output):
    img = cv2.imread(input)
    cv2.imwrite(output, img)


def get_face_embedding(input):
    faces = fa.get(cv2.imread(input))
    if len(faces) == 0:
        os.remove(input)
        return None
    elif len(faces) == 1:
        main_face = faces[0]
    elif len(faces) > 1:
        print(f"Warning: {len(faces)} faces detected in {input}")
        main_face = max(faces, key=lambda x: x.bbox[2] - x.bbox[0])
    return main_face.embedding


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

    # if len(cameras) == 0:
    #     # show error message using pyqt5
    #     tmp_app = QApplication([])
    #     msg = QMessageBox()
    #     msg.setIcon(QMessageBox.Critical)
    #     msg.setText("No camera devices found")
    #     msg.setWindowTitle("Error")
    #     msg.exec_()
    #     tmp_app.quit()

    return cameras


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


def convert_all_to_jpg():
    tmp_files = scan_files("data")

    for file in tmp_files:
        if file.endswith(".jpg"):
            # cv2.imwrite(file, cv2.imread(file), [int(cv2.IMWRITE_JPEG_QUALITY), 60])
            pass
        elif file.endswith(".heic"):
            convert_heic_to_jpg(file, file.replace(".heic", ".jpg"))
            os.remove(file)
        elif file.endswith(".HEIC"):
            convert_heic_to_jpg(file, file.replace(".HEIC", ".jpg"))
            os.remove(file)
        elif file.endswith(".png"):
            convert_png_to_jpg(file, file.replace(".png", ".jpg"))
            os.remove(file)
        elif file.endswith(".PNG"):
            convert_png_to_jpg(file, file.replace(".PNG", ".jpg"))
            os.remove(file)
        elif file.endswith(".jpeg"):
            convert_jpeg_to_jpg(file, file.replace(".jpeg", ".jpg"))
            os.remove(file)
        elif file.endswith(".JPEG"):
            convert_jpeg_to_jpg(file, file.replace(".JPEG", ".jpg"))
            os.remove(file)
        elif file.endswith(".JPG"):
            os.rename(file, file.replace(".JPG", ".jpg"))
        elif file.endswith(".ini"):
            os.remove(file)
        else:
            print(file)


convert_all_to_jpg()

# %%
# reload and resave if group_student_files and group_student_embs are updated


group_student_files = pickle.load(open("group_student_files.pkl", "rb"))
current_group_student_files = scan_directory("data")

if current_group_student_files != group_student_files:
    print("Database Updating...")
    group_student_embs = gen_group_student_embs(current_group_student_files)
    for g in group_student_embs:
        for s in group_student_embs[g]:
            for e in group_student_embs[g][s]:
                if e is None:
                    print(f"Warning: data/{g}/{s}/{e} has no face detected")
                    group_student_embs[g][s] = []
                    current_group_student_files[g][s] = []

    group_student_files = current_group_student_files
    pickle.dump(group_student_files, open("group_student_files.pkl", "wb"))
    pickle.dump(group_student_embs, open("group_student_embs.pkl", "wb"))

else:
    print("Database Loading...")
    group_student_embs = pickle.load(open("group_student_embs.pkl", "rb"))


# %%
if group_student_files:
    group = list(group_student_files.keys())[0]

if group_student_files:
    all_dirs_embs = gen_name_embs(group_student_embs[group])

cameras = list_camera_devices()

cap = cv2.VideoCapture(0)

THRESHOLD = 0.60


# %%
class Window(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Attendance System")
        self.setWindowIcon(QIcon("./logo/mu_logo.png"))
        self.show()

        # setup real-time updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        # self.timer.start(16) # 60 FPS
        self.timer.start(33)  # 30 FPS

        # setup init list view
        if group_student_files:
            self.col_data = list(group_student_files[group].keys())
            self.data_init = list(group_student_files[group].keys())
        else:
            self.col_data = []
            self.data_init = []
        self.model_init = QStringListModel()
        self.model_init.setStringList(self.data_init)
        self.listView_init.setModel(self.model_init)

        # setup attd list view
        self.data_attd = []
        self.model_attd = QStringListModel()
        self.model_attd.setStringList(self.data_attd)
        self.listView_attd.setModel(self.model_attd)

        # setup label camera
        self.WIDTH = self.label_camera.width()
        self.HEIGHT = self.label_camera.height()

        # setup frame skip
        self.faces = []
        self.frame_count = self.SKIP_FRAMES = 10

    def paintEvent(self, event):
        if cap.isOpened():

            _, frame = cap.read()

            if self.frame_count == self.SKIP_FRAMES:
                self.frame_count = 0
                self.faces = fa.get(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            self.frame_count += 1

            if len(self.faces) > 0:
                for face in self.faces:

                    box = face.bbox.astype(int)

                    if (not all(len(x) == 0 for x in list(group_student_files.keys()))) and (not all(len(x) == 0 for x in list(group_student_files[group].values()))):

                        # score for all names
                        score_all = []

                        for name, embs in all_dirs_embs:
                            high_score = 0
                            for emb in embs:
                                sim_score = compare_faces_cosine(face.embedding, emb)
                                if sim_score > high_score:
                                    high_score = sim_score
                            score_all.append(high_score)

                        if np.max(np.array(score_all)) > THRESHOLD:

                            cv2.rectangle(img=frame, pt1=(box[0], box[1]), pt2=(box[2], box[3]), color=(0, 255, 0), thickness=2)
                            cv2.putText(img=frame, text=f"{all_dirs_embs[np.argmax(np.array(score_all))][0]} {100*np.max(np.array(score_all)):.0f}%", org=(box[0], box[1] - 10), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 255, 0), thickness=2)
                            cv2.putText(img=frame, text="Attended", org=(box[0], box[3] + 20), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 255, 0), thickness=2)

                            # attendant data
                            if all_dirs_embs[np.argmax(np.array(score_all))][0] not in self.data_attd:
                                self.col_data[np.argmax(np.array(score_all))] = [self.col_data[np.argmax(np.array(score_all))], time.strftime("%H:%M:%S")]
                                self.data_attd.append(all_dirs_embs[np.argmax(np.array(score_all))][0])
                                tmp_data_attd = self.data_attd.copy()
                                tmp_data_attd.reverse()
                                self.model_attd.setStringList(tmp_data_attd)
                                self.listView_attd.setModel(self.model_attd)

                                self.data_init.pop(np.argmax(np.array(score_all)))
                                self.model_init.setStringList(self.data_init)
                                self.listView_init.setModel(self.model_init)

                                # read new frame
                                _, tmp_frame = cap.read()

                                # put box and text on image
                                cv2.rectangle(
                                    img=tmp_frame,
                                    pt1=(box[0] - 10, box[1] - 10),
                                    pt2=(box[2] + 10, box[3] + 10),
                                    color=(0, 255, 0),
                                    thickness=2,
                                )
                                cv2.putText(
                                    img=tmp_frame,
                                    text=f"{all_dirs_embs[np.argmax(np.array(score_all))][0]} {100*np.max(np.array(score_all)):.0f}%",
                                    org=(box[0], box[1] - 20),
                                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                    fontScale=0.5,
                                    color=(0, 255, 0),
                                    thickness=2,
                                )

                                # save image with name
                                cv2.imwrite(f"log/log_{group}_{all_dirs_embs[np.argmax(np.array(score_all))][0]}_{date.today().strftime('%Y_%m_%d')}_{time.strftime('%H_%M_%S')}.jpg", tmp_frame)
                        else:
                            cv2.rectangle(img=frame, pt1=(box[0], box[1]), pt2=(box[2], box[3]), color=(0, 0, 255), thickness=2)
                            cv2.putText(img=frame, text=f"{all_dirs_embs[np.argmax(np.array(score_all))][0]} {100*np.max(np.array(score_all)):.0f}%", org=(box[0], box[1] - 10), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 0, 255), thickness=2)
                            cv2.putText(img=frame, text="Unknown", org=(box[0], box[3] + 20), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 0, 255), thickness=2)

                    # for unknown faces
                    else:
                        cv2.rectangle(img=frame, pt1=(box[0], box[1]), pt2=(box[2], box[3]), color=(0, 0, 255), thickness=2)
                        cv2.putText(img=frame, text="No Data", org=(box[0], box[1] - 10), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 0, 255), thickness=2)
                        cv2.putText(img=frame, text="Unknown", org=(box[0], box[3] + 20), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 0, 255), thickness=2)

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

    if (not all(len(x) == 0 for x in list(group_student_files.keys()))) and (not all(len(x) == 0 for x in list(group_student_files[group].values()))):

        formatted_data = [item if isinstance(item, list) else [item] for item in win.col_data]

        # save to csv
        with open(f"result/result_{group}_{date.today().strftime("%Y_%m_%d")}_{time.strftime("%H_%M_%S")}.csv", "w", newline="", encoding="utf-8") as file:
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
    else:
        msg = QMessageBox()
        msg.setWindowIcon(QIcon("./logo/pi_logo.png"))
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText("No data to save")
        msg.setWindowTitle("Warning")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec_()


win.pushButton_save.clicked.connect(f_save)


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


win.pushButton_reset.clicked.connect(f_reset)


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


def f_threshold_change():
    global THRESHOLD
    THRESHOLD = win.spinBox_threshold.value() / 100


win.spinBox_threshold.setValue(int(THRESHOLD * 100))
win.spinBox_threshold.valueChanged.connect(f_threshold_change)


win.label_developer.setOpenExternalLinks(True)
win.label_developer.setText("Developer: <a href='https://muysengly.github.io/blog/about/about.html'>MUY Sengly</a> 😊")


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
win.label_version.setText(f"Version: 1.20 🧑‍💻")

app.exec()

app.quit()
cap.release()
