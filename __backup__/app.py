#!/usr/bin/env python
# coding: utf-8

# In[1]:


########## __________ ##########
# pyuic5 -x src/gui/026.ui -o src/gui/gui.py

# jupyter nbconvert --to script src/026.ipynb --output app --output-dir=src


# jupyter nbconvert --to script 026.ipynb --output app
########## __________ ##########


# In[2]:


# TODO:
#
# - File edited but database does not update
#


# In[3]:


########## import library ##########
import os
import re
import csv
import cv2
import time
import pickle
import requests

import numpy as np

from datetime import date
from insightface.app import FaceAnalysis

from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtCore import QStringListModel, QTimer, Qt
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication

from github.gui.gui import Ui_MainWindow
########## __________ ##########


# In[4]:


os.environ["QT_SCALE_FACTOR"] = "1"
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"


# In[5]:


########## initial variable ##########
VERSION = "1.26"
MIN_FACE_SIZE = 100  # minimum face size
MAX_NUMBER_FACE = 5

group_name = []  # group name
all_dirs_embs = []  # list of all embeddings
group_student_embs = []  # list of student embeddings
group_student_files = []  # list of student files
group_student_file_sizes = []  # list of student file sizes



# similarity_threshold = pickle.load(open("./resource/similarity_threshold.pkl", "rb"))
if not os.path.exists("./local/similarity_threshold.pkl"):
    similarity_threshold = 0.6
    pickle.dump(similarity_threshold, open("./local/similarity_threshold.pkl", "wb"))
else:
    similarity_threshold = pickle.load(open("./local/similarity_threshold.pkl", "rb"))
########## __________ ##########


# In[6]:


########## define insightface ##########
fa = FaceAnalysis(name="buffalo_sc", root=f"{os.getcwd()}/github", providers=["CPUExecutionProvider"])
fa.prepare(ctx_id=-1, det_thresh=0.5, det_size=(640, 640))
########## __________ ##########


# In[7]:


# utility functions


def get_face_embedding(input):

    faces = fa.get(cv2.imread(input), max_num=MAX_NUMBER_FACE)


    if len(faces) == 0:

        print(f"Warning: no face detected in {input}")

        os.remove(input)

        return None

    elif len(faces) == 1:

        main_face = faces[0]

    elif len(faces) > 1:

        print(f"Warning: {len(faces)} faces detected in {input}")

        main_face = max(faces, key=lambda x: x.bbox[2] - x.bbox[0])


    box = main_face.bbox

    if box[2] - box[0] < MIN_FACE_SIZE or box[3] - box[1] < MIN_FACE_SIZE:

        print(f"Warning: face size is too small in {input}")

        os.remove(input)

        return None
    else:

        return main_face.embedding



def compare_faces_cosine(emb1, emb2):

    similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))

    return similarity



def get_list_folders(input, pattern=None):

    if pattern is not None:

        return [f for f in os.listdir(input) if os.path.isdir(os.path.join(input, f)) and re.search(pattern, f)]
    else:

        return [f for f in os.listdir(input) if os.path.isdir(os.path.join(input, f))]



def get_list_files(input, pattern=None):

    if pattern is None:

        return [f for f in os.listdir(input) if os.path.isfile(os.path.join(input, f))]
    else:

        return [f for f in os.listdir(input) if os.path.isfile(os.path.join(input, f)) and re.search(pattern, f)]



def scan_directory(input):

    data = {}
    for group in get_list_folders(input):

        data[group] = {}

        for student in get_list_folders(f"{input}/{group}"):

            data[group][student] = get_list_files(f"{input}/{group}/{student}", "jpg")
    return data



def get_name_embs(input):

    all_dirs_embs = []
    for n in input:

        tmp = []
        for e in input[n]:
            tmp.append(e)

        all_dirs_embs.append([n, tmp])

    return all_dirs_embs



def get_group_student_embs(input):
    output = {}
    for g in input:
        output[g] = {}
        for s in input[g]:
            output[g][s] = []
            for f in input[g][s]:
                # IMPORTANT: check if the file is in prev_group_student_files
                if group_student_files == [] or (group_student_files.get(g) is None) or (group_student_files[g].get(s) is None) or (f not in group_student_files[g][s]):
                    output[g][s] = [get_face_embedding(f"data/{g}/{s}/{f}")]
                else:
                    output[g][s] = group_student_embs[g][s]
    return output



