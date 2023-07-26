import threading
import argparse
from argparse import RawTextHelpFormatter
import time
import requests
import subprocess
from requests.exceptions import ConnectionError
from AudioTranscriber import AudioTranscriber
from GPTResponder import GPTResponder
import customtkinter as ctk
import TranscriberModels
import interactions
import ui
from language import LANGUAGES_DICT
import GlobalVars
import configuration
import conversation

def main():
    # Set up all arguments
    cmd_args = argparse.ArgumentParser(description='Command Line Arguments for Transcribe',
                                       formatter_class=RawTextHelpFormatter)
    cmd_args.add_argument('-a', '--api', action='store_true',
                          help='Use the online Open AI API for transcription.\
                          \nThis option requires an API KEY and will consume Open AI credits.')
    cmd_args.add_argument('-k', '--api_key', action='store', default=None,
                          help='API Key for accessing OpenAI APIs. This is an optional parameter.\
                            Without the API Key only transcription works.')
    cmd_args.add_argument('-m', '--model', action='store', choices=['tiny', 'base', 'small'],
                          default='tiny',
                          help='Specify the model to use for transcription.'
                          '\nBy default tiny english model is part of the install.'
                          '\ntiny multi-lingual model has to be downloaded from the link \
                            https://drive.google.com/file/d/1M4AFutTmQROaE9xk2jPc5Y4oFRibHhEh/view?usp=drive_link'
                          '\nbase english model has to be downloaded from the link \
                            https://drive.google.com/file/d/1E44DVjpfZX8tSrSagaDJXU91caZOkwa6/view?usp=drive_link'
                          '\nbase multi-lingual model has to be downloaded from the link \
                            https://drive.google.com/file/d/1UcqU_D0cPFqq_nckSfstMBfogFsvR-KR/view?usp=drive_link'
                          '\nsmall english model has to be downloaded from the link \
                            https://drive.google.com/file/d/1vhtoZCwfYGi5C4jK1r-QVr5GobSBnKiH/view?usp=drive_link'
                          '\nsmall multi-lingual model has to be downloaded from the link \
                            https://drive.google.com/file/d/1bl8er_st8WPZKPWVeYMNlaUi9IzR3jEZ/view?usp=drive_link'
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

    config = configuration.Config().get_data()

    # Two calls to GlobalVars.TranscriptionGlobals is on purpose
    global_vars = GlobalVars.TranscriptionGlobals()

    global_vars = GlobalVars.TranscriptionGlobals(key=config["OpenAI"]["api_key"])

    # Command line arg for api_key takes preference over api_key specified in parameters.yaml file
    if args.api_key is not None:
        api_key = args.api_key
    else:
        api_key = config['OpenAI']['api_key']

    global_vars.api_key = api_key

    model = TranscriberModels.get_model(args.api, model=args.model)

    root = ctk.CTk()
    ui_components = ui.create_ui_components(root)
    transcript_textbox = ui_components[0]
    response_textbox = ui_components[1]
    update_interval_slider = ui_components[2]
    update_interval_slider_label = ui_components[3]
    global_vars.freeze_button = ui_components[4]
    lang_combobox = ui_components[5]

    global_vars.user_audio_recorder.record_into_queue(global_vars.audio_queue)

    time.sleep(2)

    global_vars.speaker_audio_recorder.record_into_queue(global_vars.audio_queue)
    global_vars.freeze_state = [True]
    convo = conversation.Conversation()

    # Transcribe and Respond threads, both work on the same instance of the AudioTranscriber class
    global_vars.transcriber = AudioTranscriber(global_vars.user_audio_recorder.source,
                                               global_vars.speaker_audio_recorder.source,
                                               model,
                                               convo=convo)
    transcribe_thread = threading.Thread(target=global_vars.transcriber.transcribe_audio_queue,
                                         args=(global_vars.audio_queue,))
    transcribe_thread.daemon = True
    transcribe_thread.start()

    global_vars.responder = GPTResponder(convo=convo)

    respond_thread = threading.Thread(target=global_vars.responder.respond_to_transcriber,
                                      args=(global_vars.transcriber,))
    respond_thread.daemon = True
    respond_thread.start()

    print("READY")

    root.grid_rowconfigure(0, weight=100)
    root.grid_rowconfigure(1, weight=1)
    root.grid_rowconfigure(2, weight=1)
    root.grid_rowconfigure(3, weight=1)
    root.grid_columnconfigure(0, weight=2)
    root.grid_columnconfigure(1, weight=1)

    ui_cb = ui.ui_callbacks()
    global_vars.freeze_button.configure(command=ui_cb.freeze_unfreeze)
    label_text = f'Update Response interval: {update_interval_slider.get()} seconds'
    update_interval_slider_label.configure(text=label_text)

    lang_combobox.configure(command=model.change_lang)

    ui.update_transcript_ui(global_vars.transcriber, transcript_textbox)
    ui.update_response_ui(global_vars.responder, response_textbox, update_interval_slider_label,
                          update_interval_slider, global_vars.freeze_state)

    root.mainloop()


if __name__ == "__main__":
    main()
