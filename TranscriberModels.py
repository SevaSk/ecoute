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
        self.lang = 'en'
        self.model = model

        if not os.path.isfile(model_filename):
            print(f'Could not find the model file: {model_filename}')
            print(f'Download the model file and add it to the directory: \
                  {os.getcwd()}')
            print('tiny multi-lingual model is available at: \
                  https://drive.google.com/file/d/1M4AFutTmQROaE9xk2jPc5Y4oFRibHhEh/view?usp=drive_link')
            print('small english model is available at: \
                  https://drive.google.com/file/d/1vhtoZCwfYGi5C4jK1r-QVr5GobSBnKiH/view?usp=drive_link')
            print('small multi-lingual model is available at: \
                  https://drive.google.com/file/d/1bl8er_st8WPZKPWVeYMNlaUi9IzR3jEZ/view?usp=drive_link')
            print('base english model is available at: \
                  https://drive.google.com/file/d/1E44DVjpfZX8tSrSagaDJXU91caZOkwa6/view?usp=drive_link')
            print('base multi-lingual model is available at: \
                  https://drive.google.com/file/d/1UcqU_D0cPFqq_nckSfstMBfogFsvR-KR/view?usp=drive_link')
            exit()
        self.model_filename = os.path.join(os.getcwd(), model_filename)
        self.audio_model = whisper.load_model(self.model_filename)
        print(f'[INFO] Whisper using GPU: {str(torch.cuda.is_available())}')

    def get_transcription(self, wav_file_path):
        try:
            result = self.audio_model.transcribe(wav_file_path,
                                                 fp16=torch.cuda.is_available(), language=self.lang)
        except Exception as exception:
            print(exception)
            return ''
        return result['text'].strip()

    def change_lang(self, lang: str):
        self.lang = lang
        self.load_model()

    def load_model(self):
        if self.lang == "en":
            self.audio_model = whisper.load_model(os.path.join(os.getcwd(), self.model + 'en.pt'))
        else:
            self.audio_model = whisper.load_model(os.path.join(os.getcwd(), self.model + '.pt'))


class APIWhisperTranscriber:
    def __init__(self):
        print('Using Open AI API for transcription.')
        # lang parameter is not required for API invocation. This exists solely
        # to support --api option from command line.
        # A better solution is to create a base class for APIWhisperTranscriber,
        # WhisperTranscriber and create change_lang method there and remove it from
        # this class
        self.lang = 'en'

    def change_lang(self, lang: str):
        self.lang = lang

    def get_transcription(self, wav_file_path):
        try:
            with open(wav_file_path, "rb") as audio_file:
                result = openai.Audio.transcribe("whisper-1", audio_file)
        except Exception as exception:
            print(exception)
            return ''
        return result['text'].strip()
