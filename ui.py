import queue
import datetime
import pyperclip
import tkinter as tk
import AudioTranscriber
import prompts
from language import LANGUAGES_DICT
import customtkinter as ctk
import GlobalVars
import GPTResponder
import app_logging as al
import constants

root_logger = al.get_logger()
UI_FONT_SIZE = 20
last_transcript_ui_update_time: datetime.datetime = datetime.datetime.now()


class ui_callbacks:

    global_vars: GlobalVars.TranscriptionGlobals

    def __init__(self):
        self.global_vars = GlobalVars.TranscriptionGlobals()

    def copy_to_clipboard(self):
        """Copy transcription text data to clipboard.
           Does not include responses from assistant.
        """
        root_logger.info(ui_callbacks.copy_to_clipboard.__name__)
        pyperclip.copy(self.global_vars.transcriber.get_transcript())

    def save_file(self):
        """Save transcription text data to file.
           Does not include responses from assistant.
        """
        root_logger.info(ui_callbacks.save_file.__name__)
        filename = ctk.filedialog.asksaveasfilename()
        with open(file=filename, mode="w", encoding='utf-8') as file_handle:
            file_handle.write(self.global_vars.transcriber.get_transcript())

    def freeze_unfreeze(self):
        """Respond to start / stop of seeking responses from openAI API"""
        root_logger.info(ui_callbacks.freeze_unfreeze.__name__)
        self.global_vars.freeze_state[0] = not self.global_vars.freeze_state[0]  # Invert the state
        self.global_vars.freeze_button.configure(
            text="Suggest Responses Continuously" if self.global_vars.freeze_state[0] else "Do Not Suggest Responses Continuously"
            )

    # to enable/disable speaker/microphone when args are given or button is pressed
    def enable_disable_speaker(self, editmenu):
        self.global_vars.speaker_audio_recorder.enabled = not self.global_vars.speaker_audio_recorder.enabled
        editmenu.entryconfigure(2, label="Disable Speaker" if self.global_vars.speaker_audio_recorder.enabled else "Enable Speaker")

    def enable_disable_microphone(self, editmenu):
        self.global_vars.user_audio_recorder.enabled = not self.global_vars.user_audio_recorder.enabled
        editmenu.entryconfigure(3, label="Disable Microphone" if self.global_vars.user_audio_recorder.enabled else "Enable Microphone")

    def update_response_ui_now(self):
        """Get response from LLM right away
           Update the Response UI with the response
        """
        transcript_string = self.global_vars.transcriber.get_transcript(
            length=constants.MAX_TRANSCRIPTION_PHRASES_FOR_LLM)

        response_string = self.global_vars.responder.generate_response_from_transcript_no_check(
            transcript_string)
        self.global_vars.response_textbox.configure(state="normal")
        write_in_textbox(self.global_vars.response_textbox, response_string)
        self.global_vars.response_textbox.configure(state="disabled")

    def update_response_ui_and_read_now(self):
        """Get response from LLM right away
        Update the Response UI with the response
        Read the response
        """
        self.update_response_ui_now()

        # Set event to play the recording audio
        self.global_vars.audio_player.speech_text_available.set()

    def set_transcript_state(self):
        """Enables, disables transcription.
           Text of menu item File -> Pause Transcription toggles accordingly"""
        root_logger.info(ui_callbacks.set_transcript_state.__name__)
        self.global_vars.transcriber.transcribe = not self.global_vars.transcriber.transcribe
        if self.global_vars.transcriber.transcribe:
            self.global_vars.filemenu.entryconfigure(1, label="Pause Transcription")
        else:
            self.global_vars.filemenu.entryconfigure(1, label="Start Transcription")


def write_in_textbox(textbox: ctk.CTkTextbox, text: str):
    """Update the text of textbox with the given text
        Args:
          textbox: textbox to be updated
          text: updated text
    """
    textbox.delete("0.0", "end")
    textbox.insert("0.0", text)


def update_transcript_ui(transcriber: AudioTranscriber, textbox: ctk.CTkTextbox):
    """Update the text of transcription textbox with the given text
        Args:
          transcriber: AudioTranscriber Object
          textbox: textbox to be updated
    """

    global last_transcript_ui_update_time

    if last_transcript_ui_update_time < GlobalVars.TranscriptionGlobals().convo.last_update:
        transcript_string = transcriber.get_transcript()
        write_in_textbox(textbox, transcript_string)
        textbox.see("end")
        last_transcript_ui_update_time = datetime.datetime.now()

    textbox.after(constants.TRANSCRIPT_UI_UPDATE_DELAY_DURATION_MS,
                  update_transcript_ui, transcriber, textbox)


def update_response_ui(responder: GPTResponder,
                       textbox: ctk.CTkTextbox,
                       update_interval_slider_label: ctk.CTkLabel,
                       update_interval_slider: ctk.CTkSlider,
                       freeze_state):
    """Update the text of response textbox with the given text
        Args:
          textbox: textbox to be updated
          text: updated text
    """
    if not freeze_state[0]:
        response = responder.response

        textbox.configure(state="normal")
        write_in_textbox(textbox, response)
        textbox.configure(state="disabled")

        update_interval = int(update_interval_slider.get())
        responder.update_response_interval(update_interval)
        update_interval_slider_label.configure(text=f'Update Response interval: {update_interval} seconds')

    textbox.after(300, update_response_ui, responder, textbox,
                  update_interval_slider_label, update_interval_slider,
                  freeze_state)


