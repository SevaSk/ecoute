from typing import Dict, List, Tuple, Callable, Any
import whisper  # type: ignore
import torch
import wave
import os
import threading
import tempfile
import io
from datetime import timedelta, datetime
import pyaudiowpatch as pyaudio  # type: ignore
from heapq import merge

PHRASE_TIMEOUT = 3.05
MAX_PHRASES = 10

class AudioTranscriber:
    def __init__(self, mic_recorder: Any, speaker_recorder: Any, model: Any, mic_sample_rate: int, speaker_sample_rate: int, speaker_channels: int):
        self.transcript_data: Dict[str, List[Tuple[str, datetime]]] = {"You": [], "Speaker": []}
        self.transcript_changed_event = threading.Event()
        self.audio_model = model
        self.audio_sources: Dict[str, Dict[str, Any]] = {
            "You": {
                "sample_rate": mic_sample_rate,
                "sample_width": pyaudio.get_sample_size(pyaudio.paInt16),
                "channels": 1,
                "last_sample": bytes(),
                "last_spoken": None,
                "new_phrase": True,
                "process_data_func": self.process_mic_data
            },
            "Speaker": {
                "sample_rate": speaker_sample_rate,
                "sample_width": pyaudio.get_sample_size(pyaudio.paInt16),
                "channels": speaker_channels,
                "last_sample": bytes(),
                "last_spoken": None,
                "new_phrase": True,
                "process_data_func": self.process_speaker_data
            }
        }

    def transcribe_audio_queue(self, audio_queue: Any) -> None:
        while True:
            who_spoke, data, time_spoken = audio_queue.get()
            self.update_last_sample_and_phrase_status(who_spoke, data, time_spoken)
            source_info = self.audio_sources[who_spoke]

            text = ''
            try:
                fd, path = tempfile.mkstemp(suffix=".wav")
                os.close(fd)
                source_info["process_data_func"](source_info["last_sample"], path)
                text = self.audio_model.transcribe(path)['text']
            except Exception as e:
                print(f"Transcription error: {e}")
            finally:
                os.unlink(path)

            if text != '' and text.lower() != 'you':
                self.update_transcript(who_spoke, text, time_spoken)
                self.transcript_changed_event.set()

    def update_last_sample_and_phrase_status(self, who_spoke: str, data: bytes, time_spoken: datetime) -> None:
        source_info = self.audio_sources[who_spoke]
        if source_info["last_spoken"] and time_spoken - source_info["last_spoken"] > timedelta(seconds=PHRASE_TIMEOUT):
            source_info["last_sample"] = bytes()
            source_info["new_phrase"] = True
        else:
            source_info["new_phrase"] = False

        source_info["last_sample"] += data
        source_info["last_spoken"] = time_spoken 

    def process_mic_data(self, data: bytes, temp_file_name: str) -> None:
        with wave.open(temp_file_name, 'wb') as wf:
            wf.setnchannels(self.audio_sources["You"]["channels"])
            wf.setsampwidth(self.audio_sources["You"]["sample_width"])
            wf.setframerate(self.audio_sources["You"]["sample_rate"])
            wf.writeframes(data)

    def process_speaker_data(self, data: bytes, temp_file_name: str) -> None:
        with wave.open(temp_file_name, 'wb') as wf:
            wf.setnchannels(self.audio_sources["Speaker"]["channels"])
            wf.setsampwidth(self.audio_sources["Speaker"]["sample_width"])
            wf.setframerate(self.audio_sources["Speaker"]["sample_rate"])
            wf.writeframes(data)

    def update_transcript(self, who_spoke: str, text: str, time_spoken: datetime) -> None:
        source_info = self.audio_sources[who_spoke]
        transcript = self.transcript_data[who_spoke]

        if source_info["new_phrase"] or len(transcript) == 0:
            if len(transcript) > MAX_PHRASES:
                transcript.pop(-1)
            transcript.insert(0, (f"{who_spoke}: [{text}]\n\n", time_spoken))
        else:
            transcript[0] = (f"{who_spoke}: [{text}]\n\n", time_spoken)

    def get_transcript(self) -> str:
        combined_transcript = list(merge(
            self.transcript_data["You"], self.transcript_data["Speaker"], 
            key=lambda x: x[1], reverse=True))
        combined_transcript = combined_transcript[:MAX_PHRASES]
        return "".join([t[0] for t in combined_transcript])
    
    def clear_transcript_data(self) -> None:
        self.transcript_data["You"].clear()
        self.transcript_data["Speaker"].clear()

        self.audio_sources["You"]["last_sample"] = bytes()
        self.audio_sources["Speaker"]["last_sample"] = bytes()

        self.audio_sources["You"]["new_phrase"] = True
        self.audio_sources["Speaker"]["new_phrase"] = True