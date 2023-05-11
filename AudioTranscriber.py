import numpy as np
import whisper
import torch
import wave
import os
import threading
from tempfile import NamedTemporaryFile
import speech_recognition as sr
import io
from datetime import datetime, timedelta
from time import sleep
import pyaudiowpatch as pyaudio

PHRASE_TIMEOUT = 3

class AudioTranscriber:
    def __init__(self):
        self.transcript_data = [""]
        self.transcript_changed_event = threading.Event()
        self.audio_model = whisper.load_model(os.getcwd() + r'\tiny.en' + '.pt')

    def create_transcription_from_queue(self, audio_queue):
        phrase_time = None
        last_sample = bytes()

        who_spoke_changed = False
        who_spoke_prev = "You"
        sample_prev = bytes()
        sample_rate_prev = 16000
        sample_width_prev = 2
        channels_prev = 1

        while True:
            now = datetime.utcnow()

            if not audio_queue.empty():
                phrase_complete = False
                if phrase_time and now - phrase_time > timedelta(seconds=PHRASE_TIMEOUT) or who_spoke_changed:
                    if who_spoke_changed:
                        who_spoke_changed = False
                        last_sample = sample_prev
                        who_spoke = who_spoke_prev
                        sample_rate = sample_rate_prev
                        sample_width = sample_width_prev
                        channels = channels_prev
                    else:
                        last_sample = bytes()

                    phrase_complete = True
                phrase_time = now

                while not audio_queue.empty() and not who_spoke_changed:
                    top_of_queue = audio_queue.get()
                    who_spoke = top_of_queue[0]
                    data = top_of_queue[1]
                    sample_rate = top_of_queue[2]
                    sample_width = top_of_queue[3]
                    channels = top_of_queue[4]

                    who_spoke_changed = who_spoke != who_spoke_prev
                    if who_spoke_changed:
                        sample_prev = data
                        who_spoke_prev = who_spoke
                        sample_rate_prev = sample_rate
                        sample_width_prev = sample_width
                        channels_prev = channels
                        break
                    else:
                        last_sample += data

                temp_file = NamedTemporaryFile().name

                if who_spoke == "You":
                    audio_data = sr.AudioData(last_sample, sample_rate, sample_width)
                    wav_data = io.BytesIO(audio_data.get_wav_data())
                    with open(temp_file, 'w+b') as f:
                        f.write(wav_data.read())
                else:
                    with wave.open(temp_file, 'wb') as wf:
                        wf.setnchannels(channels)
                        p = pyaudio.PyAudio()
                        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
                        wf.setframerate(sample_rate)
                        wf.writeframes(last_sample)

                result = self.audio_model.transcribe(temp_file, fp16=torch.cuda.is_available())
                text = result['text'].strip()

                if phrase_complete:
                    self.transcript_data = [who_spoke + ": [" + text + ']\n\n'] + self.transcript_data
                else:
                    self.transcript_data[0] = who_spoke + ": [" + text + ']\n\n'
            sleep(0.25)

    def get_transcript(self):
        return "".join(self.transcript_data)
    