def clear_transcriber_context(transcriber: AudioTranscriber,
                              audio_queue: queue.Queue):
    """Reset the transcriber
        Args:
          textbox: textbox to be updated
          text: updated text
    """
    root_logger.info(clear_transcriber_context.__name__)
    transcriber.clear_transcript_data()
    with audio_queue.mutex:
        audio_queue.queue.clear()


def create_ui_components(root):
    root_logger.info(create_ui_components.__name__)
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    root.title("Transcribe")
    root.configure(bg='#252422')
    root.geometry("1000x600")

    ui_cb = ui_callbacks()
    global_vars = GlobalVars.TranscriptionGlobals()

    # Create the menu bar
    menubar = tk.Menu(root)

    # Create a file menu
    filemenu = tk.Menu(menubar, tearoff=False)

    # Add a "Save" menu item to the file menu
    filemenu.add_command(label="Save Transcript to File", command=ui_cb.save_file)

    # Add a "Pause" menu item to the file menu
    filemenu.add_command(label="Pause Transcription", command=ui_cb.set_transcript_state)

    # Add a "Quit" menu item to the file menu
    filemenu.add_command(label="Quit", command=root.quit)

    # Add the file menu to the menu bar
    menubar.add_cascade(label="File", menu=filemenu)

    # Create an edit menu
    editmenu = tk.Menu(menubar, tearoff=False)

    # Add a "Clear Audio Transcript" menu item to the file menu
    editmenu.add_command(label="Clear Audio Transcript", command=lambda: clear_transcriber_context(
        global_vars.transcriber, global_vars.audio_queue))

    # Add a "Copy To Clipboard" menu item to the file menu
    editmenu.add_command(label="Copy Transcript to Clipboard", command=ui_cb.copy_to_clipboard)

    # Add "Disable Speaker" menu item to file menu
    editmenu.add_command(label="Disable Speaker", command=lambda: ui_cb.enable_disable_speaker(editmenu))

    # Add "Disable Microphone" menu item to file menu
    editmenu.add_command(label="Disable Microphone", command=lambda: ui_cb.enable_disable_microphone(editmenu))

    # See example of add_radiobutton() at https://www.plus2net.com/python/tkinter-menu.php
    # Radiobutton would be a good way to display different languages
    # lang_menu = tk.Menu(menubar, tearoff=False)
    # for lang in LANGUAGES_DICT.values():
    #    model.change_lang
    #    lang_menu.add_command(label=lang, command=model.change_lang)
    # editmenu.add_cascade(menu=lang_menu, label='Languages')

    # Add the edit menu to the menu bar
    menubar.add_cascade(label="Edit", menu=editmenu)

    # Add the menu bar to the main window
    root.config(menu=menubar)

    transcript_textbox = ctk.CTkTextbox(root, width=300, font=("Arial", UI_FONT_SIZE),
                                        text_color='#FFFCF2', wrap="word")
    transcript_textbox.grid(row=0, column=0, padx=10, pady=20, sticky="nsew")

    response_textbox = ctk.CTkTextbox(root, width=300, font=("Arial", UI_FONT_SIZE),
                                      text_color='#639cdc', wrap="word")
    response_textbox.grid(row=0, column=1, padx=10, pady=20, sticky="nsew")
    response_textbox.insert("0.0", prompts.INITIAL_RESPONSE)

    freeze_button = ctk.CTkButton(root, text="Suggest Responses Continuously", command=None)
    freeze_button.grid(row=1, column=1, padx=10, pady=3, sticky="nsew")

    response_now_button = ctk.CTkButton(root, text="Suggest Response Now", command=None)
    response_now_button.grid(row=2, column=1, padx=10, pady=3, sticky="nsew")

    read_response_now_button = ctk.CTkButton(root, text="Suggest Response and Read", command=None)
    read_response_now_button.grid(row=3, column=1, padx=10, pady=3, sticky="nsew")

    update_interval_slider_label = ctk.CTkLabel(root, text="", font=("Arial", 12),
                                                text_color="#FFFCF2")
    update_interval_slider_label.grid(row=1, column=0, padx=10, pady=3, sticky="nsew")

    update_interval_slider = ctk.CTkSlider(root, from_=1, to=10, width=300, height=20,
                                           number_of_steps=9)
    update_interval_slider.set(2)
    update_interval_slider.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

    lang_combobox = ctk.CTkOptionMenu(root, width=15, values=list(LANGUAGES_DICT.values()))
    lang_combobox.grid(row=3, column=0, ipadx=60, padx=10, sticky="wn")

    # Order of returned components is important.
    # Add new components to the end
    return [transcript_textbox, response_textbox, update_interval_slider,
            update_interval_slider_label, freeze_button, lang_combobox,
            filemenu, response_now_button, read_response_now_button, editmenu]
