from openai import OpenAI
import os
from prompts import create_prompt, INITIAL_RESPONSE
import time

# Get API key from environment variable or keys.py file
try:
    from keys import OPENAI_API_KEY
    client = OpenAI(api_key=OPENAI_API_KEY)
except ImportError:
    # Fallback to environment variable
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_response_from_transcript(transcript):
    try:
        response = client.chat.completions.create(
                model="gpt-4o-mini",  # Using the latest model
                messages=[{"role": "system", "content": create_prompt(transcript)}],
                temperature=0.6,
                max_tokens=500  # Limiting token usage for faster responses
        )
    except Exception as e:
        print(e)
        return ''
    full_response = response.choices[0].message.content
    try:
        # Extract text between square brackets
        if '[' in full_response and ']' in full_response:
            return full_response.split('[')[1].split(']')[0]
        # Fallback if response doesn't contain square brackets
        return full_response
    except Exception as e:
        print(f"Error parsing response: {e}")
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

    def update_response_interval(self, interval):
        self.response_interval = interval