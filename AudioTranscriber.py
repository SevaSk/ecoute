import whisper
import torch
import wave
import os
import threading
from tempfile import NamedTemporaryFile
import custom_speech_recognition as sr
import io
from datetime import timedelta
import pyaudiowpatch as pyaudio
from AudioRecorder import DefaultMicRecorder, DefaultSpeakerRecorder
from heapq import merge

PHRASE_TIMEOUT = 3.01

MAX_PHRASES = 10

class AudioTranscriber:
    def __init__(self, default_mic : DefaultMicRecorder, default_speaker : DefaultSpeakerRecorder):
        self.transcript_data = {"You": [], "Speaker": []}
        self.transcript_changed_event = threading.Event()
        self.audio_model = whisper.load_model(os.path.join(os.getcwd(), 'tiny.en.pt'))
        self.audio_sources = {
            "You": {
                "sample_rate": default_mic.source.SAMPLE_RATE,
                "sample_width": default_mic.source.SAMPLE_WIDTH,
                "channels": default_mic.num_channels,
                "last_sample": bytes(),
                "last_spoken": None,
                "new_phrase": True,
                "process_data_func": self.process_mic_data
            },
            "Speaker": {
                "sample_rate": default_speaker.source.SAMPLE_RATE,
                "sample_width": default_speaker.source.SAMPLE_WIDTH,
                "channels": default_speaker.num_channels,
                "last_sample": bytes(),
                "last_spoken": None,
                "new_phrase": True,
                "process_data_func": self.process_speaker_data
            }
        }

    def transcribe_audio_queue(self, audio_queue):
        while True:
            who_spoke, data, time_spoken = audio_queue.get()
            source_info = self.audio_sources[who_spoke]

            self.update_last_sample_and_phrase_status(who_spoke, data, time_spoken)
            temp_file = source_info["process_data_func"](source_info["last_sample"])
            text = self.get_transcription(temp_file)

            if text != '' and text.lower() != 'you':
                self.update_transcript(who_spoke, text, time_spoken)
                self.transcript_changed_event.set()

    def update_last_sample_and_phrase_status(self, who_spoke, data, time_spoken):
        source_info = self.audio_sources[who_spoke]
        if source_info["last_spoken"] and time_spoken - source_info["last_spoken"] > timedelta(seconds=PHRASE_TIMEOUT):
            source_info["last_sample"] = bytes()
            source_info["new_phrase"] = True
        else:
            source_info["new_phrase"] = False

        source_info["last_sample"] += data
        source_info["last_spoken"] = time_spoken 

    def process_mic_data(self, data):
        temp_file = NamedTemporaryFile().name
        audio_data = sr.AudioData(data, self.audio_sources["You"]["sample_rate"], self.audio_sources["You"]["sample_width"])
        wav_data = io.BytesIO(audio_data.get_wav_data())
        with open(temp_file, 'w+b') as f:
            f.write(wav_data.read())
        return temp_file

    def process_speaker_data(self, data):
        temp_file = NamedTemporaryFile().name
        with wave.open(temp_file, 'wb') as wf:
            wf.setnchannels(self.audio_sources["Speaker"]["channels"])
            p = pyaudio.PyAudio()
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.audio_sources["Speaker"]["sample_rate"])
            wf.writeframes(data)
        return temp_file

    def get_transcription(self, file_path):
        result = self.audio_model.transcribe(file_path, fp16=torch.cuda.is_available())
        return result['text'].strip()

    def update_transcript(self, who_spoke, text, time_spoken):
        source_info = self.audio_sources[who_spoke]
        transcript = self.transcript_data[who_spoke]

        if source_info["new_phrase"] or len(transcript) == 0:
            if len(transcript) > MAX_PHRASES:
                transcript.pop(0)  # remove oldest phrase
            transcript.insert(0, (f"{who_spoke}: [{text}]\n\n", time_spoken))
        else:
            transcript[0] = (f"{who_spoke}: [{text}]\n\n", time_spoken)

    def get_transcript(self):
        combined_transcript = list(merge(
            self.transcript_data["You"], self.transcript_data["Speaker"], 
            key=lambda x: x[1], reverse=True))
        combined_transcript = combined_transcript[:MAX_PHRASES]
        return "".join([t[0] for t in combined_transcript])
    
    def clear_transcript_data(self):
        self.transcript_data["You"].clear()
        self.transcript_data["Speaker"].clear()
        