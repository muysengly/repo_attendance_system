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


from View import Ui_MainWindow

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


import csv
import datetime


# In[4]:


from AttendanceDatabase import AttendanceDatabase

att_db = AttendanceDatabase(path_depth + "attendance.sqlite")


# In[ ]:


class Window(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QIcon(f"{path_depth}resource/asset/my_logo.png"))
        self.setWindowTitle("Angkor Inference")

        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
        self.setMaximumSize(QWIDGETSIZE_MAX, QWIDGETSIZE_MAX)

        self.show()


# In[6]:


app = QApplication([])
win = Window()

data = []  # to store attendance data

now = datetime.datetime.now()
# ytd = now - datetime.timedelta(days=1) # yesterday's date

win.dateEdit_start_date.setDate(QDate(now.year, now.month, now.day))
win.timeEdit_start_time.setTime(QTime(0, 0, 0))

win.dateEdit_end_date.setDate(QDate(now.year, now.month, now.day))
win.timeEdit_end_time.setTime(QTime(23, 59, 59))


win.tableWidget.setColumnWidth(0, 320)
win.tableWidget.setColumnWidth(1, 130)
win.tableWidget.setColumnWidth(2, 100)

win.pushButton_back.setIcon(QIcon(f"{path_depth}resource/asset/previous.png"))
win.pushButton_query.setIcon(QIcon(f"{path_depth}resource/asset/data-searching.png"))


group_names = att_db.read_group()
win.comboBox_group_name.addItems(group_names)

if len(group_names) == 0:
    win.comboBox_group_name.setEnabled(False)
    win.dateEdit_end_date.setEnabled(False)
    win.dateEdit_start_date.setEnabled(False)
    win.timeEdit_end_time.setEnabled(False)
    win.timeEdit_start_time.setEnabled(False)
    win.pushButton_query.setEnabled(False)
    win.pushButton_save.setEnabled(False)
    win.pushButton_clear.setEnabled(False)
    win.tableWidget.setEnabled(False)
    QMessageBox.warning(win, "Warning", "No groups found in the database. \nPlease add a group first.")
else:
    group_name = group_names[0]
    # win.comboBox_group_name.setEnabled(True)


def on_group_name_changed(index):
    global group_name
    group_name = win.comboBox_group_name.itemText(index)


win.comboBox_group_name.currentIndexChanged.connect(on_group_name_changed)


def on_button_query_clicked():

    global data

    start_date = win.dateEdit_start_date.date().toString("yyyy-MM-dd")
    start_time = win.timeEdit_start_time.time().toString("HH:mm:ss")

    end_date = win.dateEdit_end_date.date().toString("yyyy-MM-dd")
    end_time = win.timeEdit_end_time.time().toString("HH:mm:ss")

    data = att_db.read_data(group_name, start_date, start_time, end_date, end_time)

    win.tableWidget.setRowCount(len(data))
    for i, row in enumerate(data):
        for j, item in enumerate(row):
            cell = QTableWidgetItem(item)
            if j == 0:  # Name column
                cell.setTextAlignment(Qt.AlignLeft)
            else:  # Date and Time columns
                cell.setTextAlignment(Qt.AlignCenter)
            win.tableWidget.setItem(i, j, cell)


win.pushButton_query.clicked.connect(on_button_query_clicked)


def on_button_clear_clicked():
    global data
    data = []
    win.tableWidget.setRowCount(0)


win.pushButton_clear.clicked.connect(on_button_clear_clicked)


def on_button_save_csv_clicked():

    if data.__len__() == 0:
        QMessageBox.warning(win, "Warning", "No data to save.")
        return

    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getSaveFileName(win, "Save Attendance", f"attd_{group_name}_{now.strftime('%Y%m%d_%H%M%S')}", "CSV Files (*.csv)", options=options)
    if file_path:
        try:
            with open(file_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Name", "Date", "Time"])  # Adjust headers as needed
                for row in data:
                    writer.writerow(row)
            QMessageBox.information(win, "Success", f"Data saved to: \n{file_path}")
        except Exception as e:
            QMessageBox.critical(win, "Error", f"Failed to save data!")


win.pushButton_save.clicked.connect(on_button_save_csv_clicked)


def on_button_back_clicked():
    win.close()


win.pushButton_back.clicked.connect(on_button_back_clicked)


app.exec_()
app = None

