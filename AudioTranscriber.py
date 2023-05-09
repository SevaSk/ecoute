import numpy as np
import whisper
import torch
import wave
import os
import threading

class AudioTranscriber:
    def __init__(self):
        self.transcript_data = []
        self.transcript_changed_event = threading.Event()
        self.audio_model = whisper.load_model(os.getcwd() + r'\tiny.en' + '.pt')

    def transcribe(self, audio_data):
        with wave.open(f'temp_{id(self)}.wav', 'wb') as wav_file:
            wav_file.setnchannels(audio_data.shape[1])
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)
            audio_data = (audio_data * (2**15 - 1)).astype(np.int16)
            wav_file.writeframes(audio_data.tobytes())
        result = self.audio_model.transcribe(f'temp_{id(self)}.wav', fp16=torch.cuda.is_available())
        text = result['text'].strip()
        return text
    
    def create_transcription_from_queue(self, audio_queue):
        while True:
            top_of_queue = audio_queue.get()
            source = top_of_queue[0]
            audio_data = top_of_queue[1]
            audio_data_transcription = self.transcribe(audio_data)
            # whisper gives "you" on many null inputs
            if audio_data_transcription != '' and audio_data_transcription.lower() != 'you':
                self.transcript_data = [source + ": [" + audio_data_transcription + ']\n\n'] + self.transcript_data
                self.transcript_changed_event.set()

    def get_transcript(self):
        return "".join(self.transcript_data)