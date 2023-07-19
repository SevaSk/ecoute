import openai
import GlobalVars
from prompts import create_prompt, INITIAL_RESPONSE
import time

openai.api_key = GlobalVars.TranscriptionGlobals().api_key
# Number of phrases to use for generating a response
MAX_PHRASES = 10


def generate_response_from_transcript(transcript):
    try:
        prompt_content = create_prompt(transcript)
        response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0301",
                messages=[{"role": "system", "content": prompt_content}],
                temperature=0.0
        )
    except Exception as exception:
        print(exception)
        return ''
    full_response = response.choices[0].message.content
    try:
        return full_response.split('[')[1].split(']')[0]
    except:
        return ''


class GPTResponder:
    def __init__(self):
        self.response = INITIAL_RESPONSE
        self.response_interval = 2

    def respond_to_transcriber(self, transcriber):
        while True:
            if transcriber.transcript_changed_event.is_set():
                start_time = time.time()

                transcriber.transcript_changed_event.clear()
                transcript_string = transcriber.get_transcript(length=MAX_PHRASES)
                response = generate_response_from_transcript(transcript_string)

                end_time = time.time()  # Measure end time
                execution_time = end_time - start_time  # Calculate time to execute the function

                if response != '':
                    self.response = response

                remaining_time = self.response_interval - execution_time
                if remaining_time > 0:
                    time.sleep(remaining_time)
            else:
                time.sleep(0.3)

    def update_response_interval(self, interval):
        self.response_interval = interval
