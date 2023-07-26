from heapq import merge
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
