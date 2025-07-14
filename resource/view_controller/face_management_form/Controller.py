#!/usr/bin/env python
# coding: utf-8

# In[1]:


# TODO:
# -
# -
# -
# -
# -


# In[2]:


import os
import sys


path_depth = "../../../"  # adjust the current working directory

if "__file__" not in globals():  # check if running in Jupyter Notebook
    os.system("jupyter nbconvert --to script Controller.ipynb --output Controller")  # convert notebook to script
    os.system("pyuic5 -x View.ui -o View.py")  # convert UI file to Python script


sys.path.append(os.path.abspath(os.path.join(path_depth, "resource", "utility")))


if os.name == "nt":
    import ctypes

    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("my.app.id")


# In[3]:


from insightface.app import FaceAnalysis  # NOTE: this library need to import first

from View import Ui_MainWindow

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import cv2
import pickle
import numpy as np


# In[4]:


from Database import DataBase

db = DataBase(path_depth + "database.sqlite")


# In[5]:


fa = FaceAnalysis(name="buffalo_sc", root=f"{os.getcwd()}/{path_depth}resource/utility/", providers=["CPUExecutionProvider"])
fa.prepare(ctx_id=-1, det_thresh=0.5, det_size=(640, 640))


# In[6]:


# pickle.dump("001 DEMO", open(path_depth + "resource/variable/_group_name.pkl", "wb"))
group_name = pickle.load(open(path_depth + "resource/variable/_group_name.pkl", "rb"))
# group_name


# In[7]:


face_names = db.read_face_names(group_name)  # read the database from the sqlite file
# face_names


# In[ ]:


class Window(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QIcon(f"{path_depth}resource/asset/my_logo.png"))
        self.setWindowTitle("Angkor Inference")

        self.listView_name.setModel(QStringListModel(face_names))

        self.label_group_name.setText('Face Management in "' + group_name + '"')


        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
        self.setMaximumSize(QWIDGETSIZE_MAX, QWIDGETSIZE_MAX)

        self.show()


# In[9]:


app = QApplication([])
win = Window()


win.pushButton_upload_image_1.setIcon(QIcon(f"{path_depth}resource/asset/image-upload.png"))
win.pushButton_upload_image_2.setIcon(QIcon(f"{path_depth}resource/asset/image-upload.png"))
win.pushButton_take_photo_1.setIcon(QIcon(f"{path_depth}resource/asset/photo-camera.png"))
win.pushButton_take_photo_2.setIcon(QIcon(f"{path_depth}resource/asset/photo-camera.png"))
win.pushButton_back.setIcon(QIcon(f"{path_depth}resource/asset/previous.png"))
win.pushButton_add.setIcon(QIcon(f"{path_depth}resource/asset/add_person.png"))

_name = ""


def on_button_add_click():

    win.listView_name.clearSelection()

    text = win.lineEdit_name.text()
    if text is not None:
        text = text.strip()
        if text.upper() not in db.read_face_names(group_name):
            win.listView_name.model().insertRow(win.listView_name.model().rowCount())
            index = win.listView_name.model().index(win.listView_name.model().rowCount() - 1)
            win.listView_name.model().setData(index, text.upper())
            db.create_face_name(group_name, text.upper())
        else:
            QMessageBox.warning(win, "Warning", "Name already exists!")

    win.lineEdit_name.clear()
    win.lineEdit_name.setFocus()


win.pushButton_add.clicked.connect(on_button_add_click)
win.lineEdit_name.returnPressed.connect(on_button_add_click)


def on_listview_double_click():
    global _name
    if win.listView_name.selectedIndexes():
        seleted = win.listView_name.selectedIndexes()[0]
        _name = seleted.data()


win.listView_name.doubleClicked.connect(on_listview_double_click)


def on_listview_data_changed():
    if win.listView_name.selectedIndexes():
        selected = win.listView_name.selectedIndexes()[0]

        if selected.data().strip() == "":
            win.listView_name.model().removeRow(selected.row())
            db.delete_face_name(group_name, _name)

        elif selected.data().strip().upper() in db.read_face_names(group_name) and selected.data().strip() != _name:
            QMessageBox.warning(win, "Warning", "Name already exists!")
            win.listView_name.model().setData(selected, _name)

        elif selected.data().upper() != _name:
            win.listView_name.model().setData(selected, selected.data().strip().upper())
            db.update_face_name(group_name, _name, selected.data().strip().upper())


win.listView_name.model().dataChanged.connect(on_listview_data_changed)


def on_listview_single_clicked():
    if win.listView_name.selectedIndexes():
        selected = win.listView_name.selectedIndexes()[0]

        img_1 = db.read_image_1(group_name, selected.data())
        if img_1 is not None and len(img_1) > 0:
            img_1 = cv2.resize(img_1, (win.label_image_1.width(), win.label_image_1.height()))
            img_1 = cv2.cvtColor(img_1, cv2.COLOR_BGR2RGB)
            q_pixmap = QPixmap.fromImage(QImage(cv2.cvtColor(img_1, cv2.COLOR_BGR2RGB).data, img_1.shape[1], img_1.shape[0], QImage.Format.Format_RGB888))
            win.label_image_1.setPixmap(q_pixmap)

        else:
            win.label_image_1.clear()
            win.label_image_1.setText("No Image #1")

        img_2 = db.read_image_2(group_name, selected.data())
        if img_2 is not None and len(img_2) > 0:
            img_2 = cv2.resize(img_2, (win.label_image_2.width(), win.label_image_2.height()))
            img_2 = cv2.cvtColor(img_2, cv2.COLOR_BGR2RGB)
            q_pixmap = QPixmap.fromImage(QImage(cv2.cvtColor(img_2, cv2.COLOR_BGR2RGB).data, img_2.shape[1], img_2.shape[0], QImage.Format.Format_RGB888))
            win.label_image_2.setPixmap(q_pixmap)
        else:
            win.label_image_2.clear()
            win.label_image_2.setText("No Image #2")


