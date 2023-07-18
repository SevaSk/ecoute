import queue
from AudioTranscriber import AudioTranscriber
from GPTResponder import GPTResponder
import AudioRecorder
import customtkinter as ctk


class TranscriptionGlobals(object):
    # Global constants for audio processing. It is implemented as a singleton

    audio_queue: queue.Queue = None
    user_audio_recorder: AudioRecorder.DefaultMicRecorder = None
    speaker_audio_recorder: AudioRecorder.DefaultSpeakerRecorder = None
    # Global for transcription from speaker, microphone
    transcriber: AudioTranscriber = None
    # Global for responses from openAI API
    responder: GPTResponder = None
    # Global for determining whether to seek responses from openAI API
    freeze_state: list = None
    freeze_button: ctk.CTkButton = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(TranscriptionGlobals, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        if self.audio_queue is None:
            self.audio_queue = queue.Queue()
        if self.user_audio_recorder is None:
            self.user_audio_recorder = AudioRecorder.DefaultMicRecorder()
        if self.speaker_audio_recorder is None:
            self.speaker_audio_recorder = AudioRecorder.DefaultSpeakerRecorder()
