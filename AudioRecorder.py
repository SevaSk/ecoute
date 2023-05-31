import custom_speech_recognition as sr
from datetime import datetime
import os
import sounddevice as sd

if os.name == 'nt':
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
        if os.name == 'nt':
            with pyaudio.PyAudio() as p:
                wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
                self.default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
                if not default_speakers["isLoopbackDevice"]:
                    for loopback in p.get_loopback_device_info_generator():
                        if default_speakers["name"] in loopback["name"]:
                            default_speakers = loopback
                            break
                    else:
                        print("[ERROR] No loopback device found.")
        else:
            self.default_device_index = 1
            p = pyaudio.PyAudio()
            self.default_speakers = p.get_device_info_by_index(self.default_device_index)
        self.set_source()
    def set_source(self):
        source = sr.Microphone(speaker=True,
                               device_index= self.default_speakers["index"],
                               sample_rate=int(self.default_speakers["defaultSampleRate"]),
                               chunk_size=pyaudio.get_sample_size(pyaudio.paInt16),
                               channels=self.default_speakers["maxInputChannels"])
        super().__init__(source=source, source_name="Speaker")
        self.adjust_for_noise("Default Speaker", "Please make or play some noise from the Default Speaker...")
    def list_audio_devices(self):
        if os.name == 'nt':
            pass
        else:
            # Get information about all available devices
            devices = sd.query_devices()
        
            # Extract device names into a list
            return [device['name'] for device in devices]
    def set_default_speaker(self,selected_speaker):
        
        # Retrieve information about all available audio devices
        devices = sd.query_devices()

        # Iterate over devices and find the index of the matching device name
        for index, device in enumerate(devices):
            if device['name'] == selected_speaker:
                self.default_device_index = index
                self.set_source()
                break

     
