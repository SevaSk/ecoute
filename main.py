import threading
from AudioTranscriber import AudioTranscriber
from GPTResponder import GPTResponder
import customtkinter as ctk  # type: ignore
import AudioRecorder 
import queue
import time
import torch  # type: ignore
import sys
import TranscriberModels
import subprocess
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def write_in_textbox(textbox, text):
    textbox.delete("0.0", "end")
    textbox.insert("0.0", text)

def update_transcript_UI(transcriber, textbox):
    transcript_string = transcriber.get_transcript()
    write_in_textbox(textbox, transcript_string)
    textbox.after(300, update_transcript_UI, transcriber, textbox)

def update_response_UI(responder, textbox, update_interval_slider_label, update_interval_slider, freeze_state):
    if not freeze_state[0]:
        response = responder.response

        textbox.configure(state="normal")
        write_in_textbox(textbox, response)
        textbox.configure(state="disabled")

        update_interval = int(update_interval_slider.get())
        responder.update_response_interval(update_interval)
        update_interval_slider_label.configure(text=f"Update interval: {update_interval} seconds")

    textbox.after(300, update_response_UI, responder, textbox, update_interval_slider_label, update_interval_slider, freeze_state)

def clear_context(transcriber, audio_queue):
    transcriber.clear_transcript_data()
    with audio_queue.mutex:
        audio_queue.queue.clear()
    logging.info("Transcript and audio queue cleared")

def create_ui_components(root):
    root.title("Ecoute")
    root.geometry("800x600")

    # Create transcript textbox
    transcript_textbox = ctk.CTkTextbox(root, height=200, width=780)
    transcript_textbox.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

    # Create response textbox
    response_textbox = ctk.CTkTextbox(root, height=200, width=780)
    response_textbox.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    # Create update interval slider
    update_interval_slider = ctk.CTkSlider(root, from_=1, to=60, number_of_steps=59)
    update_interval_slider.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
    update_interval_slider.set(30)  # Default to 30 seconds

    # Create update interval slider label
    update_interval_slider_label = ctk.CTkLabel(root, text="Update interval: 30 seconds")
    update_interval_slider_label.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

    # Create freeze button
    freeze_button = ctk.CTkButton(root, text="Freeze")
    freeze_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

    return transcript_textbox, response_textbox, update_interval_slider, update_interval_slider_label, freeze_button

def main():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        logging.error("The ffmpeg library is not installed. Please install ffmpeg and try again.")
        return

    # Check if the API key is set in the environment
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        logging.error("OPENAI_API_KEY is not set in the environment. Please set it and try again.")
        return

    root = ctk.CTk()
    transcript_textbox, response_textbox, update_interval_slider, update_interval_slider_label, freeze_button = create_ui_components(root)

    audio_queue = queue.Queue()

    # Set up microphone recording
    user_audio_recorder = AudioRecorder.DefaultMicRecorder()
    user_audio_recorder.record_into_queue(audio_queue)
    logging.info("Microphone recording started")

    time.sleep(2)

    # Set up speaker recording (for interviewer's voice)
    speaker_audio_recorder = AudioRecorder.DefaultSpeakerRecorder()
    speaker_audio_recorder.record_into_queue(audio_queue)
    logging.info("Speaker recording started")

    # Initialize the transcription model
    model = TranscriberModels.get_model('--api' in sys.argv)
    logging.info(f"Transcription model initialized: {'API' if '--api' in sys.argv else 'Local'}")

    # Set up audio transcription
    transcriber = AudioTranscriber(user_audio_recorder.source, speaker_audio_recorder.source, model, 
                                   user_audio_recorder.SAMPLE_RATE, speaker_audio_recorder.sample_rate,
                                   speaker_audio_recorder.channels)
    transcribe = threading.Thread(target=transcriber.transcribe_audio_queue, args=(audio_queue,))
    transcribe.daemon = True
    transcribe.start()
    logging.info("Audio transcription thread started")

    # Set up GPT responder
    responder = GPTResponder(api_key=api_key)
    respond = threading.Thread(target=responder.respond_to_transcriber, args=(transcriber,))
    respond.daemon = True
    respond.start()
    logging.info("GPT responder thread started")

    print("READY")
    logging.info("Application ready")

    # Add the clear transcript button to the UI
    clear_transcript_button = ctk.CTkButton(root, text="Clear Transcript", command=lambda: clear_context(transcriber, audio_queue))
    clear_transcript_button.grid(row=1, column=0, padx=10, pady=3, sticky="nsew")

    freeze_state = [False]
    def freeze_unfreeze():
        freeze_state[0] = not freeze_state[0]
        freeze_button.configure(text="Unfreeze" if freeze_state[0] else "Freeze")
        logging.info(f"Response {'frozen' if freeze_state[0] else 'unfrozen'}")

    freeze_button.configure(command=freeze_unfreeze)

    update_interval_slider_label.configure(text=f"Update interval: {update_interval_slider.get()} seconds")

    # Start UI update loops
    update_transcript_UI(transcriber, transcript_textbox)
    update_response_UI(responder, response_textbox, update_interval_slider_label, update_interval_slider, freeze_state)
 
    root.mainloop()

if __name__ == "__main__":
    main()