import openai
import GlobalVars
from prompts import create_prompt, INITIAL_RESPONSE
import time
import conversation
import constants
import configuration

# Number of phrases to use for generating a response
MAX_PHRASES = 20


class GPTResponder:
    def __init__(self, convo: conversation.Conversation):
        self.response = INITIAL_RESPONSE
        self.response_interval = 2
        self.gl_vars = GlobalVars.TranscriptionGlobals()
        openai.api_key = self.gl_vars.api_key
        self.conversation = convo
        self.config = configuration.Config().get_data()
        self.model = self.config['OpenAI']['ai_model']

    def generate_response_from_transcript_no_check(self, transcript):
        try:
            prompt_content = create_prompt(transcript)
            response = openai.ChatCompletion.create(
                    model=self.model,
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

    def generate_response_from_transcript(self, transcript):
        """Ping OpenAI LLM model to get response from the Assistant
        """

        if self.gl_vars.freeze_state[0]:
            return ''

        return generate_response_from_transcript_no_check(self, transcript)

    def respond_to_transcriber(self, transcriber):
        while True:

            if transcriber.transcript_changed_event.is_set():
                start_time = time.time()

                transcriber.transcript_changed_event.clear()
                transcript_string = transcriber.get_transcript(length=MAX_PHRASES)
                response = self.generate_response_from_transcript(transcript_string)

                end_time = time.time()  # Measure end time
                execution_time = end_time - start_time  # Calculate time to execute the function

                if response != '':
                    self.response = response
                    self.conversation.update_conversation(persona=constants.PERSONA_ASSISTANT,
                                                          text=response,
                                                          time_spoken=end_time)

                remaining_time = self.response_interval - execution_time
                if remaining_time > 0:
                    time.sleep(remaining_time)
            else:
                time.sleep(0.3)

    def update_response_interval(self, interval):
        self.response_interval = interval
