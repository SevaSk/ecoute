import openai
import whisper
import os
import torch


def get_model(use_api: bool, model: str = None):
    if use_api:
        return APIWhisperTranscriber()

    model_cleaned = model if model else 'tiny'
    print(f'Using model: {model_cleaned}')
    return WhisperTranscriber(model=model_cleaned)


class WhisperTranscriber:
    def __init__(self, model: str = 'tiny'):
        model_filename = model + '.en.pt'

        if not os.path.isfile(model_filename):
            print(f'Could not find the model file: {model_filename}')
            print(f'Download the model file and add it to the directory: \
                  {os.getcwd()}')
            print('small model is available at: \
                  https://drive.google.com/file/d/1vhtoZCwfYGi5C4jK1r-QVr5GobSBnKiH/view?usp=drive_link')
            print('base model is available at: \
                  https://drive.google.com/file/d/1E44DVjpfZX8tSrSagaDJXU91caZOkwa6/view?usp=drive_link')
            exit()

        self.audio_model = whisper.load_model(os.path.join(os.getcwd(),
                                                           model_filename))
        print(f'[INFO] Whisper using GPU: {str(torch.cuda.is_available())}')

    def get_transcription(self, wav_file_path):
        try:
            result = self.audio_model.transcribe(wav_file_path, fp16=torch.cuda.is_available())
        except Exception as exception:
            print(exception)
            return ''
        return result['text'].strip()


class APIWhisperTranscriber:
    def __init__(self):
        print('Using Open AI API for transcription.')

    def get_transcription(self, wav_file_path):
        try:
            with open(wav_file_path, "rb") as audio_file:
                result = openai.Audio.transcribe("whisper-1", audio_file)
        except Exception as exception:
            print(exception)
            return ''
        return result['text'].strip()
