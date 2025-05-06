import os
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QPushButton, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout
)
from PyQt6.QtGui import QColor, QPalette
import packages.json_util

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
    def __init__(self):
        super().__init__()

        self.setWindowTitle("File System Tagger")
        self.setGeometry(100, 100, 1500, 1200)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor('#111111'))
        self.setPalette(palette)

        



app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()