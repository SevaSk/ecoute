import torch
from faster_whisper import WhisperModel
from openai import OpenAI

def get_model(use_api):
    if use_api:
        return APIWhisperTranscriber()
    else:
        return FasterWhisperTranscriber()

class FasterWhisperTranscriber:
    def __init__(self):
        print(f"[INFO] Loading Faster Whisper model...")
        self.model = WhisperModel("tiny.en", device="cuda" if torch.cuda.is_available() else "cpu", 
                                 compute_type="float32" if torch.cuda.is_available() else "int8")
        print(f"[INFO] Faster Whisper using GPU: {torch.cuda.is_available()}")

    def get_transcription(self, wav_file_path):
        try:
            segments, _ = self.model.transcribe(wav_file_path, beam_size=5)
            full_text = " ".join(segment.text for segment in segments)
            return full_text.strip()
        except Exception as e:
            print(e)
            return ''

class APIWhisperTranscriber:
    def __init__(self, api_key=None):
        self.client = OpenAI(api_key=api_key)
    
    def get_transcription(self, wav_file_path):
        try:
            with open(wav_file_path, "rb") as audio_file:
                result = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            return result.text.strip()
        except Exception as e:
            print(e)
            return ''