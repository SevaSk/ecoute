import threading
import argparse
from argparse import RawTextHelpFormatter
import queue
import time
import requests
from AudioTranscriber import AudioTranscriber
from GPTResponder import GPTResponder
import customtkinter as ctk
import AudioRecorder
import torch
import TranscriberModels
import subprocess
import pyperclip
import interactions
import ui
from requests.exceptions import ConnectionError


def main():
    # Set up all arguments
    cmd_args = argparse.ArgumentParser(description='Command Line Arguments for Transcribe',
                                       formatter_class=RawTextHelpFormatter)
    cmd_args.add_argument('-a', '--api', action='store_true',
                          help='Use the online Open AI API for transcription.\
                          \nThis option requires an API KEY and will consume Open AI credits.')
    cmd_args.add_argument('-m', '--model', action='store', choices=['tiny', 'base', 'small'],
                          default='tiny',
                          help='Specify the model to use for transcription.'
                          '\nBy default tiny model is part of the install.'
                          '\nbase model has to be downloaded from the link \
                            https://drive.google.com/file/d/1E44DVjpfZX8tSrSagaDJXU91caZOkwa6/view?usp=drive_link'
                          '\nsmall model has to be downloaded from the link \
                            https://drive.google.com/file/d/1vhtoZCwfYGi5C4jK1r-QVr5GobSBnKiH/view?usp=drive_link'
                          '\nOpenAI has more models besides the ones specified above.'
                          '\nThose models are prohibitive to use on local machines because \
                            of memory requirements.')
    cmd_args.add_argument('-e', '--experimental', action='store_true', help='Experimental command\
                          line argument. Behavior is undefined.')
    args = cmd_args.parse_args()

    try:
        subprocess.run(["ffmpeg", "-version"],
                       stdout = subprocess.DEVNULL,
                       stderr = subprocess.DEVNULL)
    except FileNotFoundError:
        print("ERROR: The ffmpeg library is not installed. Please install \
              ffmpeg and try again.")
        return

    query_params = interactions.create_params()
    try:
        response = requests.get("http://127.0.0.1:5000/ping", params=query_params)
        if response.status_code != 200:
            print(f'Error received: {response}')
    except ConnectionError:
        print('Operating as a standalone client')

    root = ctk.CTk()
    ui_components = ui.create_ui_components(root)
    transcript_textbox = ui_components[0]
    response_textbox = ui_components[1]
    update_interval_slider = ui_components[2]
    update_interval_slider_label = ui_components[3]
    freeze_button = ui_components[4]
    copy_button = ui_components[5]
    save_file_button = ui_components[6]
    transcript_button = ui_components[7]

    audio_queue = queue.Queue()

    user_audio_recorder = AudioRecorder.DefaultMicRecorder()
    user_audio_recorder.record_into_queue(audio_queue)

    time.sleep(2)

    speaker_audio_recorder = AudioRecorder.DefaultSpeakerRecorder()
    speaker_audio_recorder.record_into_queue(audio_queue)
    model = TranscriberModels.get_model(args.api, model=args.model)

    # Transcribe and Respond threads, both work on the same instance of the AudioTranscriber class
    transcriber = AudioTranscriber(user_audio_recorder.source,
                                   speaker_audio_recorder.source, model)
    transcribe_thread = threading.Thread(target=transcriber.transcribe_audio_queue,
                                         args=(audio_queue,))
    transcribe_thread.daemon = True
    transcribe_thread.start()

    responder = GPTResponder()
    respond_thread = threading.Thread(target=responder.respond_to_transcriber,
                                      args=(transcriber,))
    respond_thread.daemon = True
    respond_thread.start()

    print("READY")

    root.grid_rowconfigure(0, weight=100)
    root.grid_rowconfigure(1, weight=1)
    root.grid_rowconfigure(2, weight=1)
    root.grid_rowconfigure(3, weight=1)
    root.grid_columnconfigure(0, weight=2)
    root.grid_columnconfigure(1, weight=1)

    # Add the clear transcript button to the UI
    clear_transcript_button = ctk.CTkButton(root, text="Clear Audio Transcript",
                                            command=lambda: ui.clear_context(transcriber, audio_queue))
    clear_transcript_button.grid(row=1, column=0, padx=10, pady=3, sticky="nsew")

    freeze_state = [True]  # Using list to be able to change its content inside inner functions

    def freeze_unfreeze():
        freeze_state[0] = not freeze_state[0]  # Invert the state
        freeze_button.configure(text="Suggest Response" if freeze_state[0] else "Do Not Suggest Response")

    freeze_button.configure(command=freeze_unfreeze)

    def copy_to_clipboard():
        pyperclip.copy(transcriber.get_transcript())

    copy_button.configure(command=copy_to_clipboard)

    def save_file():
        filename = ctk.filedialog.asksaveasfilename()
        with open(file=filename, mode="w", encoding='utf-8') as file_handle:
            file_handle.write(transcriber.get_transcript())

    save_file_button.configure(command=save_file)

    def set_transcript_state():
        transcriber.transcribe = not transcriber.transcribe
        transcript_button.configure(text="Pause Transcript" if transcriber.transcribe else "Start Transcript")

    transcript_button.configure(command=set_transcript_state)

    update_interval_slider_label.configure(text=f"Update interval: \
                                          {update_interval_slider.get()} \
                                          seconds")

    ui.update_transcript_ui(transcriber, transcript_textbox)
    ui.update_response_ui(responder, response_textbox, update_interval_slider_label,
                          update_interval_slider, freeze_state)

    root.mainloop()


if __name__ == "__main__":
    main()
