#!/usr/bin/env python
# coding: utf-8

# In[1]:


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


# In[3]:


from insightface.app import FaceAnalysis  # NOTE: this library need to import first

from View import Ui_MainWindow

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import cv2
import glob
import pickle

import numpy as np


# In[4]:


fa = FaceAnalysis(name="buffalo_sc", root=f"{os.getcwd()}/{path_depth}resource/utility/", providers=["CPUExecutionProvider"])
fa.prepare(ctx_id=-1, det_thresh=0.5, det_size=(640, 640))


# In[5]:


# group_paths = glob.glob(os.path.join(path_depth + "resource/database/", "*.pkl"))
# group_names = [name.split("\\")[-1][:-4] for name in group_paths]


# pickle.dump("001 SCIENTIFIC DAY", open(path_depth + "resource/variable/_group_name.pkl", "wb"))
group_name = pickle.load(open(path_depth + "resource/variable/_group_name.pkl", "rb"))
# group_name


# In[6]:


database = pickle.load(open(path_depth + "resource/database/" + group_name + ".pkl", "rb"))
# database


# In[7]:


class Window(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QIcon(f"{path_depth}resource/asset/itc_logo.png"))
        self.setWindowTitle("Face Management Form")

        self.listView_name.setModel(QStringListModel([row[0] for row in database]))

        self.label_group_name.setText('Manage Faces in "' + group_name + '"')

        self.show()


# In[8]:


app = QApplication([])
win = Window()

_name = ""


def on_button_add_clicked():

    global database

    text = win.lineEdit_name.text()
    if text:
        win.listView_name.model().insertRow(win.listView_name.model().rowCount())
        index = win.listView_name.model().index(win.listView_name.model().rowCount() - 1)
        win.listView_name.model().setData(index, text)
        print(f"Added: {text}")

        database.append([text, [None, None], [None, None]])

    print("Add button clicked")

    win.lineEdit_name.clear()
    win.lineEdit_name.setFocus()
    pickle.dump(database, open(path_depth + "resource/database/" + group_name + ".pkl", "wb"))


win.pushButton_add.clicked.connect(on_button_add_clicked)
win.lineEdit_name.returnPressed.connect(on_button_add_clicked)

add_icon = QIcon(f"{path_depth}resource/asset/add_person.png")
win.pushButton_add.setIcon(add_icon)


def on_listview_double_clicked():
    global _name
    if win.listView_name.selectedIndexes():
        seleted = win.listView_name.selectedIndexes()[0]
        _name = seleted.data()
        print(f"{seleted.row()} : {seleted.data()}")


win.listView_name.doubleClicked.connect(on_listview_double_clicked)


def on_data_changed():
    global database
    if win.listView_name.selectedIndexes():
        selected = win.listView_name.selectedIndexes()[0]
        if selected.data() == "":
            # print("Deleted" + _name)
            win.listView_name.model().removeRow(selected.row())
            database.pop(selected.row())

        elif selected.data() != _name:
            win.listView_name.model().setData(selected, selected.data())
            # print(_name + " --> " + selected.data())

            database[selected.row()][0] = selected.data()


    pickle.dump(database, open(path_depth + "resource/database/" + group_name + ".pkl", "wb"))


win.listView_name.model().dataChanged.connect(on_data_changed)


def context_menu_event_name(point):
    if win.listView_name.selectedIndexes():
        index = win.listView_name.indexAt(point)
        if index.isValid():
            menu = QMenu()
            delete_icon = QIcon(f"{path_depth}resource/asset/delete.png")
            delete_action = menu.addAction(delete_icon, "Delete")
            action = menu.exec_(win.listView_name.mapToGlobal(point))
            if action == delete_action:
                name = index.data()
                win.listView_name.model().removeRow(index.row())
                database.pop(index.row())
                pickle.dump(database, open(path_depth + "resource/database/" + group_name + ".pkl", "wb"))
                # print(f"Deleted: {name}")
                if len(database) == 0: # if no data in database
                    win.label_image_1.clear()
                    win.label_image_2.clear()
                    win.label_image_1.setText("No Image #1")
                    win.label_image_2.setText("No Image #2")


win.listView_name.setContextMenuPolicy(Qt.CustomContextMenu)
win.listView_name.customContextMenuRequested.connect(context_menu_event_name)


