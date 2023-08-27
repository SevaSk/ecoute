"""Plays the responses received from LLM as Audio
This class does text to speech
"""

import os
import time
import tempfile
import threading
import playsound
import gtts
import app_logging as al
import conversation
import constants


root_logger = al.get_logger()


class AudioPlayer:
    """Play text to audio
    """
    def __init__(self, convo: conversation):
        root_logger.info(AudioPlayer.__name__)
        self.speech_text_available = threading.Event()
        self.conversation = convo
        self.temp_dir = tempfile.gettempdir()

    def play_audio(self, speech: str):
        """Play text to audio.
        This is a blocking method and will return when audio playback is complete.
        For large audio text, this could be several minutes.
        """
        root_logger.info(AudioPlayer.__name__)
        audio_obj = gtts.gTTS(speech)
        temp_audio_file = tempfile.mkstemp(dir=self.temp_dir, suffix='.mp3')
        os.close(temp_audio_file[0])

        audio_obj.save(temp_audio_file[1])
        try:
            playsound.playsound(temp_audio_file[1])
        except playsound.PlaysoundException as play_ex:
            print('Error when attempting to play audio.')
            print(play_ex)

        os.remove(temp_audio_file[1])

    def play_audio_loop(self):
        """Play text to audio continuously based on the signaling of event
        """
        while True:
            if self.speech_text_available.is_set():
                self.speech_text_available.clear()
                speech = self.conversation.get_conversation(
                    sources=[constants.PERSONA_ASSISTANT], length=1)
                # Speech text is in the format
                # f"{persona}: [{text}]\n\n"
                # Remove persona
                final_speech = speech[len(constants.PERSONA_ASSISTANT)+2:]
                # Remove whitespace
                final_speech = final_speech.strip()
                # Remove Square brackets
                final_speech = final_speech[1:-1]
                self.play_audio(speech=final_speech)
            time.sleep(0.1)
