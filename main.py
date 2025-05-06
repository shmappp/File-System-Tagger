import os
import json
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton
import packages.json_util

import sys

DATA_JSON = os.path.join(os.getcwd(), 'data.json')

app = QApplication(sys.argv)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('File System Tagger')
        button = QPushButton('Start')

        self.setCentralWidget(button)

window = MainWindow()
window.show()

app.exec()