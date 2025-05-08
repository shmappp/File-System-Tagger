
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtCore import Qt, QModelIndex

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