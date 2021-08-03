import threading
import logging
from picamera import PiCamera, Color
from PIL import Image

log = logging.getLogger()

ANNOTATION_TEXT = "NACISNIJ PRZYCISK ABY NAGRAC ZYCZENIA, (MAX 60s)"


class VideoRecorder:
    def __init__(self, preview=True):
        self.lock = threading.Lock()
        self.camera = PiCamera()
        self.camera.resolution = (1920, 1080)  # (640, 480)
        self.camera.framerate = 25
        self.camera.rotation = 180
        #self.camera.annotate_background = Color('red')
        #self.camera.annotate_foreground = Color('white')
        #self.camera.annotate_text_size = 70
        #self.camera.annotate_text = ANNOTATION_TEXT
        
        self.overlay_img = Image.open('overlay.png')
        if preview:
            self.camera.start_preview()
            self.add_overlay()

    def add_overlay(self):
        self.overlay = self.camera.add_overlay(
            self.overlay_img.tobytes(), size=self.overlay_img.size, 
            alpha=0, layer=3
        )
        
    def remove_overlay(self):
        self.camera.remove_overlay(self.overlay)
        
    def start(self, file_name, file_dir):
        self.lock.acquire()
        file_name = f"{file_dir}/{file_name}.h264"
        # self.camera.annotate_text = ""
        self.remove_overlay()
        log.info('starting video recording: %s', file_name)
        video_thread = threading.Thread(target=self.camera.start_recording, args=(file_name,))
        video_thread.start()
        
    def stop(self):
        if self.lock.locked():
            self.lock.release()
            self.camera.stop_recording()
            self.add_overlay()
            # self.camera.annotate_text = ANNOTATION_TEXT
            return True
        else:
            return False
