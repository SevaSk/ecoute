import datetime
import time
import pprint
import openai
import GlobalVars
import prompts
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
           Updates the conversation object with the response from LLM.
        """
        try:
            prompt_api_message = prompts.create_single_turn_prompt_message(transcript)
            multiturn_prompt_content = self.conversation.get_merged_conversation(
                length=constants.MAX_TRANSCRIPTION_PHRASES_FOR_LLM)
            multiturn_prompt_api_message = prompts.create_multiturn_prompt(multiturn_prompt_content)
            # pprint.pprint(f'Prompt api message: {prompt_api_message}')
            # print(f'Multiturn prompt for ChatGPT: {multiturn_prompt_api_message}')
            usual_response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=prompt_api_message,
                    temperature=0.0
            )
            # Multi turn response is only effective when continuous mode is off.
            # In continuous mode, there are far too many responses from LLM,
            # they confuse the LLM if that many responses are replayed back to LLM.
            multi_turn_response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=multiturn_prompt_api_message,
                    temperature=0.0
            )

            # print('-------- Single Turn --------')
            # pprint.pprint(f'message={prompt_api_message}', width=120)
            # pprint.pprint(f'response={usual_response}', width=120)
            # print('-------- Multi Turn --------')
            # pprint.pprint(f'message={multiturn_prompt_api_message}', width=120)
            # pprint.pprint(f'response={multi_turn_response}', width=120)
            # print('-------- -------- -------- -------- -------- --------')

        except Exception as exception:
            print(exception)
            root_logger.error('Error when attempting to get a response from LLM.')
            root_logger.exception(exception)
            return prompts.INITIAL_RESPONSE

        # single_turn_response_content = usual_response.choices[0].message.content
        multi_turn_response_content = multi_turn_response.choices[0].message.content
        # pprint.pprint(f'Prompt api response: {usual_response}')
        try:
            # The original way of processing the response.
            # It causes issues when there are multiple questions in the transcript.
            # response = single_turn_response_content.split('[')[1].split(']')[0]
            # processed_single_turn_response = self.process_response(single_turn_response_content)
            processed_multi_turn_response = self.process_response(multi_turn_response_content)
            self.update_conversation(persona=constants.PERSONA_ASSISTANT,
                                     response=processed_multi_turn_response)
            return processed_multi_turn_response
        except Exception as exception:
            root_logger.error('Error parsing response from LLM.')
            root_logger.exception(exception)
            return prompts.INITIAL_RESPONSE

    def process_response(self, input_str: str) -> str:
        """ Extract relevant data from LLM response.
        """
        lines = input_str.split(sep='\n')
        response = ''
        for line in lines:
            # Skip any responses that contain content like
            # Speaker 1: <Some statement>
            # This is generated content added by OpenAI that can be skipped
            if 'Speaker' in line and ':' in line:
                continue
            response = response + line.strip().strip('[').strip(']')

        return response

    def generate_response_from_transcript(self, transcript):
        """Ping OpenAI LLM model to get response from the Assistant
        """

        if self.gl_vars.freeze_state[0]:
            return ''

        return self.generate_response_from_transcript_no_check(transcript)

    def update_conversation(self, response, persona):
        if response != '':
            self.response = response
            self.conversation.update_conversation(persona=persona,
                                                  text=response,
                                                  time_spoken=datetime.datetime.now())

    def respond_to_transcriber(self, transcriber):
        """Thread method to continously update the transcript
        """
        while True:

            if transcriber.transcript_changed_event.is_set():
                start_time = time.time()

                transcriber.transcript_changed_event.clear()
                response = ''

                # Do processing only if LLM transcription is enabled
                if not self.gl_vars.freeze_state[0]:
                    transcript_string = transcriber.get_transcript(
                        length=constants.MAX_TRANSCRIPTION_PHRASES_FOR_LLM)
                    response = self.generate_response_from_transcript(transcript_string)

                end_time = time.time()  # Measure end time
                execution_time = end_time - start_time  # Calculate time to execute the function

                remaining_time = self.response_interval - execution_time
                if remaining_time > 0:
                    time.sleep(remaining_time)
            else:
                time.sleep(self.response_interval)

    def update_response_interval(self, interval):
        """Change the interval for pinging LLM
        """
        root_logger.info(GPTResponder.update_response_interval.__name__)
        self.response_interval = interval


if __name__ == "__main__":
    print('GPTResponder')
