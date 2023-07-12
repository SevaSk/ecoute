import customtkinter as ctk
import AudioTranscriber
import prompts
from language import LANGUAGES


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
    transcript_string = transcriber.get_transcript()
    write_in_textbox(textbox, transcript_string)
    textbox.see("end")
    textbox.after(300, update_transcript_ui, transcriber, textbox)


def update_response_ui(responder, textbox, update_interval_slider_label,
                       update_interval_slider, freeze_state):
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
        update_interval_slider_label.configure(text=f"Update interval: \
                                               {update_interval} seconds")

    textbox.after(300, update_response_ui, responder, textbox,
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
    response_textbox.insert("0.0", prompts.INITIAL_RESPONSE)

    freeze_button = ctk.CTkButton(root, text="Suggest Response", command=None)
    freeze_button.grid(row=1, column=1, padx=10, pady=3, sticky="nsew")

    update_interval_slider_label = ctk.CTkLabel(root, text="", font=("Arial", 12),
                                                text_color="#FFFCF2")
    update_interval_slider_label.grid(row=2, column=1, padx=10, pady=3, sticky="nsew")

    update_interval_slider = ctk.CTkSlider(root, from_=1, to=10, width=300, height=20,
                                           number_of_steps=9)
    update_interval_slider.set(2)
    update_interval_slider.grid(row=3, column=1, padx=10, pady=10, sticky="nsew")

    copy_button = ctk.CTkButton(root, text="Copy Audio Transcript", command=None)
    copy_button.grid(row=2, column=0, padx=10, pady=3, sticky="nsew")

    save_file_button = ctk.CTkButton(root, text="Save Audio Transcript to File", command=None)
    save_file_button.grid(row=3, column=0, padx=10, pady=3, sticky="nsew")

    lang_combobox = ctk.CTkOptionMenu(root, values=list(LANGUAGES.values()))
    lang_combobox.grid(row=4, column=1, padx=200, pady=10, sticky="nsew")

    transcript_button = ctk.CTkButton(root, text="Pause Transcript", command=None)
    transcript_button.grid(row=4, column=0, padx=10, pady=3, sticky="nsew")

    # Order of returned components is important.
    # Add new components to the end
    return [transcript_textbox, response_textbox, update_interval_slider,
            update_interval_slider_label, freeze_button, copy_button,
            save_file_button, lang_combobox, transcript_button]
