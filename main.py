import os
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QPushButton, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QTreeView, QCompleter
)
from PyQt6.QtGui import QColor, QPalette, QFileSystemModel
from PyQt6.QtCore import QDir, Qt
import packages.json_util
import qdarktheme

import sys

DATA_JSON = os.path.join(os.getcwd(), 'data.json')


class Color(QWidget):
    def __init__(self, color):
        super().__init__()

        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)

class MainWindow(QMainWindow):
    def navigate_to_path(self):
        path = self.path_input.text()

        if not os.path.exists(path):
            print('Path does not exist')
            return

        index = self.tree_model.index(path)
        if index.isValid():
            self.tree.expand(index.parent())
            self.tree.setCurrentIndex(index)
            self.tree.scrollTo(index)
        else:
            print(f'Navigation to {path} failed')

    def __init__(self):
        super().__init__()

        self.root_path = os.path.expanduser("~")

        self.setWindowTitle("File System Tagger")
        self.setGeometry(100, 100, 1500, 1200)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor('#111111'))
        self.setPalette(palette)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        explorer_layout = QVBoxLayout()
        self.tree_model = QFileSystemModel()
        self.tree_model.setRootPath(self.root_path)
        self.root_index = self.tree_model.index(self.root_path) #TODO: replace
        self.tree = QTreeView()
        self.tree.setModel(self.tree_model)
        self.tree.setColumnWidth(0, 300)
        self.tree.setRootIndex(self.root_index)
        
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText('Enter full path and press Enter')
        self.path_input.returnPressed.connect(self.navigate_to_path)

        self.completer_model = QFileSystemModel()
        self.completer_model.setRootPath(self.root_path)

        completer = QCompleter(self.completer_model, self.path_input)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchStartsWith)
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)

        self.path_input.setCompleter(completer)

        explorer_layout.addWidget(self.path_input)
        explorer_layout.addWidget(self.tree)
        main_layout.addLayout(explorer_layout)




app = QApplication(sys.argv)
qdarktheme.setup_theme()
window = MainWindow()
window.show()
app.exec()