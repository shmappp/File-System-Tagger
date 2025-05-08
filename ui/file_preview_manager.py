
from PyQt6.QtWidgets import (
    QStackedWidget, QTextEdit, QLabel
)
from PyQt6.QtGui import QPixmap, QTextOption
from PyQt6.QtCore import Qt

from config import Config

from utils.thumbnail_extractor import get_thumbnail_qimage_ffmpeg

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