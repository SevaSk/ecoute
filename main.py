import soundcard as sc
import threading
from AudioTranscriber import AudioTranscriber
from GPTResponder import GPTResponder
import customtkinter as ctk
from Microphone import Microphone
import AudioRecorder 
import queue
import os
import time

def write_in_textbox(textbox, text):
    textbox.delete("0.0", "end")
    textbox.insert("0.0", text)

def update_transcript_UI(transcriber, textbox):
    transcript_string = transcriber.get_transcript()
    textbox.delete("0.0", "end")
    textbox.insert("0.0", transcript_string)
    textbox.after(300, update_transcript_UI, transcriber, textbox)

def update_response_UI(responder, textbox, update_interval_slider_label, update_interval_slider):
    response = responder.response

    textbox.configure(state="normal")
    textbox.delete("0.0", "end")
    textbox.insert("0.0", response)
    textbox.configure(state="disabled")
    update_interval = int(update_interval_slider.get())

    responder.update_response_interval(update_interval)
    update_interval_slider_label.configure(text=f"Update interval: {update_interval} seconds")

    textbox.after(300, update_response_UI, responder, textbox, update_interval_slider_label, update_interval_slider)

def clear_transcript_data(transcriber):
    transcriber.transcript_data.clear()

def clear_temp_files():
    for file in os.listdir():
        if file.startswith('temp_'):
            os.remove(file)

if __name__ == "__main__":
    clear_temp_files()

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

    user_audio_recorder = AudioRecorder.DefaultMicRecorder()
    user_audio_recorder.record_into_queue(audio_queue)

    time.sleep(2)

    speaker_audio_recorder = AudioRecorder.DefaultSpeakerRecorder()
    speaker_audio_recorder.record_into_queue(audio_queue)

    global_transcriber = AudioTranscriber(user_audio_recorder, speaker_audio_recorder)
    transcribe = threading.Thread(target=global_transcriber.create_transcription_from_queue, args=(audio_queue,))
    transcribe.start()

    responder = GPTResponder()
    respond = threading.Thread(target=responder.respond_to_transcriber, args=(global_transcriber,))
    respond.start()

    print("READY")

    root.grid_rowconfigure(0, weight=100)
    root.grid_rowconfigure(1, weight=10)
    root.grid_rowconfigure(2, weight=1)
    root.grid_rowconfigure(3, weight=1)
    root.grid_rowconfigure(4, weight=1)
    root.grid_columnconfigure(0, weight=2)
    root.grid_columnconfigure(1, weight=1)

     # Add the clear transcript button to the UI
    clear_transcript_button = ctk.CTkButton(root, text="Clear Transcript", command=lambda: clear_transcript_data(global_transcriber, ))
    clear_transcript_button.grid(row=1, column=0, padx=10, pady=3, sticky="nsew")

    update_transcript_UI(global_transcriber, transcript_textbox)
    update_response_UI(responder, response_textbox, update_interval_slider_label, update_interval_slider)
 
    root.mainloop()