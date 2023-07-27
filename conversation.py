from heapq import merge
import constants
import configuration
import datetime

DEFAULT_PREAMBLE = """You are a casual pal, genuinely interested in the conversation at hand.""" \
                   """Please respond, in detail, to the conversation. Confidently give a """\
                   """straightforward response to the speaker, even if you don't understand """\
                   """them. Give your response in square brackets. DO NOT ask to repeat, """\
                   """and DO NOT ask for clarification. Just answer the speaker directly."""\
                   """A poor transcription of conversation is given below."""


class Conversation:
    """Encapsulates the complete conversation.
    Has text from Speakers, Microphone, LLM, Instructions to LLM
    """

    def __init__(self):
        self.transcript_data = {constants.PERSONA_SYSTEM: [],
                                constants.PERSONA_YOU: [],
                                constants.PERSONA_SPEAKER: [],
                                constants.PERSONA_ASSISTANT: []}
        transcript = self.transcript_data[constants.PERSONA_SYSTEM]
        transcript.append((f"{constants.PERSONA_SYSTEM}: [{DEFAULT_PREAMBLE}]\n\n", datetime.datetime.now()))
        config = configuration.Config().get_data()

    def clear_conversation_data(self):
        """Clear all conversation data
        """
        self.transcript_data[constants.PERSONA_YOU].clear()
        self.transcript_data[constants.PERSONA_SPEAKER].clear()
        self.transcript_data[constants.PERSONA_SYSTEM].clear()
        self.transcript_data[constants.PERSONA_ASSISTANT].clear()

    def update_conversation(self, persona: str, text: str, time_spoken, pop: bool = False):
        """Update conversation with new data
        Args:
        person: person this part of conversation is attributed to
        text: Actual words
        time_spoken: Time at which conversation happened, this is typically reported in local time
        """
        transcript = self.transcript_data[persona]
        if pop:
            transcript.pop()
        transcript.append((f"{persona}: [{text}]\n\n", time_spoken))

    def get_conversation(self,
                         sources: list = None,
                         length: int = 0):
        """Get the complete transcript
        Args:
        sources: Get data from which sources (You, Speaker, Assistant, System)
        length: Get the last length elements from the audio transcript.
                Default value = 0, gives the complete transcript
        """
        if sources is None:
            sources = [constants.PERSONA_YOU,
                       constants.PERSONA_SPEAKER,
                       constants.PERSONA_ASSISTANT,
                       constants.PERSONA_SYSTEM]

        combined_transcript = list(merge(
            self.transcript_data[constants.PERSONA_YOU][-length:],
            self.transcript_data[constants.PERSONA_SPEAKER][-length:],
            self.transcript_data[constants.PERSONA_ASSISTANT][-length:],
            self.transcript_data[constants.PERSONA_SYSTEM][-length:],
            key=lambda x: x[1]))
        combined_transcript = combined_transcript[-length:]
        return "".join([t[0] for t in combined_transcript])

    def get_merged_conversation(self, length: int = 0) -> list:
        """Creates a prompt to be sent to LLM (OpenAI by default)
           length: Get the last length elements from the audio transcript.
           Default value = 0, gives the complete transcript
        """
        # print(f'You: Length: {len(self.transcript_data[constants.PERSONA_YOU])}')
        # print(f'Speaker: Length: {len(self.transcript_data[constants.PERSONA_SPEAKER])}')
        # print(f'Assistant: Length: {len(self.transcript_data[constants.PERSONA_ASSISTANT])}')
        # print(f'System: Length: {len(self.transcript_data[constants.PERSONA_SYSTEM])}')

        combined_transcript = list(merge(
            self.transcript_data[constants.PERSONA_YOU][-length:],
            self.transcript_data[constants.PERSONA_SPEAKER][-length:],
            self.transcript_data[constants.PERSONA_ASSISTANT][-length:],
            key=lambda x: x[1]))
        combined_transcript = combined_transcript[-length:]

        combined_transcript.insert(0, (f"{constants.PERSONA_SYSTEM}: [{self.transcript_data[constants.PERSONA_SYSTEM][0]}]\n\n", datetime.datetime.now()))
        return combined_transcript
