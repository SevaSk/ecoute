from CustomPrompts import PREAMBLE, EPILOGUE

INITIAL_RESPONSE = '👋 Welcome to Transcribe 🤝'


def create_prompt(transcript):
    return f'{PREAMBLE} \
 \
{transcript}.\
{EPILOGUE}'


def create_single_turn_prompt_message(transcript: str):
    message = f'{PREAMBLE} \
 \
{transcript}.\
{EPILOGUE}'

    prompt_api_message = [{"role": "system", "content": message}]
    return prompt_api_message


def create_multiturn_prompt(convo: list):
    # print(convo)
    return ''
