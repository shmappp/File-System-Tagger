import os
import json
from PyQt6.QtWidgets import QApplication, QWidget

import sys

DATA_JSON = os.path.join(os.getcwd(), 'data.json')

def load_data():
    if os.path.exists(DATA_JSON):
        with open('DATA_JSON', 'r') as f:
            return json.load(f)
    else:
        return []

def save_data(data):
    with open(DATA_JSON, 'w') as f:
        json.dump(data, f, indent=2)

app = QApplication(sys.argv)

window = QWidget()
window.show()

app.exec()