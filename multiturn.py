import pprint
import openai

# Initial message object
# System input is instructions to chatGPT as to how should it behave
# User input is conversation by the user
# Assistant is responses we would expect chatGPT to provide us
messages = [
    {"role": "system", "content": "You are an expert at Fantasy Football and helping others learn about Fantasy football."},
    {"role": "user", "content": "I am V, I want to learn about Fantasy football"},
    {"role": "assistant", "content": "Hello, V. That's awesome! What do you want to know about Fantasy football?"},
    {"role": "user", "content": "What is Fantasy Football?"}
]

# model="gpt-3.5-turbo"
MODEL = "gpt-3.5-turbo-0301"


def update_chat(message_list, role, content):
    """Add a new message to the message array
       This should be expanded to include just the last x number of messages,
       I think 10 is good number
       Always keep the system message though, that is required for training the system
    """
    message_list.append({"role": role, "content": content})
    return messages


# Method to call chatGPT for a response
def get_chatgpt_response(message_list):
    """Call chatGPT for a response
    """
    response = openai.ChatCompletion.create(model=MODEL, messages=message_list)
    # return  response['choices'][0]['message']['content']
    return response

# Sample interaction with ChatGPT LLM
# [{'content': 'You are an expert at Fantasy Football and helping others learn about Fantasy football.',
#  'role': 'system'},
# {'content': 'I am V, I want to learn about Fantasy football', 'role': 'user'},
# {'content': "Hello, V. That's awesome! What do you want to know about Fantasy football?", 'role': 'assistant'},
# {'content': 'What is Fantasy Football?', 'role': 'user'},
# {'content': 'Fantasy football is a game where participants create virtual teams composed of professional football '
#             'players who earn points based on their real-life performances in a given week. Participants usually '
#             'draft these players at the beginning of the season, and during each week of the football season, '
#             "participants set their lineups and make changes based on their player's performances and other factors "
#             'like player injury, team schedule, and matchups. The aim is to accumulate as many points as possible and '
#             'have the highest-scoring team at the end of the season.',
#  'role': 'assistant'},
# {'content': 'What is a good strategy for fantasy football', 'role': 'user'},
# {'content': 'There are several strategies in fantasy football, and the one that works best for you may depend on your '
#             'level of experience, the league rules, and the league size. Here are some general strategies that can '
#             'help you succeed in fantasy football:\n'
#             '\n'
#             '1. Draft a solid team: The most important aspect of fantasy football is the draft. Allocate your draft '
#             'picks wisely; make sure you get a good mix of consistent performers and high-upside picks.\n'
#             '\n'
#             '2. Stay up-to-date: Keep up with the latest NFL news and injuries throughout the season. This will help '
#             'you stay ahead of your opponents and optimize your lineup decisions.\n'
#             '\n'
#             "3. Monitor weekly matchups: Be mindful of your players' matchups and how they could impact their "
#             "production. Check the opposing team's defense against your player position.\n"
#             '\n'
#             "4. Don't overreact to a poor performance: Every team will have a bad game, so don't be too quick to drop "
#             'a player after a weak performance. Try and give him the opportunity to improve before making a hasty '
#             'decision.\n'
#             '\n'
#             '5. Utilize the waiver wire: During the season, look to make pickups that may help improve your team. '
#             "Keep an eye on players who are performing well that aren't owned in your league.\n"
#             '\n'
#             '6. Watch out for bye weeks: Ensure that you have backup players for your starters during their bye '
#             "weeks. You don't want to encounter a situation where you don't have a player that can play in the "
#             'situation.',
#  'role': 'assistant'},
# {'content': 'What are the positions in fantasy football', 'role': 'user'},
# {'content': "The positions in fantasy football depend on the league's configuration. However, the most common setup "
#             'for fantasy football includes the following positions:\n'
#             '\n'
#             '1. Quarterback (QB) - The quarterback is usually the highest-scoring position and is responsible for '
#             'throwing the ball and leading team offenses.\n'
#             '\n'
#             '2. Running Back (RB) - Running backs are typically the workhorses of fantasy football teams. They carry '
#             'the ball and rack up points for scoring touchdowns and accumulating yards.\n'
#             '\n'
#             '3. Wide Receiver (WR) - Wide receivers are key fantasy players as they catch passes and score '
#             'touchdowns.\n'
#             '\n'
#             '4. Tight End (TE) - Tight ends are another pass-catching position that frequently scores touchdowns and '
#             'can accumulate good yardage for extra points.\n'
#             '\n'
#             '5. Kicker (K) - While not as essential as the other positions, kickers can get you points by scoring '
#             'field goals and extra points\n'
#             '\n'
#             '6. Defense/Special Teams (DST) - A single team defense/special teams position where you can score points '
#             "based on the team's performance such as sacks, interceptions, and touchdowns.\n"
#             '\n'
#             'Some leagues include other positions like Flex (RB/WR/TE), Superflex (QB/RB/WR/TE), or Individual '
#             'Defensive Players (IDP).',
#  'role': 'assistant'},
# {'content': 'who are the best wide receivers in fantasy football', 'role': 'user'},
# {'content': 'The best wide receivers in fantasy football generally change from year to year due to injuries, player '
#             'turnover, and other factors. However, here are a few players who are seen as the most consistent and '
#             'reliable fantasy performers:\n'
#             '\n'
#             '1. Davante Adams - Adams is widely regarded as the number one overall receiver in fantasy football. His '
#             'combination of talent, target volume, and Aaron Rodgers throwing to him makes him a lock as a top '
#             'fantasy option.\n'
#             '\n'
#             '2. Tyreek Hill - As one of the fastest players in the league, Hill is always a danger to break a big '
#             "play. He is Patrick Mahomes' go-to receiver on the Chiefs, and there are few better options in fantasy "
#             'football.\n'
#             '\n'
#             '3. DeAndre Hopkins - Hopkins has been consistently good throughout his career. However, his transition '
#             'to the Arizona Cardinals in 2020 has only made him a more prolific fantasy option.\n'
#             '\n'
#             '4. Stefon Diggs - Diggs might excel as a receiver, especially when paired with a strong QB like Josh '
#             "Allen. He had a breakout year in the 2020 season and solidified himself as one of the league's elite "
#             'receivers.\n'
#             '\n'
#             '5. Calvin Ridley - Without Julio Jones on the Falcons roster, Ridley progressed to the number one '
#             "receiver. He's already a valuable fantasy option and he's on the rise.\n"
#             '\n'
#             'Other notable receivers with the potential for high fantasy output include Michael Thomas, Julio Jones, '
#             'Keenan Allen, Allen Robinson, and A.J. Brown.',
#  'role': 'assistant'}]


if __name__ == "__main__":
    openai.api_key = "<OpenAI Key>"
    model_response = get_chatgpt_response(messages)
    messages = update_chat(messages, "assistant",
                           model_response['choices'][0]['message']['content'])
    pprint.pprint(messages, width=120)

    while True:
        user_input = input("Ask the next question: ")
        messages = update_chat(messages, "user", user_input)
        model_response = get_chatgpt_response(messages)
        messages = update_chat(messages, "assistant",
                               model_response['choices'][0]['message']['content'])
        print('---------------- Getting response from LLM ---------------- ')
        pprint.pprint(messages, width=120)
