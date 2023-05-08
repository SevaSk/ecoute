# pyinstaller --onedir --add-data "C:/Users/mcfar/AppData/Local/Programs/Python/Python310/Lib/site-packages/customtkinter;customtkinter/" --noconfirm --windowed --noconsole main.py

import threading
from AudioTranscriber import AudioTranscriber, TRANSCRIPT_LIMIT
from gpt_responder import GPTResponder
import customtkinter as ctk
from Microphone import Microphone
import soundcard as sc

def write_in_textbox(textbox, text):
    textbox.delete("0.0", "end")
    textbox.insert("0.0", text)

#TODO make fast leetcode :)
def create_transcript_string(transcriber_mic, transcriber_speaker, reverse = True):
    transcript_string = ""

    mic_transcript = transcriber_mic.get_transcript()
    speaker_transcript = transcriber_speaker.get_transcript()
    total_transcript = [('You', data) for data in mic_transcript] + [('Speaker', data) for data in speaker_transcript]
    sorted_transcript = sorted(total_transcript, key = lambda x: x[1]['timestamp'], reverse = reverse)
    for source, line in sorted_transcript[:TRANSCRIPT_LIMIT]:
        transcript_string += source + ": [" + line['utterance'] + ']\n\n'
    return transcript_string

def update_transcript_UI(transcriber_mic, transcriber_thread_mic, transcriber_speaker, transcriber_thread_speaker, textbox):
    transcript_string = create_transcript_string(transcriber_mic, transcriber_speaker, reverse=True)
    textbox.delete("0.0", "end")
    textbox.insert("0.0", transcript_string)
    textbox.after(200, update_transcript_UI, transcriber_mic, transcriber_thread_mic, transcriber_speaker, transcriber_thread_speaker, textbox)

def update_response_UI(transcriber_mic, transcriber_speaker, responder, textbox, update_interval_slider_label, update_interval_slider):
    transcript_string = create_transcript_string(transcriber_mic, transcriber_speaker,reverse=False)
    t = threading.Thread(target=lambda: responder.generate_response_from_transcript(transcript_string))
    t.start()
    textbox.configure(state="normal")
    textbox.delete("0.0", "end")
    textbox.insert("0.0", responder.last_response)
    textbox.configure(state="disabled")
    update_interval = int(update_interval_slider.get())
    update_interval_slider_label.configure(text=f"Update interval: {update_interval} seconds")
    textbox.after(int(update_interval * 1000), update_response_UI, transcriber_mic, transcriber_speaker, responder, textbox, update_interval_slider_label, update_interval_slider)

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
    clear_transcript_button = ctk.CTkButton(root, text="Clear Transcript", command=lambda: clear_transcript_data(transcriber_mic, transcriber_speaker))
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

    responder = GPTResponder()

    user_mirophone = Microphone(str(sc.default_microphone().name), False)
    transcriber_mic = AudioTranscriber(lang='en-US', microphone=user_mirophone)
    recorder_thread_mic = threading.Thread(target=transcriber_mic.record_into_queue)
    transcriber_thread_mic = threading.Thread(target=transcriber_mic.transcribe_from_queue)
    recorder_thread_mic.start()
    transcriber_thread_mic.start()

    speaker_mirophone = Microphone(str(sc.default_speaker().name), True)
    transcriber_speaker = AudioTranscriber(lang='en-US', microphone=speaker_mirophone)
    recorder_thread_speaker = threading.Thread(target=transcriber_speaker.record_into_queue)
    transcriber_thread_speaker = threading.Thread(target=transcriber_speaker.transcribe_from_queue)
    recorder_thread_speaker.start()
    transcriber_thread_speaker.start()

    root.grid_rowconfigure(0, weight=100)
    root.grid_rowconfigure(1, weight=10)
    root.grid_rowconfigure(2, weight=1)
    root.grid_rowconfigure(3, weight=1)
    root.grid_rowconfigure(4, weight=1)
    root.grid_columnconfigure(0, weight=2)
    root.grid_columnconfigure(1, weight=1)

    update_transcript_UI(transcriber_mic, transcriber_thread_mic, transcriber_speaker, transcriber_thread_speaker, transcript_textbox)
    update_response_UI(transcriber_mic, transcriber_speaker, responder, response_textbox, update_interval_slider_label, update_interval_slider)

    root.mainloop()

    transcriber_thread_mic.join()
    transcriber_thread_speaker.join()