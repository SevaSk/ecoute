import queue
from AudioTranscriber import AudioTranscriber
import AudioRecorder
import customtkinter as ctk
import Singleton
import app_logging as al


root_logger = al.get_logger()

class TranscriptionGlobals(Singleton.Singleton):
    """Global constants for audio processing. It is implemented as a Singleton class.
    """

    audio_queue: queue.Queue = None
    user_audio_recorder: AudioRecorder.DefaultMicRecorder = None
    speaker_audio_recorder: AudioRecorder.DefaultSpeakerRecorder = None
    # Global for transcription from speaker, microphone
    transcriber: AudioTranscriber = None
    # Global for responses from openAI API
    responder = None
    # Global for determining whether to seek responses from openAI API
    freeze_state: list = None
    freeze_button: ctk.CTkButton = None
    api_key: str = None

    def __init__(self, key: str = 'API_KEY'):
        root_logger.info(TranscriptionGlobals.__name__)
        if self.audio_queue is None:
            self.audio_queue = queue.Queue()
        if self.user_audio_recorder is None:
            self.user_audio_recorder = AudioRecorder.DefaultMicRecorder()
        if self.speaker_audio_recorder is None:
            self.speaker_audio_recorder = AudioRecorder.DefaultSpeakerRecorder()
        if self.api_key is None:
            self.api_key = key
