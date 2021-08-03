import threading
import logging
from picamera import PiCamera, Color

log = logging.getLogger()

ANNOTATION_TEXT = "NACISNIJ PRZYCISK ABY NAGRAC ZYCZENIA, (MAX 60s)"


class VideoRecorder:
    def __init__(self, preview=True):
        self.lock = threading.Lock()
        self.camera = PiCamera()
        self.camera.resolution = (1920, 1080)  # (640, 480)
        self.camera.framerate = 25
        self.camera.rotation = 180
        self.camera.annotate_background = Color('red')
        self.camera.annotate_foreground = Color('white')
        self.camera.annotate_text_size = 70
        self.camera.annotate_text = ANNOTATION_TEXT
        if preview:
            self.camera.start_preview()
        
    def start(self, file_name, file_dir):
        self.lock.acquire()
        file_name = f"{file_dir}/{file_name}.h264"
        self.camera.annotate_text = ""
        log.info('starting video recording: %s', file_name)
        video_thread = threading.Thread(target=self.camera.start_recording, args=(file_name,))
        video_thread.start()
        
    def stop(self):
        if self.lock.locked():
            self.lock.release()
            self.camera.stop_recording()
            self.camera.annotate_text = ANNOTATION_TEXT
            return True
        else:
            return False