def get_group_student_file_size(input):

    output = {}
    for g in input:

        output[g] = {}
        for s in input[g]:

            output[g][s] = {}
            for f in input[g][s]:

                output[g][s][f] = os.path.getsize(f"database/{g}/{s}/{f}")
    return output



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

cap = cv2.VideoCapture(0)


# In[8]:


def load_database():
    global group_student_files, group_student_embs

    if os.path.exists("./local/group_student_files.pkl") and os.path.exists("./local/group_student_embs.pkl"):
        group_student_files = pickle.load(open("./local/group_student_files.pkl", "rb"))
        group_student_embs = pickle.load(open("./local/group_student_embs.pkl", "rb"))

    _group_student_files = scan_directory("data")

    if _group_student_files != group_student_files:
        print("Database Updating...")
        _group_student_embs = get_group_student_embs(_group_student_files)
        for g in _group_student_embs:
            for s in _group_student_embs[g]:
                for e in _group_student_embs[g][s]:
                    if e is None:
                        print(f"Warning: database/{g}/{s}/{e} has no face detected")
                        _group_student_embs[g][s] = []
                        _group_student_files[g][s] = []

        group_student_files = _group_student_files
        group_student_embs = _group_student_embs
        pickle.dump(group_student_files, open("./local/group_student_files.pkl", "wb"))
        pickle.dump(group_student_embs, open("./local/group_student_embs.pkl", "wb"))

    else:
        print("Database Loading...")
        group_student_embs = pickle.load(open("./local/group_student_embs.pkl", "rb"))

    print("Database Load Successfully")


load_database()



# if group_student_files has data
if group_student_files:
    group_name = list(group_student_files.keys())[0]
    all_dirs_embs = get_name_embs(group_student_embs[group_name])


# In[9]:


class Window(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Intelligent Systems")
        self.setWindowIcon(QIcon("./github/img/my_logo.png"))
        self.show()

        # setup real-time updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        # self.timer.start(16) # 60 FPS
        self.timer.start(33)  # 30 FPS

        # setup init list view
        if group_student_files:
            self.data_init = list(group_student_files[group_name].keys())
        else:
            self.data_init = []

        self.col_data = self.data_init.copy()
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
        self.SKIP_FRAMES = 10
        self.frame_count = 0

        ########## set ITC's logo ##########
        # set image to win.label_logo_itc
        logo_itc = cv2.imread("./github/img/my_logo.png")
        logo_itc = cv2.cvtColor(logo_itc, cv2.COLOR_BGR2RGB)
        logo_itc = cv2.resize(logo_itc, (self.label_logo.width(), self.label_logo.height()))
        q_logo_itc = QImage(logo_itc.data, logo_itc.shape[1], logo_itc.shape[0], QImage.Format.Format_RGB888)
        q_pixmap_logo_itc = QPixmap.fromImage(q_logo_itc)
        self.label_logo.setPixmap(q_pixmap_logo_itc)
        self.label_logo.setScaledContents(True)
        ########## __________ ##########


    def paintEvent(self, event):
        if cap.isOpened():

            _, frame = cap.read()
            frame = cv2.flip(frame, 1)

            self.frame_count += 1
            if self.frame_count % self.SKIP_FRAMES == 0:
                self.frame_count = 0
                self.faces = fa.get(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), max_num=MAX_NUMBER_FACE)

            # check if insightface detect any faces
            if len(self.faces) > 0:
                # chect for each face in faces
                for face in self.faces:
                    # get face bounding box
                    box = face.bbox.astype(int)

                    # if box is too small, skip it
                    if (box[2] - box[0]) < MIN_FACE_SIZE or (box[3] - box[1]) < MIN_FACE_SIZE:
                        continue

                    # if face is not in the list of faces and not in the list of students
                    if (not all(len(x) == 0 for x in list(group_student_files.keys()))) and (not all(len(x) == 0 for x in list(group_student_files[group_name].values()))):

                        ########## check score for all students ##########
                        score_all = []
                        for name, embs in all_dirs_embs:
                            high_score = 0
                            for emb in embs:
                                sim_score = compare_faces_cosine(face.embedding, emb)
                                if sim_score > high_score:
                                    high_score = sim_score
                            score_all.append(high_score)
                        ########## __________ ##########

                        # for attended faces
                        if np.max(np.array(score_all)) > similarity_threshold:

                            cv2.rectangle(img=frame, pt1=(box[0], box[1]), pt2=(box[2], box[3]), color=(0, 255, 0), thickness=2)
                            cv2.putText(img=frame, text=f"{all_dirs_embs[np.argmax(np.array(score_all))][0]} {100*np.max(np.array(score_all)):.0f}%", org=(box[0], box[1] - 10), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 255, 0), thickness=2)
                            cv2.putText(img=frame, text="Attended", org=(box[0], box[3] + 20), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 255, 0), thickness=2)

                            # update the attendance data and list follow the frame skip
                            if all_dirs_embs[np.argmax(np.array(score_all))][0] not in self.data_attd:

                                self.col_data[np.argmax(np.array(score_all))] = [self.col_data[np.argmax(np.array(score_all))], time.strftime("%H:%M:%S")]
                                self.data_attd.append(all_dirs_embs[np.argmax(np.array(score_all))][0])
                                tmp_data_attd = self.data_attd.copy()
                                tmp_data_attd.reverse()
                                self.model_attd.setStringList(tmp_data_attd)
                                self.listView_attd.setModel(self.model_attd)

                                cv2.imwrite(f"result/log/log_{group_name}_{all_dirs_embs[np.argmax(np.array(score_all))][0]}_{date.today().strftime('%Y_%m_%d')}_{time.strftime('%H_%M_%S')}.jpg", frame)

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


# In[10]:


########## init objects ##########
cap = cv2.VideoCapture(0)
app = QApplication([])
win = Window()
########## __________ ##########


########## design label ##########
win.label_version.setText(f"Version: {VERSION} 🧑‍💻")
win.label_developer.setOpenExternalLinks(True)
win.label_developer.setText("Developer: <a href='https://muysengly.github.io/blog/about/about.html'>MUY Sengly</a> 😊")
########## __________ ##########


########## button save ##########
def f_save():
    # save data to csv file
    if win.data_attd != []:
        tmp_col_data = win.col_data.copy()
        tmp_col_data.insert(0, [f"{date.today().strftime("%Y-%m-%d")}", ""])
        formatted_data = [item if isinstance(item, list) else [item] for item in tmp_col_data]
        with open(f"result/result_{group_name}_{date.today().strftime("%Y_%m_%d")}_{time.strftime("%H_%M_%S")}.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows(formatted_data)

        # show message box
        msg = QMessageBox()
        msg.setWindowTitle("Success")
        msg.setWindowIcon(QIcon("./github/img/my_logo.png"))
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowFlags(msg.windowFlags() | Qt.WindowStaysOnTopHint)
        msg.setText("Data saved successfully.")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec_()
    else:
        msg = QMessageBox()
        msg.setWindowTitle("Warning")
        msg.setWindowIcon(QIcon("./github/img/my_logo.png"))
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowFlags(msg.windowFlags() | Qt.WindowStaysOnTopHint)
        msg.setText("No data to save.")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec_()


win.pushButton_save.clicked.connect(f_save)
########## __________ ##########


########## butten reset ##########
def f_reset():

    win.col_data = win.data_init.copy()
    win.data_attd = []
    win.model_attd = QStringListModel()
    win.model_attd.setStringList(win.data_attd)
    win.listView_attd.setModel(win.model_attd)


win.pushButton_reset.clicked.connect(f_reset)
########## __________ ##########


########## combox camera ##########
def f_camera_change():
    global cap
    cap.release()
    cap = cv2.VideoCapture(win.comboBox_camera.currentIndex())


win.comboBox_camera.addItems(cameras)
win.comboBox_camera.currentIndexChanged.connect(f_camera_change)
########## __________ ##########


########## combobox group ##########
def f_group_change():
    global group_name, all_dirs_embs

    group_name = win.comboBox_group.currentText()
    all_dirs_embs = get_name_embs(group_student_embs[group_name])

    win.data_init = list(group_student_files[win.comboBox_group.currentText()].keys())
    win.model_init = QStringListModel()
    win.model_init.setStringList(win.data_init)
    win.listView_init.setModel(win.model_init)

    win.col_data = win.data_init.copy()
    win.data_attd = []
    win.model_attd = QStringListModel()
    win.model_attd.setStringList(win.data_attd)
    win.listView_attd.setModel(win.model_attd)


win.comboBox_group.addItems(list(group_student_files.keys()))
win.comboBox_group.currentIndexChanged.connect(f_group_change)
########## __________ ##########


########## spinbox threshold ##########
def f_threshold_change():
    global similarity_threshold
    similarity_threshold = win.spinBox_threshold.value() / 100
    pickle.dump(similarity_threshold, open("./local/similarity_threshold.pkl", "wb"))


win.spinBox_threshold.setValue(int(similarity_threshold * 100))
win.spinBox_threshold.valueChanged.connect(f_threshold_change)
########## __________ ##########


########## __________ ##########
def f_take_picture():

    global all_dirs_embs

    selected = win.listView_init.selectedIndexes()
    if selected:
        selected_name = selected[0].data()

        _, _frame = cap.read()
        _frame = cv2.flip(_frame, 1)

        # show message box
        msg = QMessageBox()
        msg.setWindowIcon(QIcon("./github/img/my_logo.png"))
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowFlags(msg.windowFlags() | Qt.WindowStaysOnTopHint)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.Yes)
        _frame = cv2.resize(_frame, dsize=(640, 480))
        _frame = cv2.cvtColor(_frame, cv2.COLOR_BGR2RGB)
        q_image = QImage(_frame.data, _frame.shape[1], _frame.shape[0], QImage.Format.Format_RGB888)
        q_pixmap = QPixmap.fromImage(q_image)
        msg.setIconPixmap(q_pixmap)
        msg.setWindowTitle(f"Do you want to save the image for {selected_name}?")

        if msg.exec_() == QMessageBox.StandardButton.Yes:
            _frame = cv2.cvtColor(_frame, cv2.COLOR_RGB2BGR)
            cv2.imwrite(f"data/{group_name}/{selected_name}/data_{date.today().strftime('%Y_%m_%d')}_{time.strftime('%H_%M_%S')}.jpg", _frame)
            load_database()
            if group_student_files:
                all_dirs_embs = get_name_embs(group_student_embs[group_name])
        else:
            pass


