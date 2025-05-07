import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListView, QPushButton, QLineEdit, QMessageBox
from PyQt5.QtCore import QStringListModel


class ListEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("List View Editor")
        self.setGeometry(100, 100, 400, 300)

        # Layouts
        main_layout = QVBoxLayout()
        input_layout = QHBoxLayout()
        button_layout = QHBoxLayout()

        # Widgets
        self.model = QStringListModel()
        self.view = QListView()
        self.view.setModel(self.model)

        self.input = QLineEdit()
        self.add_button = QPushButton("Add")
        self.edit_button = QPushButton("Edit")
        self.delete_button = QPushButton("Delete")

        # Assemble layouts
        input_layout.addWidget(self.input)
        input_layout.addWidget(self.add_button)

        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)

        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.view)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        # Connections
        self.add_button.clicked.connect(self.add_item)
        self.edit_button.clicked.connect(self.edit_item)
        self.delete_button.clicked.connect(self.delete_item)

    def add_item(self):
        text = self.input.text().strip()
        if text:
            current_items = self.model.stringList()
            current_items.append(text)
            self.model.setStringList(current_items)
            self.input.clear()

    def edit_item(self):
        selected_indexes = self.view.selectedIndexes()
        if selected_indexes:
            index = selected_indexes[0]
            new_text = self.input.text().strip()
            if new_text:
                self.model.setData(index, new_text)
                self.input.clear()
        else:
            QMessageBox.warning(self, "No Selection", "Please select an item to edit.")

    def delete_item(self):
        selected_indexes = self.view.selectedIndexes()
        if selected_indexes:
            index = selected_indexes[0]
            current_items = self.model.stringList()
            del current_items[index.row()]
            self.model.setStringList(current_items)
        else:
            QMessageBox.warning(self, "No Selection", "Please select an item to delete.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ListEditor()
    window.show()
    sys.exit(app.exec_())
