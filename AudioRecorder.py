import numpy as np
import speech_recognition as sr
import pyaudiowpatch as pyaudio

RECORD_TIMEOUT = 2
ENERGY_THRESHOLD = 1000
DYNAMIC_ENERGY_THRESHOLD = False

class DefaultMicRecorder:
    def __init__(self):
        self.recorder = sr.Recognizer()
        self.recorder.energy_threshold = ENERGY_THRESHOLD
        self.recorder.dynamic_energy_threshold = DYNAMIC_ENERGY_THRESHOLD
        self.source = sr.Microphone(sample_rate=16000)

        with self.source:
            self.recorder.adjust_for_ambient_noise(self.source)

    def record_into_queue(self, audio_queue):
        def record_callback(_, audio:sr.AudioData) -> None:
            data = audio.get_raw_data()
            audio_queue.put(("You", data, self.source.SAMPLE_RATE, self.source.SAMPLE_WIDTH, 1))

        self.recorder.listen_in_background(self.source, record_callback, phrase_time_limit=RECORD_TIMEOUT)

class DefaultSpeakerRecorder:
    def __init__(self):
        self.recorder = sr.Recognizer()
        self.recorder.energy_threshold = ENERGY_THRESHOLD
        self.recorder.dynamic_energy_threshold = DYNAMIC_ENERGY_THRESHOLD

        with pyaudio.PyAudio() as p:
            wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
            self.default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
            
            if not self.default_speakers["isLoopbackDevice"]:
                for loopback in p.get_loopback_device_info_generator():
                    if self.default_speakers["name"] in loopback["name"]:
                        self.default_speakers = loopback
                        break
                else:
                    print("No loopback device")
        
        self.source = sr.Microphone(sample_rate=int(self.default_speakers["defaultSampleRate"]),
                                speaker=True,
                                chunk_size= pyaudio.get_sample_size(pyaudio.paInt16))
        

    def record_into_queue(self, audio_queue):
        def record_callback(_, audio:sr.AudioData) -> None:
            data = audio.get_raw_data()
            audio_queue.put(("Speaker", data, self.source.SAMPLE_RATE, 
                             self.source.SAMPLE_WIDTH,
                             self.default_speakers["maxInputChannels"]))

        self.recorder.listen_in_background(self.source, record_callback, phrase_time_limit=RECORD_TIMEOUT)