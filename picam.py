import argparse
import datetime
import logging
import os
import time
import threading
import shutil
import subprocess
import tempfile

# from pynput import keyboard
from gpiozero import Button
from signal import pause

from audio_recorder import AudioRecorder
from video_recorder import VideoRecorder


logging.basicConfig(
    format='[%(threadName)s] %(asctime)s: %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S',
    level=logging.DEBUG
)
log = logging.getLogger()
MIN_DISK_SPACE_MB = 100
MAX_VIDEO_LENGTH = 10


class App:
    def __init__(self, preview=False, max_video_length=MAX_VIDEO_LENGTH):
        log.info("booting up..")
        self.final_dir = self._setup_dirs()
        self.max_video_length = max_video_length
        self.video_recorder = VideoRecorder(preview=preview)
        self.audio_recorder = AudioRecorder()
        time.sleep(2)
        log.info("ready!")

    def _setup_dirs(self):
        final_dir = os.path.expanduser('~/media/')
        if(os.path.isdir(final_dir) == False):
            os.mkdir(final_dir)
        return final_dir
    
    def _make_filename(self):
        return datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    
    def has_space(self):
        statvfs = os.statvfs("/")
        megabytes_available = int(statvfs.f_frsize * statvfs.f_bavail / 1024 / 1024)
        log.info(f"Still {megabytes_available}MB left on device")
        return megabytes_available > MIN_DISK_SPACE_MB
    
    def on_keyboard_release(self, key):
        if key == keyboard.Key.enter:
            if lock.locked():
                self.stop_recording()
            elif self.has_space():
                self.start_recording()  
            else:
                return False
        if key == keyboard.Key.esc:
            if lock.locked():
                self.stop_recording()
            return False
    
    def timer(self, seconds=MAX_VIDEO_LENGTH):
        log.info(f"going to sleep for {seconds}s and then stop recording")
        for i in range(seconds):
            if not lock.locked():
                log.info("looks like recording has ended before timeout")
                return
            time.sleep(1)
        log.info("time's up!, stopping recording")
        self.stop_recording()

    def start_recording(self):
        lock.acquire()
        timer_thread = threading.Thread(target=self.timer, args=(self.max_video_length,))
        timer_thread.start()
        self.tmp_dir = tempfile.mkdtemp()
        self.file_name = self._make_filename()
        
        log.info("starting threads...")   
        self.video_recorder.start(self.file_name, self.tmp_dir)
        self.audio_recorder.start(self.file_name, self.tmp_dir)

    def stop_recording(self, mux=True):
        log.info("stopping threads...")
        self.audio_recorder.stop()
        self.video_recorder.stop()
        if mux:
            log.info("starting mux...")
            cmd = (
                f"ffmpeg -i {self.tmp_dir}/{self.file_name}.wav -i {self.tmp_dir}/{self.file_name}.h264 "
                f"-c:v copy -c:a aac -strict experimental {self.final_dir}/{self.file_name}.mp4"
            )
            subprocess.run(cmd, capture_output=True, shell=True)
            log.info(f"{self.file_name}.mp4 is ready!")
        shutil.rmtree(self.tmp_dir)
        log.info(f"{self.tmp_dir} removed")
        lock.release()
    
    def run(self):
        def on_release(button):
            if lock.locked():
                self.stop_recording()
            elif self.has_space():
                self.start_recording()  
            else:
                return False
            
        button = Button(2)
        button.when_released = on_release
        pause()
        # listener = keyboard.Listener(on_release=self.on_keyboard_release)
        # listener.start()
        # listener.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audio&Video recorder")
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--max-video-length", type=int)
    args = parser.parse_args()
    
    lock = threading.Lock()
    app = App(preview=args.preview, max_video_length=args.max_video_length)
    app.run()
