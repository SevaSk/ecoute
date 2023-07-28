import datetime
import time
import GlobalVars
import prompts
import openai
import conversation
import constants
import configuration
import app_logging as al


root_logger = al.get_logger()


class GPTResponder:
    """Handles all interactions with openAI LLM / ChatGPT
    """
    def __init__(self, convo: conversation.Conversation):
        root_logger.info(GPTResponder.__name__)
        self.response = prompts.INITIAL_RESPONSE
        self.response_interval = 2
        self.gl_vars = GlobalVars.TranscriptionGlobals()
        openai.api_key = self.gl_vars.api_key
        self.conversation = convo
        self.config = configuration.Config().get_data()
        self.model = self.config['OpenAI']['ai_model']

    def generate_response_from_transcript_no_check(self, transcript) -> str:
        """Ping LLM to get a suggested response right away.
           Gets a response even if the continuous suggestion option is disabled.
        """
        try:
            # prompt_content = create_prompt(transcript)
            # prompt_api_message = [{"role": "system", "content": prompt_content}]
            prompt_api_message = prompts.create_single_turn_prompt_message(transcript)
            multiturn_prompt_content = self.conversation.get_merged_conversation(
                length=constants.MAX_TRANSCRIPTION_PHRASES_FOR_LLM)
            multiturn_prompt_api_message = prompts.create_multiturn_prompt(multiturn_prompt_content)
            # print(f'Usual prompt api message: {prompt_api_message}')
            # print(f'Multiturn prompt: {multiturn_prompt_api_message}')
            usual_response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=prompt_api_message,
                    temperature=0.0
            )

        except Exception as exception:
            print(exception)
            root_logger.error('Error when attempting to get a response from LLM.')
            root_logger.exception(exception)
            return prompts.INITIAL_RESPONSE

        usual_full_response = usual_response.choices[0].message.content
        try:
            return usual_full_response.split('[')[1].split(']')[0]
        except Exception as exception:
            root_logger.error('Error parsing response from LLM.')
            root_logger.exception(exception)
            return prompts.INITIAL_RESPONSE

    def generate_response_from_transcript(self, transcript):
        """Ping OpenAI LLM model to get response from the Assistant
        """

        if self.gl_vars.freeze_state[0]:
            return ''

        return self.generate_response_from_transcript_no_check(transcript)

    def respond_to_transcriber(self, transcriber):
        """Thread method to continously update the transcript
        """
        while True:

            if transcriber.transcript_changed_event.is_set():
                start_time = time.time()

                transcriber.transcript_changed_event.clear()
                transcript_string = transcriber.get_transcript(
                    length=constants.MAX_TRANSCRIPTION_PHRASES_FOR_LLM)
                response = self.generate_response_from_transcript(transcript_string)

                end_time = time.time()  # Measure end time
                execution_time = end_time - start_time  # Calculate time to execute the function

                if response != '':
                    self.response = response
                    self.conversation.update_conversation(persona=constants.PERSONA_ASSISTANT,
                                                          text=response,
                                                          time_spoken=datetime.datetime.now())

                remaining_time = self.response_interval - execution_time
                if remaining_time > 0:
                    time.sleep(remaining_time)
            else:
                time.sleep(0.3)

    def update_response_interval(self, interval):
        """Change the interval for pinging LLM
        """
        root_logger.info(GPTResponder.update_response_interval.__name__)
        self.response_interval = interval
