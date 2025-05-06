import os
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QPushButton, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QTreeView
)
from PyQt6.QtGui import QColor, QPalette, QFileSystemModel
from PyQt6.QtCore import QDir
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

        index = self.model.index(path)
        if index.isValid():
            self.tree.expand(index.parent())
            self.tree.setCurrentIndex(index)
            self.tree.scrollTo(index)
        else:
            print(f'Navigation to {path} failed')

    def __init__(self):
        super().__init__()

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
        self.explorer = QFileSystemModel()
        self.tree = QTreeView()
        self.tree.setModel(self.explorer)
        self.tree.setColumnWidth(0, 300)
        self.tree.setRootIndex(self.explorer.index(QDir.rootPath()))

        explorer_layout.addWidget(self.tree)
        main_layout.addLayout(explorer_layout)




app = QApplication(sys.argv)
qdarktheme.setup_theme()
window = MainWindow()
window.show()
app.exec()