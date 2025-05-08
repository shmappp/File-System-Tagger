from PyQt6.QtWidgets import (
    QPushButton
) 

import utils.tag_util as tag_util

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