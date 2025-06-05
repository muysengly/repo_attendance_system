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


path_depth = "../../../"  # adjust the current working directory
if "__file__" not in globals():  # check if running in Jupyter Notebook
    os.system("jupyter nbconvert --to script Controller.ipynb --output Controller")  # convert notebook to script
    os.system("pyuic5 -x View.ui -o View.py")  # convert UI file to Python script

os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_SCALE_FACTOR"] = "1"
os.environ["NO_ALBUMENTATIONS_UPDATE"] = "1"

import ctypes

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("my.app.id")  # work for Windows taskbar


# In[3]:


from View import Ui_MainWindow

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import pickle
import requests
import zipfile


# In[4]:


import sys

sys.path.append(path_depth)
from resource.utility.Database import DataBase

db = DataBase(path_depth + "database.sqlite")


# In[ ]:


class Window(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QIcon(f"{path_depth}resource/asset/itc_logo.png"))
        self.setWindowTitle("Main Form")

        self.label_itc_logo.setPixmap(QPixmap(f"{path_depth}resource/asset/itc_logo.png").scaled(self.label_itc_logo.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.label_gtr_logo.setPixmap(QPixmap(f"{path_depth}resource/asset/gtr_logo.png").scaled(self.label_gtr_logo.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

        self.comboBox_group_name.clear()
        self.comboBox_group_name.addItems(db.read_table())

        self.show()


# In[6]:


app = QApplication([])
win = Window()

# open(path_depth + "resource/variable/_version.txt", "w").write("1.0.2")
version_string = open(path_depth + "resource/variable/_version.txt", "r").read().strip()
version_int = list(map(int, version_string.split(".")))
win.label_version.setText(f"Version: {version_string}")

win.pushButton_check_attendance.setIcon(QIcon(f"{path_depth}resource/asset/face-scanner.png"))
win.pushButton_manage.setIcon(QIcon(f"{path_depth}resource/asset/settings-gears.png"))
win.pushButton_check_update.setIcon(QIcon(f"{path_depth}resource/asset/refresh.png"))


def on_manage_button_clicked():
    win.hide()

    os.system("python " + path_depth + "resource/view_controller/select_manage_form/Controller.py")
    win.comboBox_group_name.clear()
    win.comboBox_group_name.addItems(db.read_table())

    win.show()


win.pushButton_manage.clicked.connect(on_manage_button_clicked)


def on_check_attendance_button_clicked():
    if len(db.read_table()) > 0:
        win.hide()

        group_name = win.comboBox_group_name.currentText()
        pickle.dump(group_name, open(path_depth + "resource/variable/_group_name.pkl", "wb"))
        os.system("python " + path_depth + "resource/view_controller/check_attendance_form/Controller.py")

        win.show()


win.pushButton_check_attendance.clicked.connect(on_check_attendance_button_clicked)


def on_click_update_button():

    try:
        headers = {"Accept": "application/vnd.github.v3.raw"}
        git_version_string = requests.get("https://api.github.com/repos/muysengly/repo_attendance_system/contents/resource/variable/_version.txt", headers=headers).text
        git_version_int = list(map(int, git_version_string.split(".")))

        if git_version_int > version_int:  # NOTE: 1.0.2 < 1.0.3 / 1.0.2 < 1.1.0 / 1.0.2 < 2.0.0
            reply = QMessageBox.question(win, "Update Available", f"Version {git_version_string} is available. \nDo you want to update?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:

                for _ in range(10):  # retry up to 10 times
                    response = requests.get("https://github.com/muysengly/repo_attendance_system/archive/refs/heads/main.zip", stream=True)
                    total_size = int(response.headers.get("content-length", 0))
                    if total_size > 0:
                        break

                if total_size > 0:
                    progress = QProgressDialog("Downloading update...", "Cancel", 0, 100, win)
                    progress.setWindowModality(Qt.WindowModal)
                    progress.setMinimumSize(400, 100)
                    progress.setWindowTitle("Update in progress")
                    progress.setValue(0)
                    downloaded = 0
                    with open("tmp.zip", "wb") as f:
                        for data in response.iter_content(1024):
                            if progress.wasCanceled():
                                response.close()
                                QMessageBox.warning(win, "Cancelled", "Update cancelled.")
                                return
                            f.write(data)
                            downloaded += len(data)
                            percent = int(downloaded * 100 / total_size)
                            progress.setValue(percent)
                    progress.setValue(100)

                    # extract the downloaded zip file
                    with zipfile.ZipFile("tmp.zip", "r") as zip_ref:
                        zip_ref.extractall("c:\\")

                    # show message box to inform the user
                    QMessageBox.information(win, "Update Complete", f"Updated to version {git_version_string}. \nPlease restart the application.")
                else:
                    QMessageBox.warning(win, "Download Error", "Failed to download the update. \nPlease try again later.")
        else:
            QMessageBox.information(win, "No Update", "You are already using the latest version.")

    except requests.RequestException as e:
        QMessageBox.critical(win, "Error", "No Internet Connection!")


win.pushButton_check_update.clicked.connect(on_click_update_button)


app.exec_()
app = None
if os.path.exists("tmp.zip"):
    os.remove("tmp.zip")

