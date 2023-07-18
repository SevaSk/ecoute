import os
import threading
import io
from datetime import timedelta
import wave
import tempfile
import whisper
import custom_speech_recognition as sr
import pyaudiowpatch as pyaudio
from heapq import merge

PHRASE_TIMEOUT = 3.05


class AudioTranscriber:
    def __init__(self, mic_source, speaker_source, model):
        self.transcript_data = {"You": [], "Speaker": []}
        self.transcript_changed_event = threading.Event()
        self.audio_model = model
        self.transcribe = True  # By default we start with transcription enabled
        self.audio_sources = {
            "You": {
                "sample_rate": mic_source.SAMPLE_RATE,
                "sample_width": mic_source.SAMPLE_WIDTH,
                "channels": mic_source.channels,
                "last_sample": bytes(),
                "last_spoken": None,
                "new_phrase": True,
                "process_data_func": self.process_mic_data
            },
            "Speaker": {
                "sample_rate": speaker_source.SAMPLE_RATE,
                "sample_width": speaker_source.SAMPLE_WIDTH,
                "channels": speaker_source.channels,
                "last_sample": bytes(),
                "last_spoken": None,
                "new_phrase": True,
                "process_data_func": self.process_speaker_data
            }
        }

    def transcribe_audio_queue(self, audio_queue):
        """Transcribe data from audio sources. In this case we have 2 sources, microphone, speaker.
        Args:
          audio_queue: queue object with reference to audio files

        """
        while True:
            who_spoke, data, time_spoken = audio_queue.get()
            self.update_last_sample_and_phrase_status(who_spoke, data, time_spoken)
            source_info = self.audio_sources[who_spoke]

            text = ''
            try:
                fd, path = tempfile.mkstemp(suffix=".wav")
                os.close(fd)
                source_info["process_data_func"](source_info["last_sample"], path)
                if self.transcribe:
                    text = self.audio_model.get_transcription(path)
            except Exception as exception:
                print(exception)
            finally:
                os.unlink(path)

            if text != '' and text.lower() != 'you':
                self.update_transcript(who_spoke, text, time_spoken)
                self.transcript_changed_event.set()

    def update_last_sample_and_phrase_status(self, who_spoke, data, time_spoken):
        if not self.transcribe:
            return
        source_info = self.audio_sources[who_spoke]
        if source_info["last_spoken"] and time_spoken - source_info["last_spoken"] > timedelta(seconds=PHRASE_TIMEOUT):
            source_info["last_sample"] = bytes()
            source_info["new_phrase"] = True
        else:
            source_info["new_phrase"] = False

        source_info["last_sample"] += data
        source_info["last_spoken"] = time_spoken

    def process_mic_data(self, data, temp_file_name):
        if not self.transcribe:
            return
        audio_data = sr.AudioData(data, self.audio_sources["You"]["sample_rate"], self.audio_sources["You"]["sample_width"])
        wav_data = io.BytesIO(audio_data.get_wav_data())
        with open(temp_file_name, 'w+b') as f:
            f.write(wav_data.read())

    def process_speaker_data(self, data, temp_file_name):
        if not self.transcribe:
            return
        with wave.open(temp_file_name, 'wb') as wf:
            wf.setnchannels(self.audio_sources["Speaker"]["channels"])
            p = pyaudio.PyAudio()
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.audio_sources["Speaker"]["sample_rate"])
            wf.writeframes(data)

    def update_transcript(self, who_spoke, text, time_spoken):
        """Update transcript with new data
        Args:
        who_spoke: Person this audio is attributed to
        text: Actual spken words
        time_spoken: Time at which audio was taken, relative to start time
        """
        source_info = self.audio_sources[who_spoke]
        transcript = self.transcript_data[who_spoke]

        if source_info["new_phrase"] or len(transcript) == 0:
            transcript.append((f"{who_spoke}: [{text}]\n\n", time_spoken))
        else:
            transcript.pop()
            transcript.append((f"{who_spoke}: [{text}]\n\n", time_spoken))

    def get_transcript(self, length: int = 0):
        """Get the audio transcript
        Args:
        length: Get the last length elements from the audio transcript.
                Default value = 0, gives the complete transcript
        """
        combined_transcript = list(merge(
            self.transcript_data["You"], self.transcript_data["Speaker"],
            key=lambda x: x[1], reverse=False))
        combined_transcript = combined_transcript[-length:]
        return "".join([t[0] for t in combined_transcript])

    def clear_transcript_data(self):
        """
        Args:
        length: Clear all data stored internally for audio transcript
        """
        self.transcript_data["You"].clear()
        self.transcript_data["Speaker"].clear()

        self.audio_sources["You"]["last_sample"] = bytes()
        self.audio_sources["Speaker"]["last_sample"] = bytes()

        self.audio_sources["You"]["new_phrase"] = True
        self.audio_sources["Speaker"]["new_phrase"] = True
