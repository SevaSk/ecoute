import openai
from keys import OPENAI_API_KEY
from prompts import create_prompt, INITIAL_RESPONSE

openai.api_key = OPENAI_API_KEY

class GPTResponder:
    def __init__(self):
        self.last_transcript = ""
        self.last_response = INITIAL_RESPONSE

    def generate_response_from_transcript(self, transcript):
        if transcript == self.last_transcript:
            return self.last_response
        response = openai.ChatCompletion.create(
              model="gpt-3.5-turbo-0301",
              messages=[{"role": "system", "content": create_prompt(transcript)}],
              temperature = 0.0
        )
        full_response = response.choices[0].message.content
        try:
            conversational_response = full_response.split('[')[1].split(']')[0]
        except:
            return self.last_response
        self.last_transcript = transcript
        self.last_response = conversational_response
        return conversational_response