def on_button_upload_image_1_clicked():

    if win.listView_name.selectedIndexes():
        selected = win.listView_name.selectedIndexes()[0]

        file_name, _ = QFileDialog.getOpenFileName(win, "Open Image File", "", "Images (*.jpg)")
        if file_name:

            image = np.array(cv2.imread(file_name))
            faces = fa.get(image)

            if len(faces) == 1:
                face = faces[0]
                box = face.bbox.astype(int)
                if (box[2] - box[0]) > 160 or (box[3] - box[1]) > 160:

                    database[selected.row()][1][0] = image
                    database[selected.row()][1][1] = faces[0].embedding
                    pickle.dump(database, open(path_depth + "resource/database/" + group_name + ".pkl", "wb"))

                    _image = cv2.resize(image, (win.label_image_1.width(), win.label_image_1.height()))
                    q_pixmap = QPixmap.fromImage(QImage(cv2.cvtColor(_image, cv2.COLOR_BGR2RGB).data, _image.shape[1], _image.shape[0], QImage.Format.Format_RGB888))
                    win.label_image_1.setPixmap(q_pixmap)
                else:
                    msg = QMessageBox(win)
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("Face is too small!")
                    msg.setWindowTitle("Database Error")
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.exec_()

            elif len(faces) == 0:

                msg = QMessageBox(win)
                msg.setIcon(QMessageBox.Critical)
                msg.setText("No face detected!")
                msg.setWindowTitle("Database Error")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()

            else:
                msg = QMessageBox(win)
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Too many faces detected!")
                msg.setWindowTitle("Database Error")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()


win.pushButton_upload_image_1.clicked.connect(on_button_upload_image_1_clicked)


def on_button_upload_image_2_clicked():
    if win.listView_name.selectedIndexes():
        selected = win.listView_name.selectedIndexes()[0]

        file_name, _ = QFileDialog.getOpenFileName(win, "Open Image File", "", "Images (*.jpg)")
        if file_name:

            image = np.array(cv2.imread(file_name))
            faces = fa.get(image)
            if len(faces) == 1:

                face = faces[0]
                box = face.bbox.astype(int)
                if (box[2] - box[0]) > 160 or (box[3] - box[1]) > 160:

                    database[selected.row()][2][0] = image
                    database[selected.row()][2][1] = faces[0].embedding
                    pickle.dump(database, open(path_depth + "resource/database/" + group_name + ".pkl", "wb"))

                    _image = cv2.resize(image, (win.label_image_2.width(), win.label_image_2.height()))
                    q_pixmap = QPixmap.fromImage(QImage(cv2.cvtColor(_image, cv2.COLOR_BGR2RGB).data, _image.shape[1], _image.shape[0], QImage.Format.Format_RGB888))
                    win.label_image_2.setPixmap(q_pixmap)

                else:
                    msg = QMessageBox(win)
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("Face is too small!")
                    msg.setWindowTitle("Database Error")
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.exec_()

            elif len(faces) == 0:
                msg = QMessageBox(win)
                msg.setIcon(QMessageBox.Critical)
                msg.setText("No face detected!")
                msg.setWindowTitle("Database Error")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()

            else:
                msg = QMessageBox(win)
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Too many faces detected!")
                msg.setWindowTitle("Database Error")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()


win.pushButton_upload_image_2.clicked.connect(on_button_upload_image_2_clicked)


def on_listview_single_clicked():
    if win.listView_name.selectedIndexes():
        selected = win.listView_name.selectedIndexes()[0]

        if database[selected.row()][1][0] is not None and len(database[selected.row()][1][0]) > 0:
            image = database[selected.row()][1][0]
            _image = cv2.resize(image, (win.label_image_1.width(), win.label_image_1.height()))
            q_pixmap = QPixmap.fromImage(QImage(cv2.cvtColor(_image, cv2.COLOR_BGR2RGB).data, _image.shape[1], _image.shape[0], QImage.Format.Format_RGB888))
            win.label_image_1.setPixmap(q_pixmap)

        else:
            win.label_image_1.clear()
            win.label_image_1.setText("No Image #1")

        if database[selected.row()][2][0] is not None and len(database[selected.row()][2][0]) > 0:
            image = database[selected.row()][2][0]
            _image = cv2.resize(image, (win.label_image_2.width(), win.label_image_2.height()))
            q_pixmap = QPixmap.fromImage(QImage(cv2.cvtColor(_image, cv2.COLOR_BGR2RGB).data, _image.shape[1], _image.shape[0], QImage.Format.Format_RGB888))
            win.label_image_2.setPixmap(q_pixmap)
        else:
            win.label_image_2.clear()
            win.label_image_2.setText("No Image #2")


