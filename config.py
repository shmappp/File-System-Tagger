import os

class Config:
    DEFAULT_ROOT_PATH = os.path.expanduser('~')
    WINDOW_TITLE = 'File System Tagger'

    WINDOW_GEOMETRY = (100, 100, 1500, 1200)
    WINDOW_BG_COLOR = '#111111' 
    
    TEXT_PREVIEW_MAX_LENGTH = 1000
    IMAGE_PREVIEW_MAX_HEIGHT = 800
    IMAGE_PREVIEW_MAX_WIDTH = 600
