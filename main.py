import os
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QPushButton, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QTreeView, QCompleter, QAbstractItemView, QSplitter, QMenu, QStackedWidget, QTextEdit
)
from PyQt6.QtGui import QColor, QPalette, QFileSystemModel, QPixmap, QAction, QTextOption
from PyQt6.QtCore import QDir, Qt, QModelIndex
import packages.json_util as json_util
import qdarktheme
from packages.thumbnail_extractor import get_thumbnail_pixmap_ffmpeg
import sys

DATA_JSON = os.path.join(os.getcwd(), 'tags.json')

tags = json_util.load_data(DATA_JSON)

class CustomFileSystemModel(QFileSystemModel):
    def __init__(self):
        super().__init__()

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
                    return f'{tags.get(file_path, [])}' # TODO: beautify tag display
            else:
                return super().data(index, role)
        elif role == Qt.ItemDataRole.DecorationRole:
            return super().data(index, role)
        return None
    
class MainWindow(QMainWindow):
    def navigate_to_path(self):
        path = self.path_input.text()

        if not os.path.exists(path):
            print('Path does not exist')
            return

        index = self.tree_model.index(path)
        if index.isValid():
            self.tree.setRootIndex(index) #optional: dynamic root traversal
            self.tree.expand(index.parent())
            self.tree.setCurrentIndex(index)
            self.tree.scrollTo(index)
        else:
            print(f'Navigation to {path} failed')
    
    def on_tree_selection_changed(self, current, previous):
        current_path = self.tree_model.filePath(current)
        self.path_input.setText(current_path)

    def display_preview(self, path):
        if path.lower().endswith(('.txt', '.md', '.log')):
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
                self.text_preview.setText(text[:1000])
            self.preview_stack.setCurrentWidget(self.text_preview)
            return
        
        pixmap = None
        if path.lower().endswith(('.mp4', '.mkv', '.mov', '.webm')):
            qimage = get_thumbnail_pixmap_ffmpeg(path)
            if qimage:
                pixmap = QPixmap.fromImage(qimage.copy())
        elif path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            pixmap = QPixmap(path)
        if pixmap:
            if pixmap.width() > 800:
                pixmap = pixmap.scaledToWidth(800)
            self.image_preview.setPixmap(pixmap)
            self.preview_stack.setCurrentWidget(self.image_preview)
        else:
            self.text_preview.setText('No preview available')
            self.preview_stack.setCurrentWidget(self.text_preview)

    def file_selected(self, index):
        path = self.tree_model.filePath(index)
        if os.path.isfile(path):
            self.display_preview(path)
    
    def handle_open(self, path):
        os.startfile(path)

    def show_custom_context_menu(self, global_pos, paths):
        menu = QMenu()
        open_action = QAction('Open')
        menu.addAction(open_action)
        
        if len(paths) == 1:
            open_action.triggered.connect(lambda: self.handle_open(list(paths)[0]))
    
        menu.exec(global_pos)

    def on_tree_context_menu(self, pos):
        index = self.tree.indexAt(pos)
        if not index.isValid():
            return
        selected_indexes = self.tree.selectionModel().selectedIndexes()
        selected_paths = set()
        for i in selected_indexes:
            if i.column() == 0: 
                selected_paths.add(self.tree_model.filePath(i))
        
        selected_path = self.tree_model.filePath(index)
        if selected_path not in selected_paths:
            selected_paths.add(selected_path)
        
        global_pos = self.tree.viewport().mapToGlobal(pos)
        self.show_custom_context_menu(global_pos, selected_paths)


    def __init__(self):
        super().__init__()

        self.root_path = os.path.expanduser('~')

        # workspace setup
        self.setWindowTitle('File System Tagger')
        self.setGeometry(100, 100, 1500, 1200)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor('#111111'))
        self.setPalette(palette)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        central_widget.setLayout(QVBoxLayout())
        central_widget.layout().addWidget(splitter)


        # explorer layout
        explorer_widget = QWidget()
        explorer_layout = QVBoxLayout(explorer_widget)

        # explorer tree view
        self.tree_model = CustomFileSystemModel()
        self.tree_model.setRootPath(self.root_path)
        self.root_index = self.tree_model.index(self.root_path) #TODO: replace
        self.tree = QTreeView()
        self.tree.setModel(self.tree_model)
        self.tree.setColumnWidth(0, 300)
        self.tree.setRootIndex(self.root_index)
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.on_tree_context_menu)

        self.tree.selectionModel().currentChanged.connect(self.on_tree_selection_changed)
        self.tree.clicked.connect(self.file_selected)
        #self.tree.selectionModel().currentChanged.connect(self.file_selected) # optional, allows arrow keys to preview
        
        # path field
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText('Enter full path and press Enter')
        self.path_input.returnPressed.connect(self.navigate_to_path)
        self.path_input.setText(self.root_path) # default to root

        # path field completion logic
        self.completer_model = QFileSystemModel()
        self.completer_model.setRootPath(self.root_path)

        completer = QCompleter(self.completer_model, self.path_input)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchStartsWith)
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)

        self.path_input.setCompleter(completer)

        # add widgets to explorer layout
        explorer_layout.addWidget(self.path_input)
        explorer_layout.addWidget(self.tree)

        # add explorer layout to main layout
        splitter.addWidget(explorer_widget)

        # actions layout
        actions_widget = QWidget()
        actions_layout = QVBoxLayout(actions_widget)

        self.preview_stack = QStackedWidget()

        self.text_preview = QTextEdit()
        self.text_preview.setWordWrapMode(QTextOption.WrapMode.WordWrap)

        self.image_preview = QLabel('Preview')
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.preview_stack.addWidget(self.text_preview)
        self.preview_stack.addWidget(self.image_preview)

        # add widgets to actions layout
        actions_layout.addWidget(self.preview_stack)

        # add actions layout to main layout
        splitter.addWidget(actions_widget)
        
        




app = QApplication(sys.argv)
qdarktheme.setup_theme()
window = MainWindow()
window.show()
app.exec()