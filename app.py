# %%
########## import library ##########
import os
import re
import time
import csv
import cv2
import pickle
import numpy as np

from datetime import date
from insightface.app import FaceAnalysis

from PyQt5.QtCore import QStringListModel, QTimer, Qt
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication
from PyQt5.QtGui import QImage, QPixmap, QIcon

from resource.gui import Ui_MainWindow

########## __________ ##########


########## __________ ##########
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_SCALE_FACTOR"] = "1"
########## __________ ##########


########## __________ ##########
# pyuic5 -x ./resource/022.ui -o ./resource/gui.py
# os.system("pyuic5 -x ./resource/022.ui -o ./resource/gui.py")
########## __________ ##########


########## compile file ##########
# import py_compile

# py_compile.compile("app.py", cfile="app.pyc")
# py_compile.compile("resource/gui.py", cfile="resource/gui.pyc")
########## __________ ##########


# %%
########## initial variable ##########

version = "1.23"

group_student_files = []  # list of student files
group_student_embs = []  # list of student embeddings
all_dirs_embs = []  # list of all embeddings
group_name = []  # group name

similarity_threshold = pickle.load(open("./resource/similarity_threshold.pkl", "rb"))
number_of_faces_maximum = 5
########## __________ ##########


# %%
########## define insightface ##########
fa = FaceAnalysis(name="buffalo_sc", root=os.getcwd(), providers=["CPUExecutionProvider"])
fa.prepare(ctx_id=-1, det_thresh=0.5, det_size=(640, 640))
########## __________ ##########


# %%
def get_face_embedding(input):
    faces = fa.get(cv2.imread(input), max_num=number_of_faces_maximum)
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
                # IMPORTANT: check if the file is in prev_group_student_files
                if (group_student_files.get(g) is None) or (group_student_files[g].get(s) is None) or (f not in group_student_files[g][s]):
                    group_student_embs[g][s] = [get_face_embedding(f"database/{g}/{s}/{f}")]
                else:
                    group_student_embs[g][s] = group_student_embs[g][s]
    return group_student_embs


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


cameras = list_camera_devices()
cap = cv2.VideoCapture(0)


# NOTE: need to fix because it load all data every time
def load_database():

    global group_student_files, group_student_embs

    group_student_files = pickle.load(open("resource/group_student_files.pkl", "rb"))
    group_student_embs = pickle.load(open("resource/group_student_embs.pkl", "rb"))
    _group_student_files = scan_directory("database")

    if _group_student_files != group_student_files:
        print("Database Updating...")
        _group_student_embs = gen_group_student_embs(_group_student_files)
        for g in _group_student_embs:
            for s in _group_student_embs[g]:
                for e in _group_student_embs[g][s]:
                    if e is None:
                        print(f"Warning: database/{g}/{s}/{e} has no face detected")
                        _group_student_embs[g][s] = []
                        _group_student_files[g][s] = []

        group_student_files = _group_student_files
        group_student_embs = _group_student_embs
        pickle.dump(group_student_files, open("resource/group_student_files.pkl", "wb"))
        pickle.dump(group_student_embs, open("resource/group_student_embs.pkl", "wb"))

    else:
        print("Database Loading...")
        group_student_embs = pickle.load(open("resource/group_student_embs.pkl", "rb"))

    print("Database Load Successfully")


load_database()

# if group_student_files has data
if group_student_files:
    group_name = list(group_student_files.keys())[0]
    all_dirs_embs = gen_name_embs(group_student_embs[group_name])


