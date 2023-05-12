import whisper
import torch
import wave
import os
import threading
from tempfile import NamedTemporaryFile
import speech_recognition as sr
import io
from datetime import timedelta
from time import sleep
import pyaudiowpatch as pyaudio
from AudioRecorder import DefaultMicRecorder, DefaultSpeakerRecorder
from heapq import merge

PHRASE_TIMEOUT = 4

class AudioTranscriber:
    def __init__(self, default_mic : DefaultMicRecorder, default_speaker : DefaultSpeakerRecorder):
        self.mic_transcript_data = []
        self.speaker_transcript_data = []
        self.transcript_changed_event = threading.Event()
        self.audio_model = whisper.load_model(os.getcwd() + r'\tiny.en' + '.pt')

        self.mic_sample_rate = default_mic.source.SAMPLE_RATE
        self.mic_sample_width = default_mic.source.SAMPLE_WIDTH
        self.mic_channels = default_mic.num_channels

        self.speaker_sample_rate = default_speaker.source.SAMPLE_RATE
        self.speaker_sample_rate = default_speaker.source.SAMPLE_RATE
        self.speaker_channels = default_speaker.num_channels

    def create_transcription_from_queue(self, audio_queue):
        mic_last_sample = bytes()
        speaker_last_sample = bytes()

        mic_last_spoken = None
        speaker_last_spoken = None

        mic_start_new_phrase = True
        speaker_start_new_phrase = True

        while True:
            top_of_queue = audio_queue.get()
            who_spoke = top_of_queue[0]
            data = top_of_queue[1]
            time_spoken = top_of_queue[2]

            if who_spoke == "You":
                if mic_last_spoken and time_spoken - mic_last_spoken > timedelta(seconds=PHRASE_TIMEOUT):
                    mic_last_sample = bytes()
                    mic_start_new_phrase = True
                else:
                    mic_start_new_phrase = False

                mic_last_sample += data
                mic_last_spoken = time_spoken 

                mic_temp_file = NamedTemporaryFile().name
                audio_data = sr.AudioData(mic_last_sample, self.mic_sample_rate, self.mic_sample_width)
                wav_data = io.BytesIO(audio_data.get_wav_data())
                with open(mic_temp_file, 'w+b') as f:
                    f.write(wav_data.read())

                result = self.audio_model.transcribe(mic_temp_file, fp16=torch.cuda.is_available())
                text = result['text'].strip()

                if text != '' and text.lower() != 'you':
                    if mic_start_new_phrase or len(self.mic_transcript_data) == 0:
                        self.mic_transcript_data = [(who_spoke + ": [" + text + ']\n\n', time_spoken)] + self.mic_transcript_data
                        self.transcript_changed_event.set()
                    else:
                        self.mic_transcript_data[0] = (who_spoke + ": [" + text + ']\n\n',
                        time_spoken)
                        self.transcript_changed_event.set()
            else:
                if speaker_last_spoken and time_spoken - speaker_last_spoken > timedelta(seconds=PHRASE_TIMEOUT):
                    speaker_last_sample = bytes()
                    speaker_start_new_phrase = True
                else:
                    speaker_start_new_phrase = False

                speaker_last_sample += data
                speaker_last_spoken = time_spoken 

                speaker_temp_file = NamedTemporaryFile().name

                with wave.open(speaker_temp_file, 'wb') as wf:
                    wf.setnchannels(self.speaker_channels)
                    p = pyaudio.PyAudio()
                    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
                    wf.setframerate(self.speaker_sample_rate)
                    wf.writeframes(speaker_last_sample)

                result = self.audio_model.transcribe(speaker_temp_file, fp16=torch.cuda.is_available())
                text = result['text'].strip()

                if text != '' and text.lower() != 'you':
                    if speaker_start_new_phrase or len(self.speaker_transcript_data) == 0:
                        self.speaker_transcript_data = [(who_spoke + ": [" + text + ']\n\n', time_spoken)] + self.speaker_transcript_data
                        self.transcript_changed_event.set()

                    else:
                        self.speaker_transcript_data[0] = (who_spoke + ": [" + text + ']\n\n',
                         time_spoken)
                        self.transcript_changed_event.set()

    def get_transcript(self):
        key = lambda x : x[1]
        transcript_tuple = list(merge(self.mic_transcript_data, self.speaker_transcript_data, key=key, reverse=True))
        return "".join([t[0] for t in transcript_tuple])
    