win.pushButton_capture.clicked.connect(f_take_picture)
########## __________ ##########


########## __________ ##########
def f_update():

    # condition for no internet connection
    try:
        app_url = requests.get("https://raw.githubusercontent.com/muysengly/repo_attendance_system/main/app.py")
        app_text = app_url.text
        gui_url = requests.get("https://raw.githubusercontent.com/muysengly/repo_attendance_system/main/gui.py")
        gui_text = gui_url.text
    except requests.exceptions.RequestException as e:
        msg = QMessageBox()
        msg.setWindowTitle("Error")
        msg.setWindowIcon(QIcon("./github/img/my_logo.png"))
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowFlags(msg.windowFlags() | Qt.WindowStaysOnTopHint)
        msg.setText("Failed to fetch update files. \nPlease check your internet connection.")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec_()
        return

    pattern = r'version = "(\d+\.\d+)"'
    match = re.search(pattern, app_text)
    git_version = match.group(1)
    print(git_version)

    curr_text = open("app.py", "r", encoding="utf-8").read()
    pattern = r'version = "(\d+\.\d+)"'
    match = re.search(pattern, curr_text)
    my_version = match.group(1)
    print(my_version)

    if git_version != my_version:
        msg = QMessageBox()
        msg.setWindowTitle("Update")
        msg.setWindowIcon(QIcon("./resource/my_logo.png"))
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowFlags(msg.windowFlags() | Qt.WindowStaysOnTopHint)
        _text = f"New version available:\nCurrent version: {my_version}\nNew version: {git_version}\n\nDo you want to update?"
        msg.setText(_text)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.Yes)
        if msg.exec_() == QMessageBox.StandardButton.Yes:
            with open("app.py", "w", encoding="utf-8") as file:
                file.write(app_text)
            with open("gui.py", "w", encoding="utf-8") as file:
                file.write(gui_text)
            msg = QMessageBox()
            msg.setWindowTitle("Update")
            msg.setWindowIcon(QIcon("./resource/my_logo.png"))
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowFlags(msg.windowFlags() | Qt.WindowStaysOnTopHint)
            msg.setText("Update successfully.\nPlease restart the program.")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec_()
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Update")
            msg.setWindowIcon(QIcon("./resource/my_logo.png"))
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowFlags(msg.windowFlags() | Qt.WindowStaysOnTopHint)
            msg.setText("Update cancelled.")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec_()
    else:
        msg = QMessageBox()
        msg.setWindowTitle("Update")
        msg.setWindowIcon(QIcon("./resource/my_logo.png"))
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowFlags(msg.windowFlags() | Qt.WindowStaysOnTopHint)
        msg.setText("You are using the latest version.")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec_()


win.pushButton_update.clicked.connect(f_update)
########## __________ ##########


########## run program ##########
app.exec()
########## __________ ##########


########## auto save ##########

########## __________ ##########


########## end objects for rerun ##########
app.quit()
cap.release()
win = None
app = None
########## __________ ##########