# %%
class Window(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Attendance System")
        self.setWindowIcon(QIcon("./resource/mu_logo.png"))
        self.show()

        # setup real-time updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        # self.timer.start(16) # 60 FPS
        self.timer.start(33)  # 30 FPS

        # setup init list view
        if group_student_files:
            self.col_data = list(group_student_files[group_name].keys())
            self.data_init = list(group_student_files[group_name].keys())
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
        self.SKIP_FRAMES = 10
        self.frame_count = 0

        ########## set ITC's logo ##########
        # set image to win.label_logo_itc
        logo_itc = cv2.imread("./resource/itc_logo.png")
        logo_itc = cv2.cvtColor(logo_itc, cv2.COLOR_BGR2RGB)
        logo_itc = cv2.resize(logo_itc, (self.label_logo_itc.width(), self.label_logo_itc.height()))
        q_logo_itc = QImage(logo_itc.data, logo_itc.shape[1], logo_itc.shape[0], QImage.Format.Format_RGB888)
        q_pixmap_logo_itc = QPixmap.fromImage(q_logo_itc)
        self.label_logo_itc.setPixmap(q_pixmap_logo_itc)
        self.label_logo_itc.setScaledContents(True)
        ########## __________ ##########

        ########## set GTR's logo ##########
        # set image to win.label_logo_gtr
        logo_gtr = cv2.imread("./resource/gtr_logo.png")
        logo_gtr = cv2.cvtColor(logo_gtr, cv2.COLOR_BGR2RGB)
        logo_gtr = cv2.resize(logo_gtr, (self.label_logo_gtr.width(), self.label_logo_gtr.height()))
        q_logo_gtr = QImage(logo_gtr.data, logo_gtr.shape[1], logo_gtr.shape[0], QImage.Format.Format_RGB888)
        q_pixmap_logo_gtr = QPixmap.fromImage(q_logo_gtr)
        self.label_logo_gtr.setPixmap(q_pixmap_logo_gtr)
        self.label_logo_gtr.setScaledContents(True)
        ########## __________ ##########

    def paintEvent(self, event):
        if cap.isOpened():

            _, frame = cap.read()
            frame = cv2.flip(frame, 1)

            self.frame_count += 1
            if self.frame_count % self.SKIP_FRAMES == 0:
                self.frame_count = 0
                self.faces = fa.get(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), max_num=number_of_faces_maximum)

            # check if insightface detect any faces
            if len(self.faces) > 0:
                # chect for each face in faces
                for face in self.faces:
                    # get face bounding box
                    box = face.bbox.astype(int)

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
                            if (all_dirs_embs[np.argmax(np.array(score_all))][0] not in self.data_attd) and (self.frame_count % self.SKIP_FRAMES == 0):

                                self.col_data[np.argmax(np.array(score_all))] = [self.col_data[np.argmax(np.array(score_all))], time.strftime("%H:%M:%S")]
                                self.data_attd.append(all_dirs_embs[np.argmax(np.array(score_all))][0])
                                tmp_data_attd = self.data_attd.copy()
                                tmp_data_attd.reverse()
                                self.model_attd.setStringList(tmp_data_attd)
                                self.listView_attd.setModel(self.model_attd)

                                if len(self.data_init) == 1:  # if only one student in the list
                                    self.data_init = []
                                else:  # if more than one student in the list
                                    self.data_init.pop(np.argmax(np.array(score_all)))
                                self.model_init.setStringList(self.data_init)
                                self.listView_init.setModel(self.model_init)

                                ########## save log file ##########
                                # read new frame
                                _, tmp_frame = cap.read()
                                frame = cv2.flip(frame, 1)

                                # put box and text on image
                                cv2.rectangle(img=tmp_frame, pt1=(box[0] - 10, box[1] - 10), pt2=(box[2] + 10, box[3] + 10), color=(0, 255, 0), thickness=2)
                                cv2.putText(img=tmp_frame, text=f"{all_dirs_embs[np.argmax(np.array(score_all))][0]} {100*np.max(np.array(score_all)):.0f}%", org=(box[0], box[1] - 20), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=(0, 255, 0), thickness=2)

                                # save image with name
                                cv2.imwrite(f"log/log_{group_name}_{all_dirs_embs[np.argmax(np.array(score_all))][0]}_{date.today().strftime('%Y_%m_%d')}_{time.strftime('%H_%M_%S')}.jpg", tmp_frame)
                                ########## __________ ##########
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
########## init objects ##########
cap = cv2.VideoCapture(0)
app = QApplication([])
win = Window()
########## __________ ##########


########## design label ##########
win.label_version.setText(f"Version: {version} 🧑‍💻")
win.label_developer.setOpenExternalLinks(True)
win.label_developer.setText("Developer: <a href='https://muysengly.github.io/blog/about/about.html'>MUY Sengly</a> 😊")
########## __________ ##########


