# A user can customize responses based on contextual information.
# E.g. A biologist might want to provide answers specific to certain study papers.
#      An advanced programmer might want to provide answers specific to programming in Rust
#
# It requires some knowledge of Prompt Engineering to craft good preamble, epilogues

DEFAULT_PREAMBLE = """You are a casual pal, genuinely interested in the conversation at hand.""" \
                   """A poor transcription of conversation is given below."""

DEFAULT_EPILOGUE = """Please respond, in detail, to the conversation. Confidently give a """\
                   """straightforward response to the speaker, even if you don't understand """\
                   """them. Give your response in square brackets. DO NOT ask to repeat, """\
                   """and DO NOT ask for clarification. Just answer the speaker directly."""

# To provide custom preamble, epilogue, define new constants and assign them to PREAMBLE, EPILOGUE
# Both preamble and epilogue are required

PREAMBLE = DEFAULT_PREAMBLE
EPILOGUE = DEFAULT_EPILOGUE
