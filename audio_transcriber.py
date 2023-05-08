import numpy as np
import soundcard as sc
import threading
import time
import queue
import whisper
import torch
import argparse
import wave
import os
from Microphone import Microphone

TRANSCRIPT_LIMIT = 10
RECORDING_TIME = 5

class AudioTranscriber:
    def __init__(self, lang: str, microphone : Microphone):
        self.audio_np_array_queue = queue.Queue()
        self.status = 'Running'
        self.transcript_data = []
        self.microphone = microphone
        self.lang = lang
        self.lock = threading.Lock()
        self.start_time = time.time()  # Record the start time
        parser = argparse.ArgumentParser()
        parser.add_argument("--model", default="tiny", help="Model to use",
                            choices=["tiny", "base", "small", "medium", "large"])
        parser.add_argument("--non_english", action='store_true',
                            help="Don't use the english model.")
        parser.add_argument("--energy_threshold", default=1000,
                            help="Energy level for mic to detect.", type=int)
        parser.add_argument("--record_timeout", default=2,
                            help="How real time the recording is in seconds.", type=float)
        parser.add_argument("--phrase_timeout", default=3,
                            help="How much empty space between recordings before we "
                                 "consider it a new line in the transcription.", type=float)  
        args = parser.parse_args()
        # Load / Download model
        model = args.model
        if args.model != "large" and not args.non_english:
            model = model + ".en"
        self.audio_model = whisper.load_model(os.getcwd() + r'\tiny.en' + '.pt')

    def get_transcript(self):
        return self.transcript_data

    def record_into_queue(self):
        SAMPLE_RATE = 16000
        with sc.get_microphone(id=self.microphone.id, include_loopback=self.microphone.loop_back).recorder(samplerate=SAMPLE_RATE) as mic:
            while True:
                data = mic.record(numframes=SAMPLE_RATE*RECORDING_TIME) # data is a frames x channels Numpy array.
                self.audio_np_array_queue.put(data)
            return

    def transcribe_from_queue(self):
        with self.lock:
            while True:
                audio_data = self.audio_np_array_queue.get()
                with wave.open(f'temp_{self.microphone.id}.wav', 'wb') as wav_file:
                    wav_file.setnchannels(audio_data.shape[1])
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(16000)
                    audio_data = (audio_data * (2**15 - 1)).astype(np.int16)
                    wav_file.writeframes(audio_data.tobytes())
                result = self.audio_model.transcribe(f'temp_{self.microphone.id}.wav', fp16=torch.cuda.is_available())
                text = result['text'].strip()
                if text != '' and text.lower() != 'you': # whisper gives "you" on many null inputs
                    timestamp = int(time.time())
                    self.transcript_data.append({'utterance': text, 'timestamp': timestamp})