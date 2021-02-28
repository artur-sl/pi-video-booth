import logging
import threading
import queue
import sounddevice as sd
import soundfile as sf
import os

log = logging.getLogger()


class AudioRecorder:

    def __init__(self):
        self.lock = threading.Lock()
        self.channels = 1
        self.q = queue.Queue()
        
        # Get samplerate
        device_info = sd.query_devices(2, 'input')
        self.samplerate = int(device_info['default_samplerate'])

    def callback(self, indata, frames, time, status):
        # This is called (from a separate thread) for each audio block.
        if status:
            log.error(status)
        self.q.put(indata.copy())

    def record(self, file_name):
        log.info('starting audio recording: %s, rate: %d, channels: %d', file_name, self.samplerate, self.channels)
        with sf.SoundFile(file_name, mode='x', samplerate=self.samplerate, channels=self.channels) as file:
            with sd.InputStream(samplerate=self.samplerate, channels=self.channels, callback=self.callback):
                while(self.lock.locked()):
                    file.write(self.q.get())

    def stop(self):
        self.lock.release()

    def start(self, file_name, file_dir):
        self.lock.acquire()
        file_name = f"{file_dir}/{file_name}.wav"
        
        audio_thread = threading.Thread(target=self.record, args=(file_name, ))
        audio_thread.start()