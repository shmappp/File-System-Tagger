import subprocess
from PyQt6.QtGui import QImage
from PIL import Image
import io
import numpy as np

def get_thumbnail_qimage_ffmpeg(video_path, time_position = '00:00:01'):
    try:
        result = subprocess.run(
            [
                'ffmpeg',
                '-ss', time_position,          # seek to 1 second (or any time)
                '-i', video_path,              # input file
                '-frames:v', '1',              # grab only one frame
                '-f', 'image2pipe',            # output as image stream
                '-vcodec', 'mjpeg',            # JPEG format
                'pipe:1'                       # output to stdout
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL  # suppress ffmpeg logging
        )

        if result.returncode != 0:
            return None

        image = Image.open(io.BytesIO(result.stdout)).convert('RGB')
        img_array = np.array(image)
        height, width, channels = img_array.shape
        bytes_per_line = channels*width
        qimage = QImage(img_array.data, width, height, bytes_per_line, QImage.Format.Format_RGB888).copy()
        return qimage

    except Exception as e:
        print('Error extracting thumbnail:', e)
        return None