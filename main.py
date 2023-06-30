import threading
import argparse
from argparse import RawTextHelpFormatter
from AudioTranscriber import AudioTranscriber
from GPTResponder import GPTResponder
import customtkinter as ctk
import AudioRecorder
import queue
import time
import torch
import TranscriberModels
import subprocess
import pyperclip


def write_in_textbox(textbox, text):
    textbox.delete("0.0", "end")
    textbox.insert("0.0", text)


def update_transcript_UI(transcriber, textbox):
    transcript_string = transcriber.get_transcript()
    write_in_textbox(textbox, transcript_string)
    textbox.see("end")
    textbox.after(300, update_transcript_UI, transcriber, textbox)


def update_response_UI(responder, textbox, update_interval_slider_label, 
                       update_interval_slider, freeze_state):
    if not freeze_state[0]:
        response = responder.response

        textbox.configure(state="normal")
        write_in_textbox(textbox, response)
        textbox.configure(state="disabled")

        update_interval = int(update_interval_slider.get())
        responder.update_response_interval(update_interval)
        update_interval_slider_label.configure(text=f"Update interval: \
                                               {update_interval} seconds")

    textbox.after(300, update_response_UI, responder, textbox,
                  update_interval_slider_label, update_interval_slider,
                  freeze_state)


def clear_context(transcriber, audio_queue):
    transcriber.clear_transcript_data()
    with audio_queue.mutex:
        audio_queue.queue.clear()


def create_ui_components(root):
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    root.title("Transcribe")
    root.configure(bg='#252422')
    root.geometry("1000x600")

    font_size = 20

    transcript_textbox = ctk.CTkTextbox(root, width=300, font=("Arial", font_size),
                                        text_color='#FFFCF2', wrap="word")
    transcript_textbox.grid(row=0, column=0, padx=10, pady=20, sticky="nsew")

    response_textbox = ctk.CTkTextbox(root, width=300, font=("Arial", font_size),
                                      text_color='#639cdc', wrap="word")
    response_textbox.grid(row=0, column=1, padx=10, pady=20, sticky="nsew")

    freeze_button = ctk.CTkButton(root, text="Freeze", command=None)
    freeze_button.grid(row=1, column=1, padx=10, pady=3, sticky="nsew")

    update_interval_slider_label = ctk.CTkLabel(root, text="", font=("Arial", 12),
                                                text_color="#FFFCF2")
    update_interval_slider_label.grid(row=2, column=1, padx=10, pady=3, sticky="nsew")

    update_interval_slider = ctk.CTkSlider(root, from_=1, to=10, width=300, height=20,
                                           number_of_steps=9)
    update_interval_slider.set(2)
    update_interval_slider.grid(row=3, column=1, padx=10, pady=10, sticky="nsew")

    copy_button = ctk.CTkButton(root, text="Copy", command=None)
    copy_button.grid(row=2, column=0, padx=10, pady=3, sticky="nsew")

    save_file_button = ctk.CTkButton(root, text="Save to File", command=None)
    save_file_button.grid(row=3, column=0, padx=10, pady=3, sticky="nsew")

    # Order of returned components is important. For adding new components add new components
    # to the end
    return [transcript_textbox, response_textbox, update_interval_slider,
            update_interval_slider_label, freeze_button, copy_button,
            save_file_button]


def main():

    # Set up all arguments
    cmd_args = argparse.ArgumentParser(description='Command Line Arguments for Transcribe',
                                       formatter_class=RawTextHelpFormatter)
    cmd_args.add_argument('-a', '--api', action='store_true',
                          help='Use the online Open AI API for transcription.\
                          \nThis option requires an API KEY and will consume Open AI credits.')
    cmd_args.add_argument('-m', '--model', action='store', choices=['tiny', 'base', 'small'], default='tiny',
                          help='Specify the model to use for transcription.'
                          '\nBy default tiny model is part of the install.'
                          '\nbase model has to be downloaded from the link https://drive.google.com/file/d/1E44DVjpfZX8tSrSagaDJXU91caZOkwa6/view?usp=drive_link'
                          '\nsmall model has to be downloaded from the link https://drive.google.com/file/d/1E44DVjpfZX8tSrSagaDJXU91caZOkwa6/view?usp=drive_link'
                          '\nOpenAI has more models besides the ones specified above.'
                          '\nThose models are prohibitive to use on local machines because of memory requirements.'
                          '\nThis option is only applicable when not using the --api option.')
    args = cmd_args.parse_args()

    try:
        subprocess.run(["ffmpeg", "-version"],
                       stdout = subprocess.DEVNULL,
                       stderr = subprocess.DEVNULL)
    except FileNotFoundError:
        print("ERROR: The ffmpeg library is not installed. Please install \
              ffmpeg and try again.")
        return

    root = ctk.CTk()
    ui_components = create_ui_components(root)
    transcript_textbox = ui_components[0]
    response_textbox = ui_components[1]
    update_interval_slider = ui_components[2]
    update_interval_slider_label = ui_components[3]
    freeze_button = ui_components[4]
    copy_button = ui_components[5]
    save_file_button = ui_components[6]

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
    transcribe = threading.Thread(target=transcriber.transcribe_audio_queue,
                                  args=(audio_queue,))
    transcribe.daemon = True
    transcribe.start()

    responder = GPTResponder()
    respond = threading.Thread(target=responder.respond_to_transcriber,
                               args=(transcriber,))
    respond.daemon = True
    respond.start()

    print("READY")

    root.grid_rowconfigure(0, weight=100)
    root.grid_rowconfigure(1, weight=1)
    root.grid_rowconfigure(2, weight=1)
    root.grid_rowconfigure(3, weight=1)
    root.grid_columnconfigure(0, weight=2)
    root.grid_columnconfigure(1, weight=1)

    # Add the clear transcript button to the UI
    clear_transcript_button = ctk.CTkButton(root, text="Clear Transcript",
                                            command=lambda: clear_context(transcriber, audio_queue))
    clear_transcript_button.grid(row=1, column=0, padx=10, pady=3, sticky="nsew")

    freeze_state = [False]  # Using list to be able to change its content inside inner functions

    def freeze_unfreeze():
        freeze_state[0] = not freeze_state[0]  # Invert the freeze state
        freeze_button.configure(text="Unfreeze" if freeze_state[0] else "Freeze")

    freeze_button.configure(command=freeze_unfreeze)

    def copy_to_clipboard():
        pyperclip.copy(transcriber.get_transcript())

    copy_button.configure(command=copy_to_clipboard)

    def save_file():
        filename = ctk.filedialog.asksaveasfilename()
        with open(file=filename, mode="w", encoding='utf-8') as file_handle:
            file_handle.write(transcriber.get_transcript())

    save_file_button.configure(command=save_file)

    update_interval_slider_label.configure(text=f"Update interval: \
                                          {update_interval_slider.get()} \
                                          seconds")

    update_transcript_UI(transcriber, transcript_textbox)
    update_response_UI(responder, response_textbox, update_interval_slider_label,
                       update_interval_slider, freeze_state)

    root.mainloop()


if __name__ == "__main__":
    main()
