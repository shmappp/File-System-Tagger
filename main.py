import os

from PyQt6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QVBoxLayout,QSplitter, QMenu, QTextEdit
)
from PyQt6.QtGui import QColor, QPalette, QAction, QTextOption
from PyQt6.QtCore import Qt
import qdarktheme
import sys
import subprocess
import platform
from functools import partial

import utils.json_util as json_util

from config import Config

from ui.tag_confirm_button import TagConfirmButton
from modules.tagging_system import TaggingSystem
from ui.file_system_viewer import FileSystemViewer
from ui.file_preview_manager import FilePreviewManager


TAG_JSON = os.path.join(os.getcwd(), 'tags.json')

tags = json_util.load_data(TAG_JSON)

class FileSystemTaggingApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.tagging_system = TaggingSystem(TAG_JSON)
        self.explorer = FileSystemViewer(self.tagging_system)
        self.preview_manager = FilePreviewManager()

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self.setWindowTitle(Config.WINDOW_TITLE)
        self.setGeometry(*Config.WINDOW_GEOMETRY)
        
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(Config.WINDOW_BG_COLOR))
        self.setPalette(palette)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        central_widget.setLayout(main_layout)

        splitter.addWidget(self.explorer.get_widget())

        actions_widget = QWidget()
        actions_layout = QVBoxLayout(actions_widget)

        actions_layout.addWidget(self.preview_manager.get_widget())
        
        self.tag_display = QTextEdit()
        self.tag_display.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        self.tag_display.setPlaceholderText('Type comma-separated tags')
        actions_layout.addWidget(self.tag_display)

        self.update_tag_button = TagConfirmButton(self.tagging_system)
        self.update_tag_button.set_tag_display(self.tag_display)
        actions_layout.addWidget(self.update_tag_button)
        
        splitter.addWidget(actions_widget)

    def _connect_signals(self):
        self.explorer.path_input.returnPressed.connect(self.navigate_to_path)
        self.explorer.tree.selectionModel().currentChanged.connect(self.on_tree_selection_changed)
        self.explorer.tree.clicked.connect(self.file_selected)
        self.explorer.tree.doubleClicked.connect(self.open_selected_file)
        self.explorer.tree.customContextMenuRequested.connect(self.on_tree_context_menu)


    def navigate_to_path(self):
        path = self.explorer.path_input.text()

        if not os.path.exists(path):
            print('Path does not exist')
            return

        index = self.explorer.tree_model.index(path)
        if index.isValid():
            self.explorer.tree.setRootIndex(index) #optional: dynamic root traversal
            self.explorer.tree.expand(index.parent())
            self.explorer.tree.setCurrentIndex(index)
            self.explorer.tree.scrollTo(index)
        else:
            print(f'Navigation to {path} failed')
    
    def on_tree_selection_changed(self, current, previous):
        current_path = self.explorer.tree_model.filePath(current)
        self.explorer.path_input.setText(current_path)

    def populate_tag_display(self, path):
        if os.path.exists(path):
            tags = self.tagging_system.get_tags(path)
            self.tag_display.setText(','.join(tags)) 

    def file_selected(self, index):
        path = self.explorer.tree_model.filePath(index)
        if os.path.isfile(path):
            self.preview_manager.display_preview(path)
            self.populate_tag_display(path)
            self.update_tag_button.set_path(path)
            
    def handle_open(self, path):
        os.startfile(path) #TODO: allow other os
    
    def handle_reveal(self, path):
        path = os.path.abspath(path)
        system = platform.system()

        if system == 'Windows':
            subprocess.run(['explorer', '/select,', os.path.normpath(path)])
        elif system == 'Darwin':
            subprocess.run(['open', '-R', path])
        elif system == 'Linus':
            folder = os.path.dirname(path)
            subprocess.run(['xdg-open', folder])
        else:
            print(f'Unsupported OS: {system}')

    def open_selected_file(self, index):
        path = self.explorer.tree_model.filePath(index)
        self.handle_open(path)

    def on_tree_context_menu(self, pos):
        index = self.explorer.tree.indexAt(pos)
        if not index.isValid():
            return
        
        selected_indexes = self.explorer.tree.selectionModel().selectedIndexes()
        selected_paths = set()

        for i in selected_indexes:
            if i.column() == 0: 
                selected_paths.add(self.explorer.tree_model.filePath(i))
        
        selected_path = self.explorer.tree_model.filePath(index)
        if selected_path not in selected_paths:
            selected_paths.add(selected_path)
        
        global_pos = self.explorer.tree.viewport().mapToGlobal(pos)
        self.show_custom_context_menu(global_pos, selected_paths)

    def show_custom_context_menu(self, global_pos, paths):
        menu = QMenu()
        open_action = QAction('Open')
        reveal_action = QAction('Reveal')
        menu.addAction(open_action)
        menu.addAction(reveal_action)   

        #TODO: handle multiple selection
        if len(paths) == 1:
            path = list(paths)[0]
            open_action.triggered.connect(lambda: self.handle_open(path))
            reveal_action.triggered.connect(lambda: self.handle_reveal(path))
    
        menu.exec(global_pos)
        
def main():

    app = QApplication(sys.argv)
    qdarktheme.setup_theme()

    window = FileSystemTaggingApp()
    window.show()
    
    app.exec()

if __name__ == '__main__':
    main()