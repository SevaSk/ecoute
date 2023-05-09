import soundcard as sc
from Microphone import Microphone
import pythoncom

RECORDING_TIME = 5
SAMPLE_RATE = 16000

class AudioRecorder:
    def __init__(self, microphone : Microphone):
        self.microphone = microphone

    def record_into_queue(self, audio_queue, source):
        pythoncom.CoInitialize()
        with sc.get_microphone(id=self.microphone.id, include_loopback=self.microphone.loop_back).recorder(samplerate=SAMPLE_RATE) as mic:
            while True:
                data = mic.record(numframes=SAMPLE_RATE*RECORDING_TIME) # data is a frames x channels Numpy array.
                audio_queue.put((source, data))