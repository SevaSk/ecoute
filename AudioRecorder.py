import custom_speech_recognition as sr
import pyaudiowpatch as pyaudio
from datetime import datetime

RECORD_TIMEOUT = 3
ENERGY_THRESHOLD = 1000
DYNAMIC_ENERGY_THRESHOLD = False

class BaseRecorder:
    def __init__(self, source, num_channels, source_name):
        self.recorder = sr.Recognizer()
        self.recorder.energy_threshold = ENERGY_THRESHOLD
        self.recorder.dynamic_energy_threshold = DYNAMIC_ENERGY_THRESHOLD
        self.source = source
        self.num_channels = num_channels
        self.source_name = source_name

    def adjust_for_noise(self):
        print(f"[INFO] Adjusting for ambient noise from {self.source_name}. Please make some noise...")
        with self.source:
            self.recorder.adjust_for_ambient_noise(self.source)
        print(f"[INFO] Completed ambient noise adjustment for {self.source_name}.")

    def record_into_queue(self, audio_queue):
        def record_callback(_, audio:sr.AudioData) -> None:
            data = audio.get_raw_data()
            audio_queue.put((self.source_name, data, datetime.utcnow()))

        self.recorder.listen_in_background(self.source, record_callback, phrase_time_limit=RECORD_TIMEOUT)

class DefaultMicRecorder(BaseRecorder):
    def __init__(self):
        super().__init__(source=sr.Microphone(sample_rate=16000), num_channels=1, source_name="You")
        self.adjust_for_noise()

class DefaultSpeakerRecorder(BaseRecorder):
    def __init__(self):
        with pyaudio.PyAudio() as p:
            wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
            default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
            
            if not default_speakers["isLoopbackDevice"]:
                for loopback in p.get_loopback_device_info_generator():
                    if default_speakers["name"] in loopback["name"]:
                        default_speakers = loopback
                        break
                else:
                    print("[ERROR] No loopback device found.")
        
        source = sr.Microphone(sample_rate=int(default_speakers["defaultSampleRate"]),
                                speaker=True,
                                chunk_size=pyaudio.get_sample_size(pyaudio.paInt16))
        super().__init__(source=source, num_channels=default_speakers["maxInputChannels"], source_name="Speaker")
        self.adjust_for_noise()