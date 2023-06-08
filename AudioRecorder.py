import custom_speech_recognition as sr
import os
from datetime import datetime

if os.name == "nt":
    import pyaudiowpatch as pyaudio
else:
    import pyaudio


RECORD_TIMEOUT = 3
ENERGY_THRESHOLD = 1000
DYNAMIC_ENERGY_THRESHOLD = False

class BaseRecorder:
    def __init__(self, source, source_name):
        self.recorder = sr.Recognizer()
        self.recorder.energy_threshold = ENERGY_THRESHOLD
        self.recorder.dynamic_energy_threshold = DYNAMIC_ENERGY_THRESHOLD

        if source is None:
            raise ValueError("audio source can't be None")

        self.source = source
        self.source_name = source_name

    def adjust_for_noise(self, device_name, msg):
        print(f"[INFO] Adjusting for ambient noise from {device_name}. " + msg)
        with self.source:
            self.recorder.adjust_for_ambient_noise(self.source)
        print(f"[INFO] Completed ambient noise adjustment for {device_name}.")

    def record_into_queue(self, audio_queue):
        def record_callback(_, audio:sr.AudioData) -> None:
            data = audio.get_raw_data()
            audio_queue.put((self.source_name, data, datetime.utcnow()))

        self.recorder.listen_in_background(self.source, record_callback, phrase_time_limit=RECORD_TIMEOUT)

class DefaultMicRecorder(BaseRecorder):
    def __init__(self):
        super().__init__(source=sr.Microphone(sample_rate=16000), source_name="You")
        self.adjust_for_noise("Default Mic", "Please make some noise from the Default Mic...")

class DefaultSpeakerRecorder(BaseRecorder):
    def __init__(self):
        #with pyaudio.PyAudio() as p:
        p = pyaudio.PyAudio() 
        try:
            if os.name == "nt":
                wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
            else:
                wasapi_info = p.get_host_api_info_by_type(pyaudio.paCoreAudio)

            default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
            isLoopbackDevice = False
            if os.name == "nt":
                isLoopbackDevice = default_speakers["isLoopbackDevice"]
            else:
                isLoopbackDevice = default_speakers.get("isLoopbackDevice", False)
            if not isLoopbackDevice:
                if os.name != "nt":
                    for i in range(p.get_device_count()):
                        device_info = p.get_device_info_by_index(i)
                        if device_info['maxInputChannels'] > 0 and device_info['hostApi'] == p.get_default_host_api_info()['index']:
                            default_speakers = loopback = device_info
                            break
                        else:
                            print("[ERROR] No loopback device found.")

                else:
                    for loopback in p.get_loopback_device_info_generator():
                        if default_speakers["name"] in loopback["name"]:
                            default_speakers = loopback
                            break
                    else:
                        print("[ERROR] No loopback device found.")
        finally:
            p.terminate()
        source = sr.Microphone(speaker=True,
                               device_index= default_speakers["index"],
                               sample_rate=int(default_speakers["defaultSampleRate"]),
                               chunk_size=pyaudio.get_sample_size(pyaudio.paInt16),
                               channels=default_speakers["maxInputChannels"])
        super().__init__(source=source, source_name="Speaker")
        self.adjust_for_noise("Default Speaker", "Please make or play some noise from the Default Speaker...")
