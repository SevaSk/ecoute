from heapq import merge
import datetime
# import pprint
import constants
import configuration


class Conversation:
    """Encapsulates the complete conversation.
    Has text from Speakers, Microphone, LLM, Instructions to LLM
    """

    def __init__(self):
        self.transcript_data = {constants.PERSONA_SYSTEM: [],
                                constants.PERSONA_YOU: [],
                                constants.PERSONA_SPEAKER: [],
                                constants.PERSONA_ASSISTANT: []}
        config = configuration.Config().get_data()
        prompt = config["OpenAI"]["system_prompt"]
        self.update_conversation(persona=constants.PERSONA_SYSTEM, text=prompt,
                                 time_spoken=datetime.datetime.now())
        initial_convo: dict = config["OpenAI"]["initial_convo"]
        # Read the initial conversation from parameters.yaml file and add to the convo
        for _, value in initial_convo.items():
            role = value['role']
            content = value['content']
            self.update_conversation(persona=role, text=content,
                                     time_spoken=datetime.datetime.now())
        self.last_update: datetime.datetime = datetime.datetime.now()

    def clear_conversation_data(self):
        """Clear all conversation data
        """
        self.transcript_data[constants.PERSONA_YOU].clear()
        self.transcript_data[constants.PERSONA_SPEAKER].clear()
        self.transcript_data[constants.PERSONA_SYSTEM].clear()
        self.transcript_data[constants.PERSONA_ASSISTANT].clear()
        self.last_update = datetime.datetime.now()

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
        self.last_update = datetime.datetime.now()

    def get_conversation(self,
                         sources: list = None,
                         length: int = 0,
                         reverse: bool = False) -> list:
        """Get the transcript based on specified sources
        Args:
        sources: Get data from which sources (You, Speaker, Assistant, System)
        length: Get the last length elements from the audio transcript.
                Default value = 0, gives the complete transcript for chosen sources
        reverse: reverse the sort order or keep it in chronological order
        """
        if sources is None:
            sources = [constants.PERSONA_YOU,
                       constants.PERSONA_SPEAKER,
                       constants.PERSONA_ASSISTANT,
                       constants.PERSONA_SYSTEM]

        combined_transcript = list(merge(
            self.transcript_data[constants.PERSONA_YOU][-length:] if constants.PERSONA_YOU in sources else [],
            self.transcript_data[constants.PERSONA_SPEAKER][-length:] if constants.PERSONA_SPEAKER in sources else [],
            self.transcript_data[constants.PERSONA_ASSISTANT][-length:] if constants.PERSONA_ASSISTANT in sources else [],
            self.transcript_data[constants.PERSONA_SYSTEM][-length:] if constants.PERSONA_SYSTEM in sources else [],
            key=lambda x: x[1], reverse=reverse))
        combined_transcript = combined_transcript[-length:]
        return "".join([t[0] for t in combined_transcript])

    def get_merged_conversation(self, length: int = 0, reverse: bool = False) -> list:
        """Creates a prompt to be sent to LLM (OpenAI by default)
           length: Get the last length elements from the audio transcript.
           Initial system prompt is always part of the return value
           Default value = 0, gives the complete transcript
        """
        # print(f'You: Length: {len(self.transcript_data[constants.PERSONA_YOU])}')
        # print(f'Speaker: Length: {len(self.transcript_data[constants.PERSONA_SPEAKER])}')
        # print(f'Assistant: Length: {len(self.transcript_data[constants.PERSONA_ASSISTANT])}')
        # print(f'System: Length: {len(self.transcript_data[constants.PERSONA_SYSTEM])}')

        combined_transcript = self.transcript_data[constants.PERSONA_SYSTEM]
        combined_transcript = list(merge(
            combined_transcript,
            self.transcript_data[constants.PERSONA_YOU][-length:],
            self.transcript_data[constants.PERSONA_SPEAKER][-length:],
            self.transcript_data[constants.PERSONA_ASSISTANT][-length:],
            key=lambda x: x[1], reverse=reverse))
        combined_transcript = combined_transcript[-length:]

        return combined_transcript