win.listView_name.selectionModel().selectionChanged.connect(on_listview_single_clicked)


def on_listview_right_click_context_menu(point):
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
                db.delete_face_name(group_name, name)
                if len(db.read_face_names(group_name)) == 0:  # if no data in database
                    win.label_image_1.clear()
                    win.label_image_2.clear()
                    win.label_image_1.setText("No Image #1")
                    win.label_image_2.setText("No Image #2")


win.listView_name.setContextMenuPolicy(Qt.CustomContextMenu)
win.listView_name.customContextMenuRequested.connect(on_listview_right_click_context_menu)


def on_button_upload_image_1_clicked():

    if win.listView_name.selectedIndexes():
        selected = win.listView_name.selectedIndexes()[0]

        file_name, _ = QFileDialog.getOpenFileName(win, "Open Image File", "", "Images (*.jpg);")
        if file_name:

            image = np.array(cv2.imread(file_name))
            faces = fa.get(image)

            if len(faces) == 1:
                face = faces[0]
                box = face.bbox.astype(int)
                if (box[2] - box[0]) > 160 or (box[3] - box[1]) > 160:
                    db.create_image_1_from_path(group_name, selected.data(), file_name)
                    db.create_emb_1(group_name, selected.data(), faces[0].embedding)

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

                    db.create_image_2_from_path(group_name, selected.data(), file_name)
                    db.create_emb_2(group_name, selected.data(), faces[0].embedding)

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


def on_button_take_photo_1_clicked():

    if win.listView_name.selectedIndexes():
        selected = win.listView_name.selectedIndexes()[0]
        win.hide()

        pickle.dump(None, open(path_depth + "resource/variable/_photo.pkl", "wb"))

        os.system("python " + path_depth + "resource/view_controller/take_photo_form/Controller.py")

        photo = pickle.load(open(path_depth + "resource/variable/_photo.pkl", "rb"))

        if photo is not None:
            db.create_image_1_from_array(group_name, selected.data(), photo)
            db.create_emb_1(group_name, selected.data(), fa.get(photo)[0].embedding)
            _image = cv2.resize(photo, (win.label_image_1.width(), win.label_image_1.height()))
            q_pixmap = QPixmap.fromImage(QImage(cv2.cvtColor(_image, cv2.COLOR_BGR2RGB).data, _image.shape[1], _image.shape[0], QImage.Format.Format_RGB888))
            win.label_image_1.setPixmap(q_pixmap)

        pickle.dump(None, open(path_depth + "resource/variable/_photo.pkl", "wb"))

        win.show()


win.pushButton_take_photo_1.clicked.connect(on_button_take_photo_1_clicked)


def on_button_take_photo_2_clicked():
    if win.listView_name.selectedIndexes():
        selected = win.listView_name.selectedIndexes()[0]
        win.hide()

        pickle.dump(None, open(path_depth + "resource/variable/_photo.pkl", "wb"))

        os.system("python " + path_depth + "resource/view_controller/take_photo_form/Controller.py")

        photo = pickle.load(open(path_depth + "resource/variable/_photo.pkl", "rb"))

        if photo is not None:

            db.create_image_2_from_array(group_name, selected.data(), photo)
            db.create_emb_2(group_name, selected.data(), fa.get(photo)[0].embedding)

            _image = cv2.resize(photo, (win.label_image_2.width(), win.label_image_2.height()))
            q_pixmap = QPixmap.fromImage(QImage(cv2.cvtColor(_image, cv2.COLOR_BGR2RGB).data, _image.shape[1], _image.shape[0], QImage.Format.Format_RGB888))
            win.label_image_2.setPixmap(q_pixmap)

        pickle.dump(None, open(path_depth + "resource/variable/_photo.pkl", "wb"))

        win.show()


win.pushButton_take_photo_2.clicked.connect(on_button_take_photo_2_clicked)


def on_button_clear_image_1_clicked():
    if win.listView_name.selectedIndexes():
        selected = win.listView_name.selectedIndexes()[0]
        win.label_image_1.clear()
        win.label_image_1.setText("No Image #1")

        db.delete_image_1(group_name, selected.data())
        db.delete_emb_1(group_name, selected.data())


win.pushButton_clear_image_1.clicked.connect(on_button_clear_image_1_clicked)


def on_button_clear_image_2_clicked():
    if win.listView_name.selectedIndexes():
        selected = win.listView_name.selectedIndexes()[0]

        win.label_image_2.clear()
        win.label_image_2.setText("No Image #2")

        db.delete_image_2(group_name, selected.data())
        db.delete_emb_2(group_name, selected.data())


win.pushButton_clear_image_2.clicked.connect(on_button_clear_image_2_clicked)


def on_button_back_clicked():
    win.close()


win.pushButton_back.clicked.connect(on_button_back_clicked)


app.exec_()


app = None

