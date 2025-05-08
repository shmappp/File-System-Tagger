from PyQt6.QtWidgets import (
    QTreeView, QAbstractItemView, QLineEdit, QCompleter, QWidget, QVBoxLayout
)
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtCore import Qt

from config import Config

from modules.custom_file_system_model import CustomFileSystemModel


class FileSystemViewer:

    def __init__(self, tagging_system):
        self.tagging_system = tagging_system

        # explorer tree view
        self.tree_model = CustomFileSystemModel(self.tagging_system)
        self.tree_model.setRootPath(Config.DEFAULT_ROOT_PATH)

        self.root_index = self.tree_model.index(Config.DEFAULT_ROOT_PATH) #TODO: replace

        self.tree = QTreeView()
        self.tree.setModel(self.tree_model)
        self.tree.setRootIndex(self.root_index)
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        # path field
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText('Enter full path and press Enter')
        self.path_input.setText(Config.DEFAULT_ROOT_PATH) # default to root

        # path field completion logic
        self.completer_model = QFileSystemModel()
        self.completer_model.setRootPath(Config.DEFAULT_ROOT_PATH)

        completer = QCompleter(self.completer_model, self.path_input)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchStartsWith)
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)

        self.path_input.setCompleter(completer)
    
    def get_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.path_input)
        layout.addWidget(self.tree)
        widget.setLayout(layout)
        return widget