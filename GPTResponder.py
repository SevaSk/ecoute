import openai
from keys import OPENAI_API_KEY
from prompts import create_prompt

openai.api_key = OPENAI_API_KEY

def generate_response_from_transcript(transcript):
    response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",
            messages=[{"role": "system", "content": create_prompt(transcript)}],
            temperature = 0.0
    )
    full_response = response.choices[0].message.content
    try:
        return full_response.split('[')[1].split(']')[0]
    except:
        return ''