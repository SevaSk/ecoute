from openai import OpenAI
import whisper
import os
import torch

# Initialize OpenAI client with API key from environment variable or keys.py
try:
    from keys import OPENAI_API_KEY
    client = OpenAI(api_key=OPENAI_API_KEY)
except ImportError:
    # Fallback to environment variable
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_model(use_api):
    if use_api:
        return APIWhisperTranscriber()
    else:
        return WhisperTranscriber()

class WhisperTranscriber:
    def __init__(self):
        # Set device to CUDA if available, otherwise use CPU
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.audio_model = whisper.load_model(os.path.join(os.getcwd(), 'tiny.en.pt')).to(self.device)
        print(f"[INFO] Whisper using GPU: {torch.cuda.is_available()} on device: {self.device}")

    def get_transcription(self, wav_file_path):
        try:
            # Use fp16 precision when using CUDA for better performance
            # Remove the device parameter as the model is already on the correct device
            result = self.audio_model.transcribe(wav_file_path, fp16=torch.cuda.is_available())
        except Exception as e:
            print(e)
            return ''
        return result['text'].strip()
    
class APIWhisperTranscriber:
    def get_transcription(self, wav_file_path):
        try:
            with open(wav_file_path, "rb") as audio_file:
                result = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"  # Explicitly request text format
                )
        except Exception as e:
            print(e)
            return ''
        return result.text.strip()