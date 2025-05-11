import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLabel, QHBoxLayout


class CustomWidget(QWidget):
    def __init__(self, text):
        super().__init__()
        layout = QHBoxLayout()
        self.label = QLabel(text)
        self.button = QPushButton("Click")
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        self.setLayout(layout)


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("List with Text and Button")
        self.resize(300, 400)

        layout = QVBoxLayout()
        self.list_widget = QListWidget()

        for i in range(5):
            item = QListWidgetItem(self.list_widget)
            widget = CustomWidget(f"Item {i+1}")
            item.setSizeHint(widget.sizeHint())
            self.list_widget.setItemWidget(item, widget)

        layout.addWidget(self.list_widget)
        self.setLayout(layout)


app = QApplication(sys.argv)
window = MyWindow()
window.show()
sys.exit(app.exec_())
