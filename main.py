import soundcard as sc
import threading
from AudioTranscriber import AudioTranscriber
import GPTResponder
import customtkinter as ctk
from Microphone import Microphone
from AudioRecorder import AudioRecorder
import queue
from prompts import INITIAL_RESPONSE

def write_in_textbox(textbox, text):
    textbox.delete("0.0", "end")
    textbox.insert("0.0", text)

def update_transcript_UI(transcriber, textbox):
    transcript_string = transcriber.get_transcript()
    textbox.delete("0.0", "end")
    textbox.insert("0.0", transcript_string)
    textbox.after(300, update_transcript_UI, transcriber, textbox)

def update_response(transcriber, last_response, textbox, update_interval_slider_label, update_interval_slider):
    textbox.configure(state="normal")
    textbox.delete("0.0", "end")

    if transcriber.transcript_changed_event.is_set():
        transcriber.transcript_changed_event.clear() 
        transcript_string = transcriber.get_transcript()
        response = GPTResponder.generate_response_from_transcript(transcript_string)
        if response != '':
            last_response = response

    textbox.insert("0.0", last_response)
    textbox.configure(state="disabled")
    update_interval = int(update_interval_slider.get())
    update_interval_slider_label.configure(text=f"Update interval: {update_interval} seconds")
    textbox.after(int(update_interval * 1000), update_response, transcriber, last_response, textbox, update_interval_slider_label, update_interval_slider)

def clear_transcript_data(transcriber_mic, transcriber_speaker):
    transcriber_mic.transcript_data.clear()
    transcriber_speaker.transcript_data.clear()

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    root = ctk.CTk()
    root.title("Ecoute")
    root.configure(bg='#252422')
    root.geometry("1000x600")
    font_size = 20

    transcript_textbox = ctk.CTkTextbox(root, width=300, font=("Arial", font_size), text_color='#FFFCF2', wrap="word")
    transcript_textbox.grid(row=0, column=0, padx=10, pady=20, sticky="nsew")

    response_textbox = ctk.CTkTextbox(root, width=300, font=("Arial", font_size), text_color='#639cdc', wrap="word")
    response_textbox.grid(row=0, column=1, padx=10, pady=20, sticky="nsew")

     # Add the clear transcript button to the UI
    clear_transcript_button = ctk.CTkButton(root, text="Clear Transcript", command=lambda: clear_transcript_data(user_transcriber, transcriber_speaker))
    clear_transcript_button.grid(row=1, column=0, padx=10, pady=3, sticky="nsew")
    # empty label, necessary for proper grid spacing
    update_interval_slider_label = ctk.CTkLabel(root, text=f"", font=("Arial", 12), text_color="#FFFCF2")
    update_interval_slider_label.grid(row=1, column=1, padx=10, pady=3, sticky="nsew")

    # Create the update interval slider
    update_interval_slider = ctk.CTkSlider(root, from_=1, to=10, width=300, height=20, number_of_steps=9)
    update_interval_slider.set(2)
    update_interval_slider.grid(row=3, column=1, padx=10, pady=10, sticky="nsew")
    update_interval_slider_label = ctk.CTkLabel(root, text=f"Update interval: {update_interval_slider.get()} seconds", font=("Arial", 12), text_color="#FFFCF2")
    update_interval_slider_label.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

    audio_queue = queue.Queue()

    user_mirophone = Microphone(str(sc.default_microphone().name), False)
    user_audio_recorder = AudioRecorder(user_mirophone)

    record_user = threading.Thread(target=user_audio_recorder.record_into_queue, args=(audio_queue, "You",))
    record_user.start()

    speaker_mirophone = Microphone(str(sc.default_speaker().name), True)
    speaker_audio_recorder = AudioRecorder(speaker_mirophone)

    record_speaker = threading.Thread(target=speaker_audio_recorder.record_into_queue, args=(audio_queue, "Speaker",))
    record_speaker.start()

    global_transcriber = AudioTranscriber()
    transcribe = threading.Thread(target=global_transcriber.create_transcription_from_queue, args=(audio_queue,))
    transcribe.start()

    root.grid_rowconfigure(0, weight=100)
    root.grid_rowconfigure(1, weight=10)
    root.grid_rowconfigure(2, weight=1)
    root.grid_rowconfigure(3, weight=1)
    root.grid_rowconfigure(4, weight=1)
    root.grid_columnconfigure(0, weight=2)
    root.grid_columnconfigure(1, weight=1)

    update_transcript_UI(global_transcriber, transcript_textbox)
    update_response(global_transcriber, INITIAL_RESPONSE, response_textbox, update_interval_slider_label, update_interval_slider)
 
    root.mainloop()