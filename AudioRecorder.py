from typing import Any, Tuple, Optional
import pyaudiowpatch as pyaudio  # type: ignore
from vosk import Model, KaldiRecognizer  # type: ignore
import json
from datetime import datetime
import queue
import os

SAMPLE_RATE = 16000
CHUNK_SIZE = 8000
RECORD_TIMEOUT = 3
MODEL_PATH = "C:/Users/vaski/Downloads/vosk-model-en-us-0.22/vosk-model-en-us-0.22"  # Update this path

class BaseRecorder:
    def __init__(self, source_name: str):
        self.source_name = source_name
        self.model = Model(MODEL_PATH)
        self.rec = KaldiRecognizer(self.model, SAMPLE_RATE)
        self.p = pyaudio.PyAudio()
        self.stream: Optional[pyaudio.Stream] = None
        self.source: Any = None
        self.SAMPLE_RATE = SAMPLE_RATE  # Expose SAMPLE_RATE as an attribute

    def adjust_for_noise(self, device_name: str, msg: str) -> None:
        print(f"[INFO] Adjusting for ambient noise from {device_name}. " + msg)
        # Vosk doesn't have a built-in noise adjustment, so we'll skip this for now
        print(f"[INFO] Completed ambient noise adjustment for {device_name}.")

    def record_into_queue(self, audio_queue: queue.Queue) -> None:
        def record_callback(in_data: bytes, frame_count: int, time_info: dict, status: int) -> Tuple[Optional[bytes], int]:
            audio_queue.put((self.source_name, in_data, datetime.utcnow()))
            return (None, pyaudio.paContinue)

        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=self.SAMPLE_RATE,
                                  input=True,
                                  frames_per_buffer=CHUNK_SIZE,
                                  stream_callback=record_callback)
        self.stream.start_stream()

    def stop_recording(self) -> None:
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()

class DefaultMicRecorder(BaseRecorder):
    def __init__(self):
        super().__init__(source_name="You")
        self.source = pyaudio.PyAudio().open(format=pyaudio.paInt16,
                                             channels=1,
                                             rate=self.SAMPLE_RATE,
                                             input=True,
                                             frames_per_buffer=CHUNK_SIZE)
        self.adjust_for_noise("Default Mic", "Please make some noise from the Default Mic...")

class DefaultSpeakerRecorder(BaseRecorder):
    def __init__(self):
        super().__init__(source_name="Speaker")
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
        
        self.device_index: int = default_speakers["index"]
        self.sample_rate: int = int(default_speakers["defaultSampleRate"])
        self.channels: int = default_speakers["maxInputChannels"]
        
        self.source = pyaudio.PyAudio().open(format=pyaudio.paInt16,
                                             channels=self.channels,
                                             rate=self.sample_rate,
                                             input=True,
                                             input_device_index=self.device_index,
                                             frames_per_buffer=CHUNK_SIZE)
        
        self.adjust_for_noise("Default Speaker", "Please make or play some noise from the Default Speaker...")

    def record_into_queue(self, audio_queue: queue.Queue) -> None:
        def record_callback(in_data: bytes, frame_count: int, time_info: dict, status: int) -> Tuple[Optional[bytes], int]:
            audio_queue.put((self.source_name, in_data, datetime.utcnow()))
            return (None, pyaudio.paContinue)

        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=self.channels,
                                  rate=self.sample_rate,
                                  input=True,
                                  input_device_index=self.device_index,
                                  frames_per_buffer=CHUNK_SIZE,
                                  stream_callback=record_callback)
        self.stream.start_stream()

def process_audio_queue(audio_queue: queue.Queue) -> None:
    rec = KaldiRecognizer(Model(MODEL_PATH), SAMPLE_RATE)
    while True:
        source, audio_data, timestamp = audio_queue.get()
        if rec.AcceptWaveform(audio_data):
            result = json.loads(rec.Result())
            if result['text']:
                print(f"[{source} - {timestamp}] {result['text']}")
        audio_queue.task_done()

# Usage example
if __name__ == "__main__":
    audio_queue: queue.Queue = queue.Queue()
    mic_recorder = DefaultMicRecorder()
    speaker_recorder = DefaultSpeakerRecorder()

    mic_recorder.record_into_queue(audio_queue)
    speaker_recorder.record_into_queue(audio_queue)

    try:
        process_audio_queue(audio_queue)
    except KeyboardInterrupt:
        print("Stopping recording...")
    finally:
        mic_recorder.stop_recording()
        speaker_recorder.stop_recording()