import threading
import logging
from picamera import PiCamera, Color

log = logging.getLogger()

ANNOTATION_TEXT = "NACISNIJ PRZYCISK ABY NAGRAC ZYCZENIA"


class VideoRecorder:
    def __init__(self, preview=True):
        self.camera = PiCamera()
        self.camera.resolution = (640, 480)
        self.camera.framerate = 25
        self.camera.rotation = 0 #180
        self.camera.annotate_background = Color('red')
        self.camera.annotate_foreground = Color('white')
        self.camera.annotate_text_size = 30
        self.camera.annotate_text = ANNOTATION_TEXT
        if preview:
            self.camera.start_preview()
        
    def start(self, file_name, file_dir):
        file_name = f"{file_dir}/{file_name}.h264"
        self.camera.annotate_text = ""
        log.info('starting video recording: %s', file_name)
        video_thread = threading.Thread(target=self.camera.start_recording, args=(file_name,))
        video_thread.start()
        
    def stop(self):
        self.camera.stop_recording()
        self.camera.annotate_text = ANNOTATION_TEXT
