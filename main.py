import os
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QPushButton, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QTreeView, QCompleter, QAbstractItemView, QSplitter, QMenu, QStackedWidget, QTextEdit
)
from PyQt6.QtGui import QColor, QPalette, QFileSystemModel, QPixmap, QAction, QTextOption
from PyQt6.QtCore import QDir, Qt, QModelIndex
import qdarktheme
import sys
import subprocess
import platform
from functools import partial

from packages.thumbnail_extractor import get_thumbnail_qimage_ffmpeg
import packages.json_util as json_util
import packages.tag_util as tag_util

TAG_JSON = os.path.join(os.getcwd(), 'tags.json')

tags = json_util.load_data(TAG_JSON)

class Config:
    DEFAULT_ROOT_PATH = r'C:\Users\Shams\Documents\testdir' #os.path.expanduser('~')
    WINDOW_TITLE = 'File System Tagger'

    WINDOW_GEOMETRY = (100, 100, 1500, 1200)
    WINDOW_BG_COLOR = '#111111' 
    
    TEXT_PREVIEW_MAX_LENGTH = 1000
    IMAGE_PREVIEW_MAX_HEIGHT = 800
    IMAGE_PREVIEW_MAX_WIDTH = 600

class TaggingSystem:
    def __init__(self, tag_json):
        self.tag_json = tag_json
        self.tags = json_util.load_data(tag_json)
    
    def get_tags(self, path):
        return self.tags.get(path, [])

    def set_tags(self, path, tags):
        self.tags[path] = tags
        self.save_tags()
    
    def save_tags(self):
        json_util.save_data(self.tags, self.tag_json)

class TagConfirmButton(QPushButton):
    def __init__(self, tag_system):
        super().__init__()
        self.confirming = False
        self.default_text = 'Update tags'
        self.confirm_text = 'Confirm empty tags?'
        self.setText(self.default_text)
        self.tag_display = None
        self.tag_system = tag_system
        self.clicked.connect(self.on_click)
     
    def set_tag_display(self, tag_display):
        self.tag_display = tag_display
    
    def set_path(self, path):
        self.path = path

    def on_click(self):
        if self.tag_display is None or self.path is None:
            return
        
        tag_text = self.tag_display.toPlainText()
        extracted_tags = tag_util.extract_tags(tag_text)
        
        if extracted_tags or self.confirming:
            self.tag_system.set_tags(self.path, extracted_tags)
            self.reset()
        else:
            self.setText(self.confirm_text)
            self.confirming = True

    def reset(self):
        self.setText(self.default_text)
        self.confirming = False
        
class CustomFileSystemModel(QFileSystemModel):
    def __init__(self, tag_system):
        super().__init__()
        self.tag_system = tag_system

    def columnCount(self, parent = QModelIndex()):
        return super().columnCount(parent) + 1

    def data(self, index, role):
        if not index.isValid():
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == self.columnCount() - 1:
                file_path = self.filePath(index)
                file_info = self.fileInfo(index)
                if file_info.isFile():
                    tags = self.tag_system.get_tags(file_path)
                    return f'{tags}' # TODO: beautify tag display
            else:
                return super().data(index, role)
        elif role == Qt.ItemDataRole.DecorationRole:
            return super().data(index, role)
        return None

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
        #self.tree.customContextMenuRequested.connect(self.on_tree_context_menu)

        #self.tree.selectionModel().currentChanged.connect(self.on_tree_selection_changed)
        #self.tree.clicked.connect(self.file_selected)
        #self.tree.selectionModel().currentChanged.connect(self.file_selected) # optional, allows arrow keys to preview
        #self.tree.doubleClicked.connect(self.open_selected_file)

        # path field
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText('Enter full path and press Enter')
        #self.path_input.returnPressed.connect(self.navigate_to_path)
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
    
class FilePreviewManager:
    def __init__(self):
        # preview widget
        self.preview_stack = QStackedWidget()

        self.text_preview = QTextEdit()
        self.text_preview.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        self.text_preview.setReadOnly(True)

        self.image_preview = QLabel('Preview')
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.preview_stack.addWidget(self.text_preview)
        self.preview_stack.addWidget(self.image_preview)
    
    def display_preview(self, path):
        if path.lower().endswith(('.txt', '.md', '.log')):
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
                self.text_preview.setText(text[:1000])
            self.preview_stack.setCurrentWidget(self.text_preview)
            return
        
        pixmap = None
        if path.lower().endswith(('.mp4', '.mkv', '.mov', '.webm', '.m4a')):
            qimage = get_thumbnail_qimage_ffmpeg(path)
            if qimage:
                pixmap = QPixmap.fromImage(qimage.copy())
        elif path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            pixmap = QPixmap(path)

        if pixmap:
            if pixmap.width() > 600:
                pixmap = pixmap.scaledToWidth(Config.IMAGE_PREVIEW_MAX_WIDTH)
            if pixmap.height() > 800:
                pixmap = pixmap.scaledToHeight(Config.IMAGE_PREVIEW_MAX_HEIGHT)
            self.image_preview.setPixmap(pixmap)
            self.preview_stack.setCurrentWidget(self.image_preview)
        else:
            self.text_preview.setText('No preview available')
            self.preview_stack.setCurrentWidget(self.text_preview)
    
    def get_widget(self):
        return self.preview_stack

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