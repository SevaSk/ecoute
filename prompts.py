from CustomPrompts import PREAMBLE, EPILOGUE

INITIAL_RESPONSE = '👋 Welcome to Transcribe 🤝'


def create_prompt(transcript):
    return f'{PREAMBLE} \
 \
{transcript}.\
{EPILOGUE}'