win.listView_name.selectionModel().selectionChanged.connect(on_listview_single_clicked)


def on_button_take_photo_1_clicked():

    if win.listView_name.selectedIndexes():
        selected = win.listView_name.selectedIndexes()[0]
        win.hide()
        os.system("python " + path_depth + "resource/view_controller/take_photo_form/Controller.py")
        photo = pickle.load(open(path_depth + "resource/variable/_photo.pkl", "rb"))
        if photo is not None:
            database[selected.row()][1][0] = photo
            faces = fa.get(database[selected.row()][1][0])
            if len(faces) > 0:
                database[selected.row()][1][1] = faces[0].embedding
                pickle.dump(database, open(path_depth + "resource/database/" + group_name + ".pkl", "wb"))

                _image = cv2.resize(photo, (win.label_image_1.width(), win.label_image_1.height()))
                q_pixmap = QPixmap.fromImage(QImage(cv2.cvtColor(_image, cv2.COLOR_BGR2RGB).data, _image.shape[1], _image.shape[0], QImage.Format.Format_RGB888))
                win.label_image_1.setPixmap(q_pixmap)
            else:
                print("No face detected in the photo.")
        win.show()


win.pushButton_take_photo_1.clicked.connect(on_button_take_photo_1_clicked)


def on_button_take_photo_2_clicked():
    if win.listView_name.selectedIndexes():

        selected = win.listView_name.selectedIndexes()[0]
        win.hide()
        os.system("python " + path_depth + "resource/view_controller/take_photo_form/Controller.py")
        photo = pickle.load(open(path_depth + "resource/variable/_photo.pkl", "rb"))
        if photo is not None:
            database[selected.row()][2][0] = photo
            faces = fa.get(database[selected.row()][2][0])
            if len(faces) > 0:
                database[selected.row()][2][1] = faces[0].embedding
                pickle.dump(database, open(path_depth + "resource/database/" + group_name + ".pkl", "wb"))

                _image = cv2.resize(photo, (win.label_image_2.width(), win.label_image_2.height()))
                q_pixmap = QPixmap.fromImage(QImage(cv2.cvtColor(_image, cv2.COLOR_BGR2RGB).data, _image.shape[1], _image.shape[0], QImage.Format.Format_RGB888))
                win.label_image_2.setPixmap(q_pixmap)
            else:
                print("No face detected in the photo.")

        win.show()


win.pushButton_take_photo_2.clicked.connect(on_button_take_photo_2_clicked)


def on_button_clear_image_1_clicked():
    if win.listView_name.selectedIndexes():
        selected = win.listView_name.selectedIndexes()[0]

        database[selected.row()][1][0] = None
        database[selected.row()][1][1] = None
        win.label_image_1.clear()
        win.label_image_1.setText("No Image #1")

        pickle.dump(database, open(path_depth + "resource/database/" + group_name + ".pkl", "wb"))


win.pushButton_clear_image_1.clicked.connect(on_button_clear_image_1_clicked)


def on_button_clear_image_2_clicked():
    if win.listView_name.selectedIndexes():
        selected = win.listView_name.selectedIndexes()[0]

        database[selected.row()][2][0] = None
        database[selected.row()][2][1] = None
        win.label_image_2.clear()
        win.label_image_2.setText("No Image #2")

        pickle.dump(database, open(path_depth + "resource/database/" + group_name + ".pkl", "wb"))


win.pushButton_clear_image_2.clicked.connect(on_button_clear_image_2_clicked)


def on_button_back_clicked():
    win.close()


win.pushButton_back.clicked.connect(on_button_back_clicked)


win.pushButton_upload_image_1.setIcon(QIcon(f"{path_depth}resource/asset/image-upload.png"))
win.pushButton_upload_image_2.setIcon(QIcon(f"{path_depth}resource/asset/image-upload.png"))
win.pushButton_take_photo_1.setIcon(QIcon(f"{path_depth}resource/asset/photo-camera.png"))
win.pushButton_take_photo_2.setIcon(QIcon(f"{path_depth}resource/asset/photo-camera.png"))
win.pushButton_back.setIcon(QIcon(f"{path_depth}resource/asset/previous.png"))


app.exec_()


database.sort(key=lambda x: x[0])
pickle.dump(database, open(path_depth + "resource/database/" + group_name + ".pkl", "wb"))


app = None

