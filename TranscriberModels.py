import openai
import whisper
import os
import torch

def get_model(use_api):
    if use_api:
        return APIWhisperTranscriber()
    else:
        return WhisperTranscriber()

class WhisperTranscriber:
    def __init__(self):
        self.audio_model = whisper.load_model(os.path.join(os.getcwd(), 'tiny.en.pt'))
        print(f"[INFO] Whisper using GPU: " + str(torch.cuda.is_available()))

    def get_transcription(self, wav_file_path):
        try:
            result = self.audio_model.transcribe(wav_file_path, fp16=torch.cuda.is_available())
        except Exception as e:
            print(e)
            return ''
        return result['text'].strip()
    
class APIWhisperTranscriber:
    def get_transcription(self, wav_file_path):
        audio_file= open(wav_file_path, "rb")
        try:
            result = openai.Audio.translate("whisper-1", audio_file)
        except Exception as e:
            print(e)
            return ''

        return result['text'].strip()