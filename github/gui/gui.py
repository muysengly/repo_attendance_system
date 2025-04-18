# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'github/gui/026.ui'
#
# Created by: PyQt5 UI code generator 5.15.11
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1270, 680)
        MainWindow.setMinimumSize(QtCore.QSize(0, 0))
        MainWindow.setMaximumSize(QtCore.QSize(100000, 10000))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label_camera = QtWidgets.QLabel(self.centralwidget)
        self.label_camera.setGeometry(QtCore.QRect(10, 120, 640, 480))
        self.label_camera.setFrameShape(QtWidgets.QFrame.Box)
        self.label_camera.setText("")
        self.label_camera.setObjectName("label_camera")
        self.pushButton_save = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_save.setGeometry(QtCore.QRect(960, 605, 300, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_save.setFont(font)
        self.pushButton_save.setObjectName("pushButton_save")
        self.listView_attd = QtWidgets.QListView(self.centralwidget)
        self.listView_attd.setGeometry(QtCore.QRect(960, 155, 300, 445))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.listView_attd.setFont(font)
        self.listView_attd.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.listView_attd.setObjectName("listView_attd")
        self.listView_init = QtWidgets.QListView(self.centralwidget)
        self.listView_init.setGeometry(QtCore.QRect(655, 155, 300, 445))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.listView_init.setFont(font)
        self.listView_init.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.listView_init.setObjectName("listView_init")
        self.pushButton_reset = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_reset.setGeometry(QtCore.QRect(1180, 110, 80, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_reset.setFont(font)
        self.pushButton_reset.setObjectName("pushButton_reset")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(960, 115, 300, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(450, 40, 400, 60))
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setUnderline(False)
        font.setWeight(75)
        font.setStrikeOut(False)
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.label_logo = QtWidgets.QLabel(self.centralwidget)
        self.label_logo.setGeometry(QtCore.QRect(10, 10, 100, 100))
        self.label_logo.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_logo.setAlignment(QtCore.Qt.AlignCenter)
        self.label_logo.setObjectName("label_logo")
        self.label_version = QtWidgets.QLabel(self.centralwidget)
        self.label_version.setGeometry(QtCore.QRect(850, 40, 400, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_version.setFont(font)
        self.label_version.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_version.setObjectName("label_version")
        self.label_developer = QtWidgets.QLabel(self.centralwidget)
        self.label_developer.setGeometry(QtCore.QRect(850, 10, 400, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_developer.setFont(font)
        self.label_developer.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_developer.setObjectName("label_developer")
        self.comboBox_camera = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_camera.setGeometry(QtCore.QRect(10, 605, 200, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.comboBox_camera.setFont(font)
        self.comboBox_camera.setObjectName("comboBox_camera")
        self.comboBox_group = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_group.setGeometry(QtCore.QRect(655, 120, 300, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.comboBox_group.setFont(font)
        self.comboBox_group.setObjectName("comboBox_group")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(435, 610, 150, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.spinBox_threshold = QtWidgets.QSpinBox(self.centralwidget)
        self.spinBox_threshold.setGeometry(QtCore.QRect(590, 610, 60, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.spinBox_threshold.setFont(font)
        self.spinBox_threshold.setMinimum(50)
        self.spinBox_threshold.setObjectName("spinBox_threshold")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(0, 650, 1270, 20))
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.pushButton_capture = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_capture.setGeometry(QtCore.QRect(655, 606, 300, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_capture.setFont(font)
        self.pushButton_capture.setObjectName("pushButton_capture")
        self.pushButton_update = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_update.setGeometry(QtCore.QRect(260, 605, 100, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_update.setFont(font)
        self.pushButton_update.setObjectName("pushButton_update")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton_save.setText(_translate("MainWindow", "Save"))
        self.pushButton_reset.setText(_translate("MainWindow", "Reset"))
        self.label_3.setText(_translate("MainWindow", "Presented"))
        self.label_4.setText(_translate("MainWindow", "Attendance System"))
        self.label_logo.setText(_translate("MainWindow", "LOGO"))
        self.label_version.setText(_translate("MainWindow", "Version"))
        self.label_developer.setText(_translate("MainWindow", "Developer"))
        self.label.setText(_translate("MainWindow", "Threshold [%]:"))
        self.label_2.setText(_translate("MainWindow", "🙏 Thank to: Lokru PO Kimtho, Lokru SRENG Sokchenda, Lokru PEC Rathana, Lokru HEL Chanthan, and 7th generation GTR students 🙏"))
        self.pushButton_capture.setText(_translate("MainWindow", "Register"))
        self.pushButton_update.setText(_translate("MainWindow", "Update"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