########## button save ##########
def f_save():
    # save data to csv file
    if (not all(len(x) == 0 for x in list(group_student_files.keys()))) and (not all(len(x) == 0 for x in list(group_student_files[group_name].values()))):

        tmp_col_data = win.col_data.copy()
        tmp_col_data.insert(0, [f"{date.today().strftime("%Y-%m-%d")}", ""])

        formatted_data = [item if isinstance(item, list) else [item] for item in tmp_col_data]

        # save to csv
        with open(f"result/result_{group_name}_{date.today().strftime("%Y_%m_%d")}_{time.strftime("%H_%M_%S")}.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows(formatted_data)

        # show message box
        msg = QMessageBox()
        msg.setWindowTitle("Success")
        msg.setWindowIcon(QIcon("./resource/mu_logo.png"))
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowFlags(msg.windowFlags() | Qt.WindowStaysOnTopHint)
        msg.setText("Data saved successfully.")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec_()
    else:
        msg = QMessageBox()
        msg.setWindowTitle("Warning")
        msg.setWindowIcon(QIcon("./resource/mu_logo.png"))
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowFlags(msg.windowFlags() | Qt.WindowStaysOnTopHint)
        msg.setText("No data to save.")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec_()


win.pushButton_save.clicked.connect(f_save)
########## __________ ##########


########## butten reset ##########
def f_reset():

    global all_dirs_embs

    if group_student_files:
        all_dirs_embs = gen_name_embs(group_student_embs[group_name])
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
    all_dirs_embs = gen_name_embs(group_student_embs[group_name])

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
########## __________ ##########


########## spinbox threshold ##########
def f_threshold_change():
    global similarity_threshold
    similarity_threshold = win.spinBox_threshold.value() / 100
    pickle.dump(similarity_threshold, open("resource/similarity_threshold.pkl", "wb"))


win.spinBox_threshold.setValue(int(similarity_threshold * 100))
win.spinBox_threshold.valueChanged.connect(f_threshold_change)
########## __________ ##########


########## __________ ##########
def f_capture():

    selected = win.listView_init.selectedIndexes()
    if selected:
        selected_name = selected[0].data()
        _, tmp_frame = cap.read()
        frame = cv2.flip(frame, 1)

        # show message box
        msg = QMessageBox()
        # msg.setWindowTitle("Success")
        msg.setWindowIcon(QIcon("./resource/mu_logo.png"))
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowFlags(msg.windowFlags() | Qt.WindowStaysOnTopHint)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.Yes)

        # set image to msg
        tmp_frame = cv2.resize(tmp_frame, dsize=(640, 480))
        tmp_frame = cv2.cvtColor(tmp_frame, cv2.COLOR_BGR2RGB)
        q_image = QImage(tmp_frame.data, tmp_frame.shape[1], tmp_frame.shape[0], QImage.Format.Format_RGB888)
        q_pixmap = QPixmap.fromImage(q_image)
        msg.setIconPixmap(q_pixmap)

        msg.setWindowTitle(f"Do you want to save the image for {selected_name}?")

        if msg.exec_() == QMessageBox.StandardButton.Yes:
            _, tmp_frame = cap.read()
            frame = cv2.flip(frame, 1)
            cv2.imwrite(f"database/{group_name}/{selected_name}/data_{date.today().strftime('%Y_%m_%d')}_{time.strftime('%H_%M_%S')}.jpg", tmp_frame)
            load_database()
        else:
            pass


win.pushButton_capture.clicked.connect(f_capture)
########## __________ ##########


########## run program ##########
app.exec()
########## __________ ##########

########## auto save ##########
if (not all(len(x) == 0 for x in list(group_student_files.keys()))) and (not all(len(x) == 0 for x in list(group_student_files[group_name].values()))):

    tmp_col_data = win.col_data.copy()
    tmp_col_data.insert(0, [f"{date.today().strftime("%Y-%m-%d")}", ""])

    formatted_data = [item if isinstance(item, list) else [item] for item in tmp_col_data]

    # save to csv
    with open(f"result/result_{group_name}_{date.today().strftime("%Y_%m_%d")}_{time.strftime("%H_%M_%S")}.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(formatted_data)
########## __________ ##########


########## end objects for rerun ##########
app.quit()
cap.release()
win = None
app = None
########## __________ ##########
