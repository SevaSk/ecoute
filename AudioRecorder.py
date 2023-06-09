import custom_speech_recognition as sr
import os
from datetime import datetime

try:
    import pyaudiowpatch as pyaudio
except ImportError:
    if os.name != "nt":
        import pyaudio
    else:
        raise

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
    
    # Different implementations of obtaining the info dict of a default speaker, for different platforms
    if os.name == "nt":
        def _get_default_speaker(self):
            # Requires PyAudioWPatch >= 0.2.12.6
            with pyaudio.PyAudio() as p:
                try:
                    # Get loopback of default WASAPI speaker
                    return p.get_default_wasapi_loopback()
        
                except OSError:                
                    print("[ERROR] Looks like WASAPI is not available on the system.")
        
                except LookupError:
                    print("[ERROR] No loopback device found.")
    else:
        def _get_default_speaker(self):
            # At the moment, recording from speakers is only available under Windows
            # raise NotImplementedError("Recording from speakers is only available under Windows")
            
            # As far as I understand, now the code style does not provide
            # for error handling - only print them.
            print("[ERROR] Recording from speakers is only available under Windows.")
            p = pyaudio.PyAudio()
            
            try:
                # This just a stub
                return p.get_default_output_device_info()
            finally:
                p.terminate()
            
    def __init__(self):
        default_speaker = self._get_default_speaker()
        
        if not default_speaker:
            print("[ERROR] Something went wrong while trying to get the default speakers.")
            return
        
        source = sr.Microphone(speaker=True,
                               device_index=default_speaker["index"],
                               sample_rate=int(default_speaker["defaultSampleRate"]),
                               chunk_size=pyaudio.get_sample_size(pyaudio.paInt16),
                               channels=default_speaker["maxInputChannels"])
        super().__init__(source=source, source_name="Speaker")
        self.adjust_for_noise("Default Speaker", "Please make or play some noise from the Default Speaker...")
