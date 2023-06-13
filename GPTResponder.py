import openai
from keys import OPENAI_API_KEY, ACCESS_TOKEN
from prompts import create_prompt, INITIAL_RESPONSE
import time
from revChatGPT.V1 import Chatbot
chatbot = Chatbot(config={
  "access_token": f"{ACCESS_TOKEN}"
})
openai.api_key = OPENAI_API_KEY

def generate_response_from_transcript(transcript):
    try:
        response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0301",
                messages=[{"role": "system", "content": create_prompt(transcript)}],
                temperature = 0.0
        )
    except Exception as e:
        print(e)
        return ''
    full_response = response.choices[0].message.content
    try:
        return full_response.split('[')[1].split(']')[0]
    except:
        return ''
    
def generate_response_from_transcript_revChatGPT(transcript):
    try:
        response = ''
        for data in chatbot.ask(
            create_prompt(transcript)
        ):
            response = data["message"]
        return response
    except Exception as e:
        print(e)
        return ''
    
class GPTResponder:
    def __init__(self, revChatGPT=False):
        self.response = INITIAL_RESPONSE
        self.response_interval = 2
        self.respond_to_transcriber = self.respond_to_transcriber_revChatGPT if revChatGPT else self.respond_to_transcriber

    def respond_to_transcriber(self, transcriber):
        while True:
            if transcriber.transcript_changed_event.is_set():
                start_time = time.time()

                transcriber.transcript_changed_event.clear() 
                transcript_string = transcriber.get_transcript()
                response = generate_response_from_transcript(transcript_string)
                
                end_time = time.time()  # Measure end time
                execution_time = end_time - start_time  # Calculate the time it took to execute the function
                
                if response != '':
                    self.response = response

                remaining_time = self.response_interval - execution_time
                if remaining_time > 0:
                    time.sleep(remaining_time)
            else:
                time.sleep(0.3)

    def respond_to_transcriber_revChatGPT(self, transcriber):
        while True:
            if transcriber.transcript_changed_event.is_set():
                start_time = time.time()

                transcriber.transcript_changed_event.clear() 
                transcript_string = transcriber.get_transcript()
                response = generate_response_from_transcript_revChatGPT(transcript_string)
                
                end_time = time.time()  # Measure end time
                execution_time = end_time - start_time  # Calculate the time it took to execute the function
                
                if response != '':
                    self.response = response

                remaining_time = self.response_interval - execution_time
                if remaining_time > 0:
                    time.sleep(remaining_time)
            else:
                time.sleep(0.3)

    def update_response_interval(self, interval):
        self.response_interval